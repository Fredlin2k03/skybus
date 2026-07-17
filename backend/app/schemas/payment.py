"""
Payment schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateOrderRequest(BaseModel):
    """Schema for creating Razorpay order."""
    booking_id: str


class CreateOrderResponse(BaseModel):
    """Schema for Razorpay order creation response."""
    order_id: str
    amount: int  # Amount in paise
    currency: str
    booking_id: str
    key_id: str  # Razorpay key for frontend


class VerifyPaymentRequest(BaseModel):
    """Schema for payment verification."""
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    booking_id: str


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    booking_id: int
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    amount: float
    currency: str
    method: Optional[str]
    status: str
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    """Schema for initiating refund."""
    booking_id: str
    amount: Optional[float] = None  # None = full refund


class RefundResponse(BaseModel):
    """Schema for refund response."""
    refund_id: str
    amount: float
    status: str
