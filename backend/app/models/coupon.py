"""
Coupon models - Discount coupons and usage tracking.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class DiscountType(str, enum.Enum):
    """Discount type: percentage or flat amount."""
    PERCENTAGE = "percentage"
    FLAT = "flat"


class Coupon(Base):
    """Discount coupons for bookings."""

    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    
    # Discount details
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    discount_value = Column(Float, nullable=False)  # Percentage or flat amount
    max_discount = Column(Float, nullable=True)  # Cap for percentage discounts
    min_booking_amount = Column(Float, default=0.0)
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Total uses allowed
    max_uses_per_user = Column(Integer, default=1)
    current_uses = Column(Integer, default=0)
    
    # Validity
    valid_from = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    valid_until = Column(String(10), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Targeting
    applicable_routes = Column(String(500), nullable=True)  # Comma-separated route IDs, null = all
    first_booking_only = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<Coupon(code={self.code}, type={self.discount_type}, value={self.discount_value})>"


class CouponUsage(Base):
    """Tracks coupon usage per user."""

    __tablename__ = "coupon_usages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    discount_applied = Column(Float, nullable=False)
    used_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<CouponUsage(coupon={self.coupon_id}, user={self.user_id})>"
