"""
Bus schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List


class BusAmenityResponse(BaseModel):
    """Schema for bus amenity response."""
    id: int
    name: str
    icon: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class BusTypeResponse(BaseModel):
    """Schema for bus type response."""
    id: int
    name: str
    category: str
    seat_layout: str
    total_seats: int
    total_rows: int
    has_upper_deck: bool
    description: Optional[str]

    class Config:
        from_attributes = True


class BusResponse(BaseModel):
    """Schema for bus response."""
    id: int
    registration_number: str
    name: str
    bus_type: BusTypeResponse
    amenities: List[BusAmenityResponse]
    is_active: bool
    manufacturing_year: Optional[int]

    class Config:
        from_attributes = True


class BusLocationResponse(BaseModel):
    """Schema for live bus location."""
    bus_id: int
    latitude: float
    longitude: float
    last_updated: str
    speed_kmph: Optional[float] = None
    next_stop: Optional[str] = None
    eta_minutes: Optional[int] = None


class SeatLayoutResponse(BaseModel):
    """Schema for individual seat in layout."""
    seat_number: str
    row_number: int
    column_number: int
    seat_type: str
    deck: str
    is_window: bool
    is_aisle: bool
    is_ladies_only: bool
    price_multiplier: float
    is_available: bool
    is_booked: bool = False
    is_blocked: bool = False
    passenger_gender: Optional[str] = None

    class Config:
        from_attributes = True


class BusSearchResult(BaseModel):
    """Schema for bus search results."""
    schedule_id: int
    bus: BusResponse
    route_name: str
    source_city: str
    destination_city: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    base_fare: float
    sleeper_fare: Optional[float]
    available_seats: int
    total_seats: int
    amenities: List[str]
    rating: Optional[float]
    total_reviews: int

    class Config:
        from_attributes = True
