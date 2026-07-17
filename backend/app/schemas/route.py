"""
Route schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List


class StopResponse(BaseModel):
    """Schema for stop response."""
    id: int
    name: str
    city: str
    state: str
    address: Optional[str]
    landmark: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True


class RouteResponse(BaseModel):
    """Schema for route response."""
    id: int
    name: str
    source_city: str
    destination_city: str
    distance_km: float
    estimated_duration_minutes: int
    is_active: bool

    class Config:
        from_attributes = True


class ScheduleStopResponse(BaseModel):
    """Schema for schedule stop details."""
    stop: StopResponse
    sequence: int
    arrival_offset_minutes: int
    departure_offset_minutes: int
    fare_from_origin: float
    is_boarding_point: bool
    is_dropping_point: bool

    class Config:
        from_attributes = True


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""
    id: int
    route: RouteResponse
    bus_id: int
    departure_time: str
    arrival_time: str
    duration_minutes: int
    days_of_operation: str
    base_fare: float
    sleeper_fare: Optional[float]
    is_active: bool
    stops: List[ScheduleStopResponse] = []

    class Config:
        from_attributes = True


class CitySearchResponse(BaseModel):
    """Schema for city autocomplete."""
    city: str
    state: str
    stop_count: int


class SearchRequest(BaseModel):
    """Schema for bus search."""
    source: str
    destination: str
    date: str  # YYYY-MM-DD format
    bus_type: Optional[str] = None
    departure_time: Optional[str] = None  # "morning", "afternoon", "evening", "night"
    price_min: Optional[float] = None
    price_max: Optional[float] = None
