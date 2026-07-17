"""
Review schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema for creating a review."""
    booking_id: int
    overall_rating: float = Field(..., ge=1, le=5)
    punctuality_rating: Optional[float] = Field(None, ge=1, le=5)
    comfort_rating: Optional[float] = Field(None, ge=1, le=5)
    cleanliness_rating: Optional[float] = Field(None, ge=1, le=5)
    staff_rating: Optional[float] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    """Schema for review response."""
    id: int
    user_id: int
    user_name: str = ""
    booking_id: int
    overall_rating: float
    punctuality_rating: Optional[float]
    comfort_rating: Optional[float]
    cleanliness_rating: Optional[float]
    staff_rating: Optional[float]
    title: Optional[str]
    comment: Optional[str]
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewStats(BaseModel):
    """Aggregated review statistics."""
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: count, 2: count, ...5: count}
