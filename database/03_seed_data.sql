/* Sample seed data for local development / demo purposes */

INSERT INTO dbo.Buses (OperatorName, BusNumber, BusType, TotalSeats, Amenities, RatingAvg)
VALUES (N'Sri Lakshmi Travels', N'KA-01-AB-1234', N'AC Sleeper', 30, N'WiFi,Charging Point,Blanket,Water Bottle', 4.3);

DECLARE @BusId INT = SCOPE_IDENTITY();

-- Lower deck: 9 rows x 2 sleeper berths (18 seats), Upper deck: 12 sleeper berths
DECLARE @r INT = 1;
WHILE @r <= 9
BEGIN
    INSERT INTO dbo.Seats (BusId, SeatNumber, Deck, SeatType, RowPosition, ColumnPosition, PriceMultiplier)
    VALUES (@BusId, CONCAT('L', @r, 'A'), 'Lower', 'Sleeper', @r, 1, 1.00);
    INSERT INTO dbo.Seats (BusId, SeatNumber, Deck, SeatType, RowPosition, ColumnPosition, PriceMultiplier)
    VALUES (@BusId, CONCAT('L', @r, 'B'), 'Lower', 'Sleeper', @r, 2, 1.00);
    SET @r += 1;
END

SET @r = 1;
WHILE @r <= 12
BEGIN
    INSERT INTO dbo.Seats (BusId, SeatNumber, Deck, SeatType, RowPosition, ColumnPosition, PriceMultiplier)
    VALUES (@BusId, CONCAT('U', @r), 'Upper', 'Sleeper', @r, 1, 0.90);
    SET @r += 1;
END

INSERT INTO dbo.Trips (BusId, SourceCity, DestinationCity, DepartureDateTime, ArrivalDateTime, BaseFare, AvailableSeats)
VALUES (@BusId, N'Bengaluru', N'Chennai', DATEADD(DAY, 2, SYSUTCDATETIME()), DATEADD(HOUR, 7, DATEADD(DAY, 2, SYSUTCDATETIME())), 900.00, 30);

DECLARE @TripId INT = SCOPE_IDENTITY();

INSERT INTO dbo.TripPoints (TripId, PointType, Name, LandmarkTime, Address)
VALUES
    (@TripId, 'Boarding', N'Madiwala Bus Stand', DATEADD(DAY, 2, SYSUTCDATETIME()), N'Madiwala, Bengaluru'),
    (@TripId, 'Boarding', N'Silk Board Junction', DATEADD(MINUTE, 20, DATEADD(DAY, 2, SYSUTCDATETIME())), N'Silk Board, Bengaluru'),
    (@TripId, 'Dropping', N'Koyambedu Bus Terminus', DATEADD(HOUR, 7, DATEADD(DAY, 2, SYSUTCDATETIME())), N'Koyambedu, Chennai'),
    (@TripId, 'Dropping', N'Tambaram', DATEADD(MINUTE, 30, DATEADD(HOUR, 7, DATEADD(DAY, 2, SYSUTCDATETIME()))), N'Tambaram, Chennai');
GO
