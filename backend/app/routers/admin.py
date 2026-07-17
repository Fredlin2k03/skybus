"""
Admin router - dashboard, management, and reporting endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.user import User, UserRole
from app.models.booking import Booking, Payment, BookingStatus, PaymentStatus
from app.models.route import Route, Schedule, Stop
from app.models.bus import Bus, BusType
from app.models.review import Review
from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponResponse
from app.middleware.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
def get_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics."""
    # Total revenue
    total_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.SUCCESS
    ).scalar() or 0
    
    # Today's revenue
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_bookings = db.query(func.count(Booking.id)).filter(
        func.date(Booking.created_at) == today
    ).scalar() or 0
    
    # Total bookings
    total_bookings = db.query(func.count(Booking.id)).scalar()
    
    # Active bookings (confirmed, upcoming)
    active_bookings = db.query(func.count(Booking.id)).filter(
        Booking.status == BookingStatus.CONFIRMED,
        Booking.travel_date >= today
    ).scalar() or 0
    
    # Total users
    total_users = db.query(func.count(User.id)).filter(
        User.role == UserRole.CUSTOMER
    ).scalar()
    
    # Total routes
    total_routes = db.query(func.count(Route.id)).filter(Route.is_active == True).scalar()
    
    # Total buses
    total_buses = db.query(func.count(Bus.id)).filter(Bus.is_active == True).scalar()
    
    # Cancellation rate
    cancelled = db.query(func.count(Booking.id)).filter(
        Booking.status == BookingStatus.CANCELLED
    ).scalar() or 0
    cancellation_rate = (cancelled / total_bookings * 100) if total_bookings > 0 else 0
    
    # Average rating
    avg_rating = db.query(func.avg(Review.overall_rating)).scalar() or 0
    
    # Recent bookings
    recent_bookings = (
        db.query(Booking)
        .options(joinedload(Booking.user), joinedload(Booking.schedule).joinedload(Schedule.route))
        .order_by(desc(Booking.created_at))
        .limit(10)
        .all()
    )
    
    recent = [
        {
            "booking_id": b.booking_id,
            "user_name": b.user.full_name,
            "route": b.schedule.route.name,
            "travel_date": b.travel_date,
            "amount": b.total_amount,
            "status": b.status.value,
            "created_at": b.created_at.isoformat(),
        }
        for b in recent_bookings
    ]
    
    return {
        "stats": {
            "total_revenue": round(total_revenue, 2),
            "today_bookings": today_bookings,
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "total_users": total_users,
            "total_routes": total_routes,
            "total_buses": total_buses,
            "cancellation_rate": round(cancellation_rate, 1),
            "average_rating": round(avg_rating, 1),
        },
        "recent_bookings": recent,
    }


@router.get("/bookings")
def get_all_bookings(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all bookings with filters (admin)."""
    query = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.schedule).joinedload(Schedule.route),
        joinedload(Booking.passengers),
    )
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if date_from:
        query = query.filter(Booking.travel_date >= date_from)
    if date_to:
        query = query.filter(Booking.travel_date <= date_to)
    
    total = query.count()
    bookings = (
        query
        .order_by(desc(Booking.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    results = [
        {
            "booking_id": b.booking_id,
            "user_name": b.user.full_name,
            "user_email": b.user.email,
            "route": b.schedule.route.name,
            "travel_date": b.travel_date,
            "passengers": len(b.passengers),
            "amount": b.total_amount,
            "status": b.status.value,
            "created_at": b.created_at.isoformat(),
        }
        for b in bookings
    ]
    
    return {"bookings": results, "total": total, "page": page, "per_page": per_page}


@router.get("/revenue")
def get_revenue_report(
    period: str = Query("month"),  # week, month, year
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get revenue report with breakdown."""
    today = datetime.now(timezone.utc).date()
    
    if period == "week":
        start_date = today - timedelta(days=7)
    elif period == "year":
        start_date = today - timedelta(days=365)
    else:
        start_date = today - timedelta(days=30)
    
    # Daily revenue
    daily_revenue = (
        db.query(
            func.date(Payment.paid_at).label("date"),
            func.sum(Payment.amount).label("revenue"),
            func.count(Payment.id).label("transactions")
        )
        .filter(
            Payment.status == PaymentStatus.SUCCESS,
            func.date(Payment.paid_at) >= start_date.isoformat()
        )
        .group_by(func.date(Payment.paid_at))
        .order_by(func.date(Payment.paid_at))
        .all()
    )
    
    # Revenue by route
    route_revenue = (
        db.query(
            Route.name,
            func.sum(Booking.total_amount).label("revenue"),
            func.count(Booking.id).label("bookings")
        )
        .join(Schedule, Schedule.route_id == Route.id)
        .join(Booking, Booking.schedule_id == Schedule.id)
        .filter(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.COMPLETED]),
            Booking.travel_date >= start_date.isoformat()
        )
        .group_by(Route.name)
        .order_by(desc(func.sum(Booking.total_amount)))
        .limit(10)
        .all()
    )
    
    return {
        "period": period,
        "daily_revenue": [
            {"date": str(d.date), "revenue": float(d.revenue), "transactions": d.transactions}
            for d in daily_revenue
        ],
        "route_revenue": [
            {"route": r.name, "revenue": float(r.revenue), "bookings": r.bookings}
            for r in route_revenue
        ],
    }


@router.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin)."""
    total = db.query(func.count(User.id)).scalar()
    users = (
        db.query(User)
        .order_by(desc(User.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    return {
        "users": [
            {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "phone": u.phone,
                "role": u.role.value,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat(),
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


# Coupon management
@router.post("/coupons", response_model=CouponResponse, status_code=201)
def create_coupon(
    data: CouponCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new coupon (admin)."""
    existing = db.query(Coupon).filter(Coupon.code == data.code.upper()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Coupon code already exists")
    
    coupon = Coupon(
        code=data.code.upper(),
        description=data.description,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        max_discount=data.max_discount,
        min_booking_amount=data.min_booking_amount,
        max_uses=data.max_uses,
        max_uses_per_user=data.max_uses_per_user,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        applicable_routes=data.applicable_routes,
        first_booking_only=data.first_booking_only,
    )
    db.add(coupon)
    db.commit()
    db.refresh(coupon)
    
    return CouponResponse.model_validate(coupon)


@router.get("/coupons")
def list_coupons(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all coupons (admin)."""
    coupons = db.query(Coupon).order_by(desc(Coupon.created_at)).all()
    return [CouponResponse.model_validate(c) for c in coupons]


@router.put("/coupons/{coupon_id}/toggle")
def toggle_coupon(
    coupon_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle coupon active status."""
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.is_active = not coupon.is_active
    db.commit()
    
    return {"message": f"Coupon {'activated' if coupon.is_active else 'deactivated'}"}
