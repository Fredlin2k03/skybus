"""
Bus models - Bus fleet, types, and amenities.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


# Many-to-many relationship between Bus and BusAmenity
bus_amenities = Table(
    "bus_amenities_link",
    Base.metadata,
    Column("bus_id", Integer, ForeignKey("buses.id"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("bus_amenities.id"), primary_key=True),
)


class BusCategory(str, enum.Enum):
    """Bus category types."""
    AC_SLEEPER = "AC Sleeper"
    AC_SEATER = "AC Seater"
    NON_AC_SLEEPER = "Non-AC Sleeper"
    NON_AC_SEATER = "Non-AC Seater"
    VOLVO_MULTI_AXLE = "Volvo Multi-Axle"


class SeatLayoutType(str, enum.Enum):
    """Seat layout configurations."""
    SEATER_2X2 = "2x2"  # 2+2 seater
    SLEEPER_2X1 = "2x1"  # 2+1 sleeper
    SEMI_SLEEPER_2X2 = "2x2_semi"  # 2+2 semi-sleeper
    SLEEPER_2X1_UPPER_LOWER = "2x1_ul"  # 2+1 with upper/lower


class BusType(Base):
    """Bus type/category definitions."""

    __tablename__ = "bus_types"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(SQLEnum(BusCategory), nullable=False)
    seat_layout = Column(SQLEnum(SeatLayoutType), nullable=False)
    total_seats = Column(Integer, nullable=False)
    total_rows = Column(Integer, nullable=False)
    has_upper_deck = Column(Boolean, default=False)
    description = Column(String(500), nullable=True)
    
    # Relationships
    buses = relationship("Bus", back_populates="bus_type")

    def __repr__(self):
        return f"<BusType(id={self.id}, name={self.name})>"


class Bus(Base):
    """Individual bus in the SkyBus fleet."""

    __tablename__ = "buses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    registration_number = Column(String(20), unique=True, nullable=False)
    bus_type_id = Column(Integer, ForeignKey("bus_types.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "SkyBus Platinum"
    
    # Status
    is_active = Column(Boolean, default=True)
    manufacturing_year = Column(Integer, nullable=True)
    last_service_date = Column(String(20), nullable=True)
    
    # Tracking
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    last_location_update = Column(String(30), nullable=True)
    
    # Relationships
    bus_type = relationship("BusType", back_populates="buses")
    amenities = relationship("BusAmenity", secondary=bus_amenities, back_populates="buses")
    schedules = relationship("Schedule", back_populates="bus")
    seat_layouts = relationship("SeatLayout", back_populates="bus")

    def __repr__(self):
        return f"<Bus(id={self.id}, reg={self.registration_number}, name={self.name})>"


class BusAmenity(Base):
    """Amenities available on buses."""

    __tablename__ = "bus_amenities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    icon = Column(String(50), nullable=True)  # Icon identifier for frontend
    description = Column(String(255), nullable=True)
    
    # Relationships
    buses = relationship("Bus", secondary=bus_amenities, back_populates="amenities")

    def __repr__(self):
        return f"<BusAmenity(id={self.id}, name={self.name})>"
