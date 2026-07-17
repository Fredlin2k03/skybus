namespace BusBooking.Api.DTOs;

// ---------- Auth ----------
public record RegisterRequest(string FullName, string Email, string Password, string? Phone);
public record LoginRequest(string Email, string Password);
public record AuthResponse(int UserId, string FullName, string Email, string Token);

// ---------- Bus search ----------
public record TripSearchResult(
    int TripId, int BusId, string OperatorName, string BusType,
    DateTime DepartureDateTime, DateTime ArrivalDateTime,
    decimal BaseFare, int AvailableSeats, decimal RatingAvg);

public record SeatDto(
    int SeatId, string SeatNumber, string Deck, string SeatType,
    int RowPosition, int ColumnPosition, decimal Price, bool IsBooked);

public record TripPointDto(int TripPointId, string PointType, string Name, DateTime LandmarkTime, string? Address);

// ---------- Booking initiation ----------
public record PassengerDto(int SeatId, string PassengerName, int Age, string Gender);

public record InitiateBookingRequest(
    int UserId,
    int TripId,
    int BoardingTripPointId,
    int DroppingTripPointId,
    string ContactPhone,
    string ContactEmail,
    List<PassengerDto> Passengers);

public record InitiateBookingResponse(
    int BookingId,
    decimal TotalAmount,
    string UpiUri,
    int PaymentWindowSeconds,
    DateTime PaymentExpiryUtc);

public record ConfirmPaymentRequest(string UpiTransactionRef);

public record BookingDetailsResponse(
    int BookingId, string BookingStatus, string PaymentStatus,
    decimal TotalFare, DateTime BookingDateUtc, DateTime? PaymentExpiryUtc,
    string SourceCity, string DestinationCity, DateTime DepartureDateTime,
    List<string> SeatNumbers);

// ---------- Cancellation ----------
public record CancellationResponse(
    int BookingId, decimal OriginalAmount, decimal HoursBeforeDeparture,
    decimal DeductionPercent, decimal RefundPercent, decimal RefundAmount);
