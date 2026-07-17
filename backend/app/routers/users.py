"""
Users router - handles profile management and user-specific operations.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    if data.full_name:
        current_user.full_name = data.full_name
    if data.phone:
        # Check if phone is taken
        existing = db.query(User).filter(User.phone == data.phone, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Phone number already in use")
        current_user.phone = data.phone
    if data.gender:
        current_user.gender = data.gender
    if data.date_of_birth:
        from datetime import datetime
        try:
            current_user.date_of_birth = datetime.strptime(data.date_of_birth, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/booking-stats")
def get_booking_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's booking statistics."""
    from app.models.booking import Booking, BookingStatus
    from sqlalchemy import func
    
    total_bookings = db.query(func.count(Booking.id)).filter(
        Booking.user_id == current_user.id
    ).scalar()
    
    completed_trips = db.query(func.count(Booking.id)).filter(
        Booking.user_id == current_user.id,
        Booking.status == BookingStatus.COMPLETED
    ).scalar()
    
    total_spent = db.query(func.sum(Booking.total_amount)).filter(
        Booking.user_id == current_user.id,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED])
    ).scalar() or 0
    
    cancelled = db.query(func.count(Booking.id)).filter(
        Booking.user_id == current_user.id,
        Booking.status == BookingStatus.CANCELLED
    ).scalar()
    
    return {
        "total_bookings": total_bookings,
        "completed_trips": completed_trips,
        "total_spent": round(total_spent, 2),
        "cancelled_bookings": cancelled,
    }
