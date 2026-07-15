/* ============================================================
   Refund calculation function + cancellation stored procedure
   ============================================================ */

-- ---------------------------------------------------------
-- fn_CalculateRefundPercent
-- Returns the REFUND percentage (not deduction) a customer
-- receives based on how many hours remain before departure.
--
--   >= 48 hrs   -> 90% refund (10% deduction)
--   24-48 hrs   -> 80% refund (20% deduction)
--   12-24 hrs   -> 70% refund (30% deduction)
--   < 12 hrs    -> 0%  refund (100% deduction)
-- ---------------------------------------------------------
CREATE OR ALTER FUNCTION dbo.fn_CalculateRefundPercent
(
    @DepartureDateTime   DATETIME2,
    @CancellationDateTime DATETIME2
)
RETURNS DECIMAL(5,2)
AS
BEGIN
    DECLARE @HoursRemaining DECIMAL(10,2);
    DECLARE @RefundPercent DECIMAL(5,2);

    SET @HoursRemaining = DATEDIFF(MINUTE, @CancellationDateTime, @DepartureDateTime) / 60.0;

    IF @HoursRemaining < 0
        SET @RefundPercent = 0.00;               -- bus already departed
    ELSE IF @HoursRemaining >= 48
        SET @RefundPercent = 90.00;
    ELSE IF @HoursRemaining >= 24
        SET @RefundPercent = 80.00;
    ELSE IF @HoursRemaining >= 12
        SET @RefundPercent = 70.00;
    ELSE
        SET @RefundPercent = 0.00;

    RETURN @RefundPercent;
END
GO

-- ---------------------------------------------------------
-- sp_CancelBookingAndRefund
-- Cancels a booking, computes the refund via the scalar
-- function above, writes an audit row to dbo.Refunds,
-- releases the seats back to Trips.AvailableSeats, and
-- returns the refund breakdown to the caller.
-- ---------------------------------------------------------
CREATE OR ALTER PROCEDURE dbo.sp_CancelBookingAndRefund
    @BookingId INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @TripId INT,
                @DepartureDateTime DATETIME2,
                @TotalFare DECIMAL(10,2),
                @CurrentStatus NVARCHAR(20),
                @SeatCount INT,
                @NowUtc DATETIME2 = SYSUTCDATETIME();

        SELECT
            @TripId = b.TripId,
            @DepartureDateTime = t.DepartureDateTime,
            @TotalFare = b.TotalFare,
            @CurrentStatus = b.BookingStatus
        FROM dbo.Bookings b
        INNER JOIN dbo.Trips t ON t.TripId = b.TripId
        WHERE b.BookingId = @BookingId;

        IF @TripId IS NULL
        BEGIN
            THROW 50001, 'Booking not found.', 1;
        END

        IF @CurrentStatus <> 'Confirmed'
        BEGIN
            THROW 50002, 'Only confirmed bookings can be cancelled.', 1;
        END

        DECLARE @HoursRemaining DECIMAL(10,2) =
            DATEDIFF(MINUTE, @NowUtc, @DepartureDateTime) / 60.0;

        DECLARE @RefundPercent DECIMAL(5,2) =
            dbo.fn_CalculateRefundPercent(@DepartureDateTime, @NowUtc);

        DECLARE @RefundAmount DECIMAL(10,2) =
            ROUND(@TotalFare * @RefundPercent / 100.0, 2);

        SELECT @SeatCount = COUNT(*) FROM dbo.SeatBookings WHERE BookingId = @BookingId;

        UPDATE dbo.Bookings
        SET BookingStatus = 'Cancelled',
            PaymentStatus = CASE WHEN @RefundAmount > 0 THEN 'Refunded' ELSE 'Forfeited' END
        WHERE BookingId = @BookingId;

        UPDATE dbo.Trips
        SET AvailableSeats = AvailableSeats + @SeatCount
        WHERE TripId = @TripId;

        INSERT INTO dbo.Refunds
            (BookingId, OriginalAmount, HoursBeforeDeparture, DeductionPercent, RefundAmount)
        VALUES
            (@BookingId, @TotalFare, @HoursRemaining, (100.00 - @RefundPercent), @RefundAmount);

        COMMIT TRANSACTION;

        -- Result set consumed by the API layer
        SELECT
            @BookingId               AS BookingId,
            @TotalFare                AS OriginalAmount,
            @HoursRemaining           AS HoursBeforeDeparture,
            (100.00 - @RefundPercent) AS DeductionPercent,
            @RefundPercent            AS RefundPercent,
            @RefundAmount             AS RefundAmount;

    END TRY
    BEGIN CATCH
        IF XACT_STATE() <> 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH
END
GO
