"""
Coupon schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CouponApplyRequest(BaseModel):
    """Schema for applying a coupon."""
    code: str = Field(..., min_length=3, max_length=50)
    booking_amount: float = Field(..., gt=0)
    route_id: Optional[int] = None


class CouponApplyResponse(BaseModel):
    """Schema for coupon application result."""
    valid: bool
    code: str
    discount_amount: float = 0.0
    message: str
    description: Optional[str] = None


class CouponResponse(BaseModel):
    """Schema for coupon response (admin)."""
    id: int
    code: str
    description: str
    discount_type: str
    discount_value: float
    max_discount: Optional[float]
    min_booking_amount: float
    max_uses: Optional[int]
    max_uses_per_user: int
    current_uses: int
    valid_from: str
    valid_until: str
    is_active: bool
    first_booking_only: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CouponCreate(BaseModel):
    """Schema for creating a coupon (admin)."""
    code: str = Field(..., min_length=3, max_length=50)
    description: str
    discount_type: str  # "percentage" or "flat"
    discount_value: float = Field(..., gt=0)
    max_discount: Optional[float] = None
    min_booking_amount: float = 0.0
    max_uses: Optional[int] = None
    max_uses_per_user: int = 1
    valid_from: str
    valid_until: str
    applicable_routes: Optional[str] = None
    first_booking_only: bool = False
