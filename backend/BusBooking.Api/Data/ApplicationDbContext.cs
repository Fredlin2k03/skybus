using BusBooking.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace BusBooking.Api.Data;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Bus> Buses => Set<Bus>();
    public DbSet<Seat> Seats => Set<Seat>();
    public DbSet<Trip> Trips => Set<Trip>();
    public DbSet<TripPoint> TripPoints => Set<TripPoint>();
    public DbSet<Booking> Bookings => Set<Booking>();
    public DbSet<SeatBooking> SeatBookings => Set<SeatBooking>();
    public DbSet<Refund> Refunds => Set<Refund>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(e =>
        {
            e.ToTable("Users");
            e.HasKey(x => x.UserId);
            e.HasIndex(x => x.Email).IsUnique();
            e.Property(x => x.CreatedAtUtc).HasColumnName("CreatedAtUtc");
        });

        modelBuilder.Entity<Bus>(e =>
        {
            e.ToTable("Buses");
            e.HasKey(x => x.BusId);
            e.Property(x => x.RatingAvg).HasColumnType("decimal(2,1)");
        });

        modelBuilder.Entity<Seat>(e =>
        {
            e.ToTable("Seats");
            e.HasKey(x => x.SeatId);
            e.Property(x => x.PriceMultiplier).HasColumnType("decimal(4,2)");
            e.HasIndex(x => new { x.BusId, x.SeatNumber }).IsUnique();
            e.HasOne(x => x.Bus).WithMany(b => b.Seats).HasForeignKey(x => x.BusId);
        });

        modelBuilder.Entity<Trip>(e =>
        {
            e.ToTable("Trips");
            e.HasKey(x => x.TripId);
            e.Property(x => x.BaseFare).HasColumnType("decimal(10,2)");
            e.HasIndex(x => new { x.SourceCity, x.DestinationCity, x.DepartureDateTime });
            e.HasOne(x => x.Bus).WithMany(b => b.Trips).HasForeignKey(x => x.BusId);
        });

        modelBuilder.Entity<TripPoint>(e =>
        {
            e.ToTable("TripPoints");
            e.HasKey(x => x.TripPointId);
            e.HasOne(x => x.Trip).WithMany(t => t.TripPoints).HasForeignKey(x => x.TripId);
        });

        modelBuilder.Entity<Booking>(e =>
        {
            e.ToTable("Bookings");
            e.HasKey(x => x.BookingId);
            e.Property(x => x.TotalFare).HasColumnType("decimal(10,2)");
            e.HasOne(x => x.Trip).WithMany().HasForeignKey(x => x.TripId);
        });

        modelBuilder.Entity<SeatBooking>(e =>
        {
            e.ToTable("SeatBookings");
            e.HasKey(x => x.SeatBookingId);
            e.Property(x => x.SeatFare).HasColumnType("decimal(10,2)");
            e.HasIndex(x => new { x.BookingId, x.SeatId }).IsUnique();
            e.HasOne(x => x.Booking).WithMany(b => b.SeatBookings).HasForeignKey(x => x.BookingId);
            e.HasOne(x => x.Seat).WithMany().HasForeignKey(x => x.SeatId);
        });

        modelBuilder.Entity<Refund>(e =>
        {
            e.ToTable("Refunds");
            e.HasKey(x => x.RefundId);
            e.Property(x => x.OriginalAmount).HasColumnType("decimal(10,2)");
            e.Property(x => x.HoursBeforeDeparture).HasColumnType("decimal(10,2)");
            e.Property(x => x.DeductionPercent).HasColumnType("decimal(5,2)");
            e.Property(x => x.RefundAmount).HasColumnType("decimal(10,2)");
        });

        // Keyless type used only for FromSqlRaw projection of the stored procedure result
        modelBuilder.Entity<RefundResult>(e =>
        {
            e.HasNoKey();
            e.ToView(null);
        });
    }
}
