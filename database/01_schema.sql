/* ============================================================
   Bus Booking Application - Azure SQL Database Schema
   Phase 1: Core transactional tables
   ============================================================ */

-- ---------------------------------------------------------
-- 1. Users
-- ---------------------------------------------------------
CREATE TABLE dbo.Users (
    UserId          INT IDENTITY(1,1) PRIMARY KEY,
    FullName        NVARCHAR(150)   NOT NULL,
    Email           NVARCHAR(256)   NOT NULL UNIQUE,
    PasswordHash    NVARCHAR(500)   NOT NULL,   -- PBKDF2 hash, never plaintext
    PasswordSalt    NVARCHAR(500)   NOT NULL,
    Phone           NVARCHAR(15)    NULL,
    CreatedAtUtc    DATETIME2       NOT NULL CONSTRAINT DF_Users_CreatedAt DEFAULT SYSUTCDATETIME(),
    IsActive        BIT             NOT NULL CONSTRAINT DF_Users_IsActive DEFAULT (1)
);
GO

-- ---------------------------------------------------------
-- 2. Buses (physical vehicle + seat template metadata)
-- ---------------------------------------------------------
CREATE TABLE dbo.Buses (
    BusId           INT IDENTITY(1,1) PRIMARY KEY,
    OperatorName    NVARCHAR(150)   NOT NULL,
    BusNumber       NVARCHAR(30)    NOT NULL,
    BusType         NVARCHAR(50)    NOT NULL,   -- e.g. 'AC Sleeper', 'Non-AC Seater'
    TotalSeats      INT             NOT NULL,
    Amenities       NVARCHAR(500)   NULL,       -- csv: 'WiFi,Charging Point,Blanket'
    RatingAvg       DECIMAL(2,1)    NOT NULL CONSTRAINT DF_Buses_Rating DEFAULT (4.0)
);
GO

-- ---------------------------------------------------------
-- 3. Seats  (static seat layout template per bus)
-- ---------------------------------------------------------
CREATE TABLE dbo.Seats (
    SeatId          INT IDENTITY(1,1) PRIMARY KEY,
    BusId           INT             NOT NULL REFERENCES dbo.Buses(BusId),
    SeatNumber      NVARCHAR(10)    NOT NULL,   -- e.g. 'L1', 'U12'
    Deck            NVARCHAR(10)    NOT NULL CONSTRAINT DF_Seats_Deck DEFAULT ('Lower'), -- Lower/Upper
    SeatType        NVARCHAR(20)    NOT NULL,   -- Sleeper / Seater
    RowPosition     INT             NOT NULL,   -- for grid rendering
    ColumnPosition  INT             NOT NULL,
    PriceMultiplier DECIMAL(4,2)    NOT NULL CONSTRAINT DF_Seats_Mult DEFAULT (1.00),
    CONSTRAINT UQ_Seats_BusSeatNumber UNIQUE (BusId, SeatNumber)
);
GO

-- ---------------------------------------------------------
-- 4. Trips (a scheduled run of a Bus between two cities)
-- ---------------------------------------------------------
CREATE TABLE dbo.Trips (
    TripId              INT IDENTITY(1,1) PRIMARY KEY,
    BusId               INT             NOT NULL REFERENCES dbo.Buses(BusId),
    SourceCity          NVARCHAR(100)   NOT NULL,
    DestinationCity     NVARCHAR(100)   NOT NULL,
    DepartureDateTime   DATETIME2       NOT NULL,
    ArrivalDateTime     DATETIME2       NOT NULL,
    BaseFare            DECIMAL(10,2)   NOT NULL,
    AvailableSeats      INT             NOT NULL
);
GO
CREATE INDEX IX_Trips_Search ON dbo.Trips (SourceCity, DestinationCity, DepartureDateTime);
GO

-- ---------------------------------------------------------
-- 5. Boarding / Dropping points (per trip)
-- ---------------------------------------------------------
CREATE TABLE dbo.TripPoints (
    TripPointId     INT IDENTITY(1,1) PRIMARY KEY,
    TripId          INT             NOT NULL REFERENCES dbo.Trips(TripId),
    PointType       NVARCHAR(10)    NOT NULL,   -- 'Boarding' or 'Dropping'
    Name            NVARCHAR(200)   NOT NULL,
    LandmarkTime    DATETIME2       NOT NULL,   -- actual arrival/departure time at that point
    Address         NVARCHAR(300)   NULL
);
GO

-- ---------------------------------------------------------
-- 6. Bookings (one checkout transaction)
-- ---------------------------------------------------------
CREATE TABLE dbo.Bookings (
    BookingId               INT IDENTITY(1,1) PRIMARY KEY,
    UserId                  INT             NOT NULL REFERENCES dbo.Users(UserId),
    TripId                  INT             NOT NULL REFERENCES dbo.Trips(TripId),
    BoardingTripPointId     INT             NOT NULL REFERENCES dbo.TripPoints(TripPointId),
    DroppingTripPointId     INT             NOT NULL REFERENCES dbo.TripPoints(TripPointId),
    ContactPhone            NVARCHAR(15)    NOT NULL,
    ContactEmail            NVARCHAR(256)   NOT NULL,
    TotalFare               DECIMAL(10,2)   NOT NULL,
    BookingStatus           NVARCHAR(20)    NOT NULL CONSTRAINT DF_Bookings_Status DEFAULT ('PendingPayment'),
        -- PendingPayment | Confirmed | Cancelled | Expired
    PaymentStatus           NVARCHAR(20)    NOT NULL CONSTRAINT DF_Bookings_PayStatus DEFAULT ('Initiated'),
        -- Initiated | Paid | Failed | Refunded
    UpiTransactionRef       NVARCHAR(100)   NULL,
    BookingDateUtc          DATETIME2       NOT NULL CONSTRAINT DF_Bookings_Date DEFAULT SYSUTCDATETIME(),
    PaymentExpiryUtc        DATETIME2       NULL   -- BookingDateUtc + 180s
);
GO

-- ---------------------------------------------------------
-- 7. SeatBookings (line items - one row per passenger/seat)
-- ---------------------------------------------------------
CREATE TABLE dbo.SeatBookings (
    SeatBookingId   INT IDENTITY(1,1) PRIMARY KEY,
    BookingId       INT             NOT NULL REFERENCES dbo.Bookings(BookingId),
    SeatId          INT             NOT NULL REFERENCES dbo.Seats(SeatId),
    PassengerName   NVARCHAR(150)   NOT NULL,
    Age             INT             NOT NULL,
    Gender          NVARCHAR(10)    NOT NULL,
    SeatFare        DECIMAL(10,2)   NOT NULL,
    CONSTRAINT UQ_SeatBookings_Booking_Seat UNIQUE (BookingId, SeatId)
);
GO

-- Prevent double-booking the same seat on the same trip for any
-- booking that is not cancelled/expired. Enforced in the stored
-- procedure/service layer via a serializable check because SQL
-- Server cannot filter a UNIQUE constraint across joined tables.
CREATE INDEX IX_SeatBookings_Seat ON dbo.SeatBookings (SeatId, BookingId);
GO

-- ---------------------------------------------------------
-- 8. Refunds (audit trail written by sp_CancelBookingAndRefund)
-- ---------------------------------------------------------
CREATE TABLE dbo.Refunds (
    RefundId            INT IDENTITY(1,1) PRIMARY KEY,
    BookingId            INT             NOT NULL REFERENCES dbo.Bookings(BookingId),
    OriginalAmount       DECIMAL(10,2)   NOT NULL,
    HoursBeforeDeparture DECIMAL(10,2)   NOT NULL,
    DeductionPercent     DECIMAL(5,2)    NOT NULL,
    RefundAmount         DECIMAL(10,2)   NOT NULL,
    CancelledAtUtc       DATETIME2       NOT NULL CONSTRAINT DF_Refunds_CancelledAt DEFAULT SYSUTCDATETIME()
);
GO
