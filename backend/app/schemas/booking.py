"""
Booking schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class PassengerCreate(BaseModel):
    """Schema for creating a passenger."""
    name: str = Field(..., min_length=2, max_length=255)
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern=r"^(male|female|other)$")
    seat_number: str
    seat_type: str
    id_type: Optional[str] = None
    id_number: Optional[str] = None


class BookingCreate(BaseModel):
    """Schema for creating a booking."""
    schedule_id: int
    travel_date: str  # YYYY-MM-DD
    boarding_stop_id: int
    dropping_stop_id: int
    passengers: List[PassengerCreate] = Field(..., min_length=1, max_length=6)
    contact_email: EmailStr
    contact_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    coupon_code: Optional[str] = None
    gst_number: Optional[str] = None
    company_name: Optional[str] = None


class PassengerResponse(BaseModel):
    """Schema for passenger response."""
    id: int
    name: str
    age: int
    gender: str
    seat_number: str
    seat_type: str
    seat_fare: float

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    """Schema for booking response."""
    id: int
    booking_id: str
    user_id: int
    schedule_id: int
    travel_date: str
    boarding_stop_id: int
    dropping_stop_id: int
    base_amount: float
    discount_amount: float
    gst_amount: float
    total_amount: float
    coupon_code: Optional[str]
    contact_email: str
    contact_phone: str
    status: str
    passengers: List[PassengerResponse]
    created_at: datetime
    cancelled_at: Optional[datetime]
    refund_amount: Optional[float]

    class Config:
        from_attributes = True


class BookingDetailResponse(BaseModel):
    """Detailed booking response with route info."""
    booking: BookingResponse
    route_name: str
    source_city: str
    destination_city: str
    bus_name: str
    bus_type: str
    departure_time: str
    arrival_time: str
    boarding_point: str
    dropping_point: str
    payment_status: Optional[str]


class BookingCancelRequest(BaseModel):
    """Schema for cancellation request."""
    reason: Optional[str] = None


class BookingListResponse(BaseModel):
    """Schema for paginated booking list."""
    bookings: List[BookingDetailResponse]
    total: int
    page: int
    per_page: int
