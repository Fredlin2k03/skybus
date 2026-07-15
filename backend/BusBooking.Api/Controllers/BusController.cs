using BusBooking.Api.Data;
using BusBooking.Api.DTOs;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace BusBooking.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class BusController : ControllerBase
{
    private readonly ApplicationDbContext _db;
    public BusController(ApplicationDbContext db) => _db = db;

    // GET /api/bus/search?source=Bengaluru&destination=Chennai&date=2026-07-20
    [HttpGet("search")]
    public async Task<ActionResult<List<TripSearchResult>>> Search(
        [FromQuery] string source, [FromQuery] string destination, [FromQuery] DateTime date)
    {
        var results = await _db.Trips
            .Include(t => t.Bus)
            .Where(t => t.SourceCity == source
                     && t.DestinationCity == destination
                     && t.DepartureDateTime.Date == date.Date
                     && t.AvailableSeats > 0)
            .OrderBy(t => t.DepartureDateTime)
            .Select(t => new TripSearchResult(
                t.TripId, t.BusId, t.Bus!.OperatorName, t.Bus.BusType,
                t.DepartureDateTime, t.ArrivalDateTime,
                t.BaseFare, t.AvailableSeats, t.Bus.RatingAvg))
            .ToListAsync();

        return Ok(results);
    }

    // GET /api/bus/trip/5/seats  -> full seat map with live price + booked status
    [HttpGet("trip/{tripId}/seats")]
    public async Task<ActionResult<List<SeatDto>>> GetSeatLayout(int tripId)
    {
        var trip = await _db.Trips.FirstOrDefaultAsync(t => t.TripId == tripId);
        if (trip is null) return NotFound(new { message = "Trip not found." });

        var bookedSeatIds = await _db.SeatBookings
            .Where(sb => sb.Booking!.TripId == tripId
                      && sb.Booking.BookingStatus != "Cancelled"
                      && sb.Booking.BookingStatus != "Expired")
            .Select(sb => sb.SeatId)
            .ToListAsync();

        var seats = await _db.Seats
            .Where(s => s.BusId == trip.BusId)
            .OrderBy(s => s.Deck).ThenBy(s => s.RowPosition).ThenBy(s => s.ColumnPosition)
            .Select(s => new SeatDto(
                s.SeatId, s.SeatNumber, s.Deck, s.SeatType,
                s.RowPosition, s.ColumnPosition,
                Math.Round(trip.BaseFare * s.PriceMultiplier, 2),
                bookedSeatIds.Contains(s.SeatId)))
            .ToListAsync();

        return Ok(seats);
    }

    // GET /api/bus/trip/5/points -> boarding & dropping points
    [HttpGet("trip/{tripId}/points")]
    public async Task<ActionResult<List<TripPointDto>>> GetTripPoints(int tripId)
    {
        var points = await _db.TripPoints
            .Where(p => p.TripId == tripId)
            .OrderBy(p => p.LandmarkTime)
            .Select(p => new TripPointDto(p.TripPointId, p.PointType, p.Name, p.LandmarkTime, p.Address))
            .ToListAsync();

        return Ok(points);
    }
}
