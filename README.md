# Bus Booking Application — Phase 1 Scaffold

A redBus-style bus booking application: React frontend, .NET 9 Web API,
Azure SQL Database. This scaffold is Phase 1 (local dev talking directly to
Azure SQL) — see `docs/SETUP_GUIDE.md` for the Phase 2 evolution path.

## Structure

```
database/
  01_schema.sql                     Users, Buses, Seats, Trips, TripPoints, Bookings, SeatBookings, Refunds
  02_refund_function_and_procs.sql  fn_CalculateRefundPercent + sp_CancelBookingAndRefund
  03_seed_data.sql                  Sample bus/trip for local testing

backend/BusBooking.Api/
  Models/Entities.cs                EF Core entity classes
  Data/ApplicationDbContext.cs      DbContext + fluent mappings
  DTOs/BookingDtos.cs               Request/response contracts
  Services/UpiService.cs            Mock UPI deep-link generator
  Services/AuthService.cs           Password hashing + JWT issuing
  Controllers/AuthController.cs     Register / login
  Controllers/BusController.cs      Search, seat layout, trip points
  Controllers/BookingController.cs  Initiate booking (UPI payload), confirm payment, cancel + refund
  Program.cs                        App bootstrap (EF Core, CORS, JWT, Swagger)
  appsettings.json                  Connection string / JWT / UPI config (placeholders)

frontend/
  src/api/api.js                    Axios client (Auth/Bus/Booking endpoints)
  src/components/BookingWizard.jsx  Checkout state machine (Seats → Points → Passengers → Summary → UPI)
  src/components/SeatMap.jsx
  src/components/BoardingDropSelector.jsx
  src/components/PassengerForm.jsx
  src/components/FareSummary.jsx
  src/components/UpiPayment.jsx     QR code + 180s countdown
  src/components/BookingWizard.css  Ticket-stub visual theme

docs/SETUP_GUIDE.md                 Azure SQL firewall + local run instructions
```

## How the refund engine works

The tiered refund logic lives in exactly one place — the database — via
`dbo.fn_CalculateRefundPercent` (a scalar function) and is applied
transactionally by `dbo.sp_CancelBookingAndRefund`, which:
1. Looks up the trip's `DepartureDateTime`.
2. Computes hours remaining until departure.
3. Applies the tier (≥48h → 90% refund, 24–48h → 80%, 12–24h → 70%, <12h → 0%).
4. Writes an audit row to `dbo.Refunds`.
5. Releases the seats back to `Trips.AvailableSeats`.

`BookingController.CancelBooking` calls this via `FromSqlRaw`/`SqlQuery`
rather than reimplementing the tiers in C#, so the business rule can't drift
between the app layer and the database layer.

## How the UPI mock works

`UpiService.BuildUpiUri` builds a standards-shaped `upi://pay?pa=...&am=...`
string. `BookingController.InitiateBooking` returns this string plus a
`paymentWindowSeconds` (180s) and the React `UpiPayment` component renders it
as a QR code (`qrcode.react`) with a live countdown. This is illustrative only
— swap in a real PSP (Razorpay/Cashfree/PayU UPI Intent APIs) before going to
production.

## Getting started

See `docs/SETUP_GUIDE.md` for the full walkthrough (Azure SQL firewall rules,
connection strings, running both apps locally).
# skybus
