"""
Booking models - Bookings, Passengers, and Payments.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class BookingStatus(str, enum.Enum):
    """Booking status states."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status states."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Booking(Base):
    """Main booking record linking user, schedule, and passengers."""

    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(String(20), unique=True, nullable=False, index=True)  # SB-XXXXXXXX
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    
    # Journey details
    travel_date = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    boarding_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    dropping_stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    
    # Pricing
    base_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    gst_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Coupon
    coupon_code = Column(String(50), nullable=True)
    
    # Contact info
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(15), nullable=False)
    
    # GST (optional)
    gst_number = Column(String(20), nullable=True)
    company_name = Column(String(200), nullable=True)
    
    # Status
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Cancellation
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(String(500), nullable=True)
    refund_amount = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    schedule = relationship("Schedule", back_populates="bookings")
    passengers = relationship("Passenger", back_populates="booking", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    boarding_stop = relationship("Stop", foreign_keys=[boarding_stop_id])
    dropping_stop = relationship("Stop", foreign_keys=[dropping_stop_id])

    def __repr__(self):
        return f"<Booking(id={self.booking_id}, status={self.status})>"


class Passenger(Base):
    """Individual passenger in a booking."""

    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    
    # Passenger details
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)
    
    # Seat
    seat_number = Column(String(10), nullable=False)
    seat_type = Column(String(20), nullable=False)  # seater, sleeper, semi-sleeper
    seat_fare = Column(Float, nullable=False)
    
    # ID (optional)
    id_type = Column(String(50), nullable=True)
    id_number = Column(String(50), nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="passengers")

    def __repr__(self):
        return f"<Passenger(name={self.name}, seat={self.seat_number})>"


class Payment(Base):
    """Payment records for bookings."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    
    # Razorpay details
    razorpay_order_id = Column(String(100), nullable=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    
    # Payment info
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    method = Column(String(50), nullable=True)  # card, upi, netbanking, wallet
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    paid_at = Column(DateTime, nullable=True)
    
    # Refund details
    refund_id = Column(String(100), nullable=True)
    refunded_at = Column(DateTime, nullable=True)
    refund_amount = Column(Float, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="payment")

    def __repr__(self):
        return f"<Payment(booking={self.booking_id}, status={self.status})>"
