"""
Review model - Post-trip ratings and reviews.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Review(Base):
    """User reviews for completed trips."""

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    
    # Ratings (1-5 scale)
    overall_rating = Column(Float, nullable=False)
    punctuality_rating = Column(Float, nullable=True)
    comfort_rating = Column(Float, nullable=True)
    cleanliness_rating = Column(Float, nullable=True)
    staff_rating = Column(Float, nullable=True)
    
    # Review text
    title = Column(String(200), nullable=True)
    comment = Column(Text, nullable=True)
    
    # Status
    is_verified = Column(Boolean, default=True)  # Verified purchase
    is_visible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.overall_rating}, user={self.user_id})>"
