using BusBooking.Api.Data;
using BusBooking.Api.DTOs;
using BusBooking.Api.Models;
using BusBooking.Api.Services;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

namespace BusBooking.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class BookingController : ControllerBase
{
    private readonly ApplicationDbContext _db;
    private readonly IUpiService _upiService;
    private readonly IConfiguration _config;

    public BookingController(ApplicationDbContext db, IUpiService upiService, IConfiguration config)
    {
        _db = db;
        _upiService = upiService;
        _config = config;
    }

    // -----------------------------------------------------------------
    // POST /api/booking/initiate
    // Creates a PendingPayment booking + seat line items, locks the
    // seats for the payment window, and returns the UPI QR payload.
    // -----------------------------------------------------------------
    [HttpPost("initiate")]
    public async Task<ActionResult<InitiateBookingResponse>> InitiateBooking(InitiateBookingRequest request)
    {
        if (request.Passengers is null || request.Passengers.Count == 0)
            return BadRequest(new { message = "At least one passenger/seat is required." });

        var trip = await _db.Trips.Include(t => t.Bus).FirstOrDefaultAsync(t => t.TripId == request.TripId);
        if (trip is null) return NotFound(new { message = "Trip not found." });

        var seatIds = request.Passengers.Select(p => p.SeatId).ToList();

        // Guard against double-booking: check for any active booking on these seats for this trip
        var alreadyBooked = await _db.SeatBookings
            .Where(sb => seatIds.Contains(sb.SeatId)
                      && sb.Booking!.TripId == request.TripId
                      && sb.Booking.BookingStatus != "Cancelled"
                      && sb.Booking.BookingStatus != "Expired")
            .AnyAsync();

        if (alreadyBooked)
            return Conflict(new { message = "One or more selected seats were just booked by someone else. Please reselect." });

        var seats = await _db.Seats.Where(s => seatIds.Contains(s.SeatId)).ToListAsync();
        if (seats.Count != seatIds.Count)
            return BadRequest(new { message = "Invalid seat selection." });

        var seatPriceLookup = seats.ToDictionary(s => s.SeatId, s => Math.Round(trip.BaseFare * s.PriceMultiplier, 2));
        var totalFare = seatPriceLookup.Values.Sum();

        var paymentWindowSeconds = _config.GetValue<int>("UpiSettings:PaymentWindowSeconds", 180);
        var now = DateTime.UtcNow;
        var expiry = now.AddSeconds(paymentWindowSeconds);

        var booking = new Booking
        {
            UserId = request.UserId,
            TripId = request.TripId,
            BoardingTripPointId = request.BoardingTripPointId,
            DroppingTripPointId = request.DroppingTripPointId,
            ContactPhone = request.ContactPhone,
            ContactEmail = request.ContactEmail,
            TotalFare = totalFare,
            BookingStatus = "PendingPayment",
            PaymentStatus = "Initiated",
            BookingDateUtc = now,
            PaymentExpiryUtc = expiry
        };

        foreach (var passenger in request.Passengers)
        {
            booking.SeatBookings.Add(new SeatBooking
            {
                SeatId = passenger.SeatId,
                PassengerName = passenger.PassengerName,
                Age = passenger.Age,
                Gender = passenger.Gender,
                SeatFare = seatPriceLookup[passenger.SeatId]
            });
        }

        _db.Bookings.Add(booking);
        await _db.SaveChangesAsync();

        var transactionRef = $"BUS{booking.BookingId:D6}{DateTime.UtcNow:HHmmss}";
        var upiUri = _upiService.BuildUpiUri(
            payeeVpa: _config["UpiSettings:PayeeVpa"]!,
            payeeName: _config["UpiSettings:PayeeName"]!,
            amount: totalFare,
            transactionNote: $"Bus booking #{booking.BookingId} {trip.SourceCity}-{trip.DestinationCity}",
            transactionRef: transactionRef);

        return Ok(new InitiateBookingResponse(
            booking.BookingId, totalFare, upiUri, paymentWindowSeconds, expiry));
    }

    // -----------------------------------------------------------------
    // POST /api/booking/{id}/confirm-payment
    // Mock confirmation: in production this is a webhook from the PSP.
    // -----------------------------------------------------------------
    [HttpPost("{id}/confirm-payment")]
    public async Task<IActionResult> ConfirmPayment(int id, ConfirmPaymentRequest request)
    {
        var booking = await _db.Bookings.FindAsync(id);
        if (booking is null) return NotFound(new { message = "Booking not found." });

        if (booking.BookingStatus != "PendingPayment")
            return BadRequest(new { message = $"Booking is in '{booking.BookingStatus}' state and cannot be confirmed." });

        if (booking.PaymentExpiryUtc.HasValue && DateTime.UtcNow > booking.PaymentExpiryUtc.Value)
        {
            booking.BookingStatus = "Expired";
            booking.PaymentStatus = "Failed";
            await _db.SaveChangesAsync();
            return BadRequest(new { message = "Payment window has expired. Please start a new booking." });
        }

        booking.BookingStatus = "Confirmed";
        booking.PaymentStatus = "Paid";
        booking.UpiTransactionRef = request.UpiTransactionRef;

        // Decrement seat availability on the trip only on confirmed payment
        var trip = await _db.Trips.FindAsync(booking.TripId);
        if (trip is not null)
        {
            var seatCount = await _db.SeatBookings.CountAsync(sb => sb.BookingId == booking.BookingId);
            trip.AvailableSeats = Math.Max(0, trip.AvailableSeats - seatCount);
        }

        await _db.SaveChangesAsync();
        return Ok(new { message = "Payment confirmed.", bookingId = booking.BookingId, status = booking.BookingStatus });
    }

    // -----------------------------------------------------------------
    // GET /api/booking/{id}
    // -----------------------------------------------------------------
    [HttpGet("{id}")]
    public async Task<ActionResult<BookingDetailsResponse>> GetBooking(int id)
    {
        var booking = await _db.Bookings
            .Include(b => b.Trip)
            .Include(b => b.SeatBookings).ThenInclude(sb => sb.Seat)
            .FirstOrDefaultAsync(b => b.BookingId == id);

        if (booking is null) return NotFound(new { message = "Booking not found." });

        return Ok(new BookingDetailsResponse(
            booking.BookingId, booking.BookingStatus, booking.PaymentStatus,
            booking.TotalFare, booking.BookingDateUtc, booking.PaymentExpiryUtc,
            booking.Trip!.SourceCity, booking.Trip.DestinationCity, booking.Trip.DepartureDateTime,
            booking.SeatBookings.Select(sb => sb.Seat!.SeatNumber).ToList()));
    }

    // -----------------------------------------------------------------
    // POST /api/booking/{id}/cancel
    // Delegates the refund calculation to dbo.sp_CancelBookingAndRefund
    // so the deduction tiers live in exactly one place: the database.
    // -----------------------------------------------------------------
    [HttpPost("{id}/cancel")]
    public async Task<ActionResult<CancellationResponse>> CancelBooking(int id)
    {
        var bookingExists = await _db.Bookings.AnyAsync(b => b.BookingId == id);
        if (!bookingExists) return NotFound(new { message = "Booking not found." });

        try
        {
            var result = await _db.Database
                .SqlQuery<RefundResult>($"EXEC dbo.sp_CancelBookingAndRefund @BookingId = {id}")
                .ToListAsync();

            var refund = result.FirstOrDefault();
            if (refund is null)
                return BadRequest(new { message = "Cancellation could not be processed." });

            return Ok(new CancellationResponse(
                refund.BookingId, refund.OriginalAmount, refund.HoursBeforeDeparture,
                refund.DeductionPercent, refund.RefundPercent, refund.RefundAmount));
        }
        catch (SqlException ex) when (ex.Number == 50002)
        {
            return BadRequest(new { message = "Only confirmed bookings can be cancelled." });
        }
        catch (SqlException)
        {
            return StatusCode(500, new { message = "An error occurred while processing the cancellation." });
        }
    }
}
