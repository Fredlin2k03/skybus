namespace BusBooking.Api.Models;

public class User
{
    public int UserId { get; set; }
    public string FullName { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string PasswordSalt { get; set; } = string.Empty;
    public string? Phone { get; set; }
    public DateTime CreatedAtUtc { get; set; }
    public bool IsActive { get; set; } = true;
}

public class Bus
{
    public int BusId { get; set; }
    public string OperatorName { get; set; } = string.Empty;
    public string BusNumber { get; set; } = string.Empty;
    public string BusType { get; set; } = string.Empty;
    public int TotalSeats { get; set; }
    public string? Amenities { get; set; }
    public decimal RatingAvg { get; set; }

    public ICollection<Seat> Seats { get; set; } = new List<Seat>();
    public ICollection<Trip> Trips { get; set; } = new List<Trip>();
}

public class Seat
{
    public int SeatId { get; set; }
    public int BusId { get; set; }
    public string SeatNumber { get; set; } = string.Empty;
    public string Deck { get; set; } = "Lower";
    public string SeatType { get; set; } = string.Empty;
    public int RowPosition { get; set; }
    public int ColumnPosition { get; set; }
    public decimal PriceMultiplier { get; set; } = 1.00m;

    public Bus? Bus { get; set; }
}

public class Trip
{
    public int TripId { get; set; }
    public int BusId { get; set; }
    public string SourceCity { get; set; } = string.Empty;
    public string DestinationCity { get; set; } = string.Empty;
    public DateTime DepartureDateTime { get; set; }
    public DateTime ArrivalDateTime { get; set; }
    public decimal BaseFare { get; set; }
    public int AvailableSeats { get; set; }

    public Bus? Bus { get; set; }
    public ICollection<TripPoint> TripPoints { get; set; } = new List<TripPoint>();
}

public class TripPoint
{
    public int TripPointId { get; set; }
    public int TripId { get; set; }
    public string PointType { get; set; } = string.Empty; // Boarding | Dropping
    public string Name { get; set; } = string.Empty;
    public DateTime LandmarkTime { get; set; }
    public string? Address { get; set; }

    public Trip? Trip { get; set; }
}

public class Booking
{
    public int BookingId { get; set; }
    public int UserId { get; set; }
    public int TripId { get; set; }
    public int BoardingTripPointId { get; set; }
    public int DroppingTripPointId { get; set; }
    public string ContactPhone { get; set; } = string.Empty;
    public string ContactEmail { get; set; } = string.Empty;
    public decimal TotalFare { get; set; }
    public string BookingStatus { get; set; } = "PendingPayment";
    public string PaymentStatus { get; set; } = "Initiated";
    public string? UpiTransactionRef { get; set; }
    public DateTime BookingDateUtc { get; set; }
    public DateTime? PaymentExpiryUtc { get; set; }

    public Trip? Trip { get; set; }
    public ICollection<SeatBooking> SeatBookings { get; set; } = new List<SeatBooking>();
}

public class SeatBooking
{
    public int SeatBookingId { get; set; }
    public int BookingId { get; set; }
    public int SeatId { get; set; }
    public string PassengerName { get; set; } = string.Empty;
    public int Age { get; set; }
    public string Gender { get; set; } = string.Empty;
    public decimal SeatFare { get; set; }

    public Booking? Booking { get; set; }
    public Seat? Seat { get; set; }
}

public class Refund
{
    public int RefundId { get; set; }
    public int BookingId { get; set; }
    public decimal OriginalAmount { get; set; }
    public decimal HoursBeforeDeparture { get; set; }
    public decimal DeductionPercent { get; set; }
    public decimal RefundAmount { get; set; }
    public DateTime CancelledAtUtc { get; set; }
}

/// <summary>Shape returned by dbo.sp_CancelBookingAndRefund - used with FromSqlRaw.</summary>
public class RefundResult
{
    public int BookingId { get; set; }
    public decimal OriginalAmount { get; set; }
    public decimal HoursBeforeDeparture { get; set; }
    public decimal DeductionPercent { get; set; }
    public decimal RefundPercent { get; set; }
    public decimal RefundAmount { get; set; }
}
