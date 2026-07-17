"""
Seat models - Seat layouts and availability tracking.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SeatType(str, enum.Enum):
    """Types of seats available."""
    SEATER = "seater"
    SLEEPER = "sleeper"
    SEMI_SLEEPER = "semi_sleeper"


class DeckType(str, enum.Enum):
    """Deck types for buses with multiple decks."""
    LOWER = "lower"
    UPPER = "upper"


class SeatLayout(Base):
    """
    Defines the physical seat layout of a bus.
    Each row represents one seat in the bus layout grid.
    """

    __tablename__ = "seat_layouts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    
    # Seat identification
    seat_number = Column(String(10), nullable=False)  # e.g., "1A", "1B", "L1", "U1"
    row_number = Column(Integer, nullable=False)
    column_number = Column(Integer, nullable=False)
    
    # Seat properties
    seat_type = Column(SQLEnum(SeatType), nullable=False)
    deck = Column(SQLEnum(DeckType), default=DeckType.LOWER)
    is_window = Column(Boolean, default=False)
    is_aisle = Column(Boolean, default=False)
    is_ladies_only = Column(Boolean, default=False)
    
    # Pricing multiplier (1.0 = base fare, 1.2 = 20% premium for window/sleeper)
    price_multiplier = Column(Float, default=1.0)
    
    # Whether this seat exists (for irregular layouts, e.g., last row with fewer seats)
    is_available = Column(Boolean, default=True)
    
    # Relationships
    bus = relationship("Bus", back_populates="seat_layouts")

    def __repr__(self):
        return f"<SeatLayout(bus={self.bus_id}, seat={self.seat_number}, type={self.seat_type})>"


class SeatAvailability(Base):
    """
    Tracks seat availability for a specific schedule on a specific date.
    Created dynamically when users search for buses.
    """

    __tablename__ = "seat_availability"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    travel_date = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    seat_number = Column(String(10), nullable=False)
    
    # Status
    is_booked = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)  # Temporarily held during booking
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=True)
    
    # Block expiry (for temporary holds)
    blocked_until = Column(String(30), nullable=True)
    
    # Gender info for ladies-only enforcement
    passenger_gender = Column(String(10), nullable=True)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="seat_availability")

    class Meta:
        unique_together = ("schedule_id", "travel_date", "seat_number")

    def __repr__(self):
        return f"<SeatAvailability(schedule={self.schedule_id}, date={self.travel_date}, seat={self.seat_number})>"
