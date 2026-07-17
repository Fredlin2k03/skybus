"""
SQLAlchemy Models Package.
Import all models here to ensure they're registered with the Base metadata.
"""

from app.models.user import User, UserRole
from app.models.bus import Bus, BusType, BusAmenity, BusCategory, SeatLayoutType
from app.models.route import Route, Stop, Schedule, ScheduleStop
from app.models.booking import Booking, Passenger, Payment, BookingStatus, PaymentStatus
from app.models.seat import SeatLayout, SeatAvailability, SeatType, DeckType
from app.models.review import Review
from app.models.coupon import Coupon, CouponUsage, DiscountType

__all__ = [
    "User", "UserRole",
    "Bus", "BusType", "BusAmenity", "BusCategory", "SeatLayoutType",
    "Route", "Stop", "Schedule", "ScheduleStop",
    "Booking", "Passenger", "Payment", "BookingStatus", "PaymentStatus",
    "SeatLayout", "SeatAvailability", "SeatType", "DeckType",
    "Review",
    "Coupon", "CouponUsage", "DiscountType",
]