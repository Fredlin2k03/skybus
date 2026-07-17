"""
Bookings router - handles booking creation, retrieval, and cancellation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, Passenger, Payment, BookingStatus, PaymentStatus
from app.models.route import Schedule, ScheduleStop, Stop
from app.models.bus import Bus
from app.models.seat import SeatLayout, SeatAvailability
from app.models.coupon import Coupon, CouponUsage
from app.schemas.booking import (
    BookingCreate, BookingResponse, BookingDetailResponse, 
    BookingCancelRequest, PassengerResponse
)
from app.middleware.auth import get_current_user
from app.utils.helpers import generate_booking_id, calculate_gst, calculate_cancellation_charges, validate_travel_date
from app.utils.email import send_booking_confirmation, send_cancellation_email

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new booking.
    Validates seat availability, applies coupon, calculates pricing.
    """
    # Validate travel date
    if not validate_travel_date(data.travel_date):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Travel date must be today or in the future"
        )
    
    # Get schedule
    schedule = (
        db.query(Schedule)
        .options(joinedload(Schedule.bus).joinedload(Bus.bus_type))
        .filter(Schedule.id == data.schedule_id, Schedule.is_active == True)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Validate stops
    boarding_stop = db.query(Stop).filter(Stop.id == data.boarding_stop_id).first()
    dropping_stop = db.query(Stop).filter(Stop.id == data.dropping_stop_id).first()
    if not boarding_stop or not dropping_stop:
        raise HTTPException(status_code=400, detail="Invalid boarding/dropping point")
    
    # Validate and lock seats
    seat_numbers = [p.seat_number for p in data.passengers]
    
    for seat_num in seat_numbers:
        # Check if seat exists in layout
        seat_layout = (
            db.query(SeatLayout)
            .filter(SeatLayout.bus_id == schedule.bus_id, SeatLayout.seat_number == seat_num)
            .first()
        )
        if not seat_layout:
            raise HTTPException(
                status_code=400, 
                detail=f"Seat {seat_num} does not exist on this bus"
            )
        
        # Check availability
        existing = (
            db.query(SeatAvailability)
            .filter(
                SeatAvailability.schedule_id == schedule.id,
                SeatAvailability.travel_date == data.travel_date,
                SeatAvailability.seat_number == seat_num,
                SeatAvailability.is_booked == True,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Seat {seat_num} is already booked"
            )
    
    # Calculate pricing
    base_amount = 0.0
    passenger_records = []
    
    for passenger_data in data.passengers:
        seat_layout = (
            db.query(SeatLayout)
            .filter(SeatLayout.bus_id == schedule.bus_id, SeatLayout.seat_number == passenger_data.seat_number)
            .first()
        )
        
        # Calculate fare based on seat type
        if seat_layout.seat_type.value == "sleeper" and schedule.sleeper_fare:
            seat_fare = schedule.sleeper_fare * seat_layout.price_multiplier
        else:
            seat_fare = schedule.base_fare * seat_layout.price_multiplier
        
        base_amount += seat_fare
        passenger_records.append({
            **passenger_data.model_dump(),
            "seat_fare": seat_fare,
        })
    
    # Apply coupon if provided
    discount_amount = 0.0
    if data.coupon_code:
        coupon = (
            db.query(Coupon)
            .filter(Coupon.code == data.coupon_code.upper(), Coupon.is_active == True)
            .first()
        )
        if coupon:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if coupon.valid_from <= today <= coupon.valid_until:
                if base_amount >= coupon.min_booking_amount:
                    # Check usage limits
                    user_uses = (
                        db.query(func.count(CouponUsage.id))
                        .filter(CouponUsage.coupon_id == coupon.id, CouponUsage.user_id == current_user.id)
                        .scalar()
                    )
                    if user_uses < coupon.max_uses_per_user:
                        if coupon.discount_type.value == "percentage":
                            discount_amount = base_amount * coupon.discount_value / 100
                            if coupon.max_discount:
                                discount_amount = min(discount_amount, coupon.max_discount)
                        else:
                            discount_amount = coupon.discount_value
                        discount_amount = min(discount_amount, base_amount)
    
    # Calculate GST
    taxable_amount = base_amount - discount_amount
    gst_amount = calculate_gst(taxable_amount)
    total_amount = taxable_amount + gst_amount
    
    # Create booking
    booking_id = generate_booking_id()
    booking = Booking(
        booking_id=booking_id,
        user_id=current_user.id,
        schedule_id=schedule.id,
        travel_date=data.travel_date,
        boarding_stop_id=data.boarding_stop_id,
        dropping_stop_id=data.dropping_stop_id,
        base_amount=round(base_amount, 2),
        discount_amount=round(discount_amount, 2),
        gst_amount=round(gst_amount, 2),
        total_amount=round(total_amount, 2),
        coupon_code=data.coupon_code,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        gst_number=data.gst_number,
        company_name=data.company_name,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.flush()
    
    # Create passengers
    for p_data in passenger_records:
        passenger = Passenger(
            booking_id=booking.id,
            name=p_data["name"],
            age=p_data["age"],
            gender=p_data["gender"],
            seat_number=p_data["seat_number"],
            seat_type=p_data["seat_type"],
            seat_fare=p_data["seat_fare"],
            id_type=p_data.get("id_type"),
            id_number=p_data.get("id_number"),
        )
        db.add(passenger)
    
    # Mark seats as booked
    for p_data in data.passengers:
        seat_avail = SeatAvailability(
            schedule_id=schedule.id,
            travel_date=data.travel_date,
            seat_number=p_data.seat_number,
            is_booked=True,
            booking_id=booking.id,
            passenger_gender=p_data.gender,
        )
        db.add(seat_avail)
    
    # Record coupon usage
    if data.coupon_code and discount_amount > 0:
        coupon_usage = CouponUsage(
            coupon_id=coupon.id,
            user_id=current_user.id,
            booking_id=booking.id,
            discount_applied=discount_amount,
        )
        db.add(coupon_usage)
        coupon.current_uses += 1
    
    # Create payment record
    payment = Payment(
        booking_id=booking.id,
        amount=round(total_amount, 2),
        currency="INR",
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    
    db.commit()
    db.refresh(booking)
    
    return BookingResponse.model_validate(booking)


@router.get("/my-bookings")
def get_my_bookings(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's bookings with pagination."""
    query = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
    )
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    total = query.count()
    bookings = (
        query
        .options(
            joinedload(Booking.passengers),
            joinedload(Booking.schedule).joinedload(Schedule.route),
            joinedload(Booking.schedule).joinedload(Schedule.bus),
            joinedload(Booking.boarding_stop),
            joinedload(Booking.dropping_stop),
            joinedload(Booking.payment),
        )
        .order_by(Booking.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    
    results = []
    for b in bookings:
        results.append({
            "booking": BookingResponse.model_validate(b).model_dump(),
            "route_name": b.schedule.route.name,
            "source_city": b.schedule.route.source_city,
            "destination_city": b.schedule.route.destination_city,
            "bus_name": b.schedule.bus.name,
            "bus_type": b.schedule.bus.bus_type.name if b.schedule.bus.bus_type else "",
            "departure_time": b.schedule.departure_time,
            "arrival_time": b.schedule.arrival_time,
            "boarding_point": b.boarding_stop.name,
            "dropping_point": b.dropping_stop.name,
            "payment_status": b.payment.status.value if b.payment else None,
        })
    
    return {
        "bookings": results,
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.get("/{booking_id}")
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed booking information."""
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.passengers),
            joinedload(Booking.schedule).joinedload(Schedule.route),
            joinedload(Booking.schedule).joinedload(Schedule.bus).joinedload(Bus.bus_type),
            joinedload(Booking.boarding_stop),
            joinedload(Booking.dropping_stop),
            joinedload(Booking.payment),
        )
        .filter(Booking.booking_id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return {
        "booking": BookingResponse.model_validate(booking).model_dump(),
        "route_name": booking.schedule.route.name,
        "source_city": booking.schedule.route.source_city,
        "destination_city": booking.schedule.route.destination_city,
        "bus_name": booking.schedule.bus.name,
        "bus_type": booking.schedule.bus.bus_type.name,
        "departure_time": booking.schedule.departure_time,
        "arrival_time": booking.schedule.arrival_time,
        "boarding_point": booking.boarding_stop.name,
        "dropping_point": booking.dropping_stop.name,
        "payment_status": booking.payment.status.value if booking.payment else None,
    }


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    data: BookingCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking and process refund."""
    booking = (
        db.query(Booking)
        .filter(Booking.booking_id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel booking with status: {booking.status.value}"
        )
    
    # Calculate refund
    cancellation_charges = calculate_cancellation_charges(
        booking.total_amount, booking.travel_date
    )
    refund_amount = booking.total_amount - cancellation_charges
    
    # Update booking
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancellation_reason = data.reason
    booking.refund_amount = refund_amount
    
    # Release seats
    db.query(SeatAvailability).filter(
        SeatAvailability.booking_id == booking.id
    ).delete()
    
    # Update payment
    if booking.payment:
        booking.payment.status = PaymentStatus.REFUNDED
        booking.payment.refund_amount = refund_amount
        booking.payment.refunded_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Send cancellation email
    send_cancellation_email(
        booking.booking_id,
        booking.contact_email,
        current_user.full_name,
        refund_amount
    )
    
    return {
        "message": "Booking cancelled successfully",
        "booking_id": booking.booking_id,
        "refund_amount": refund_amount,
        "cancellation_charges": cancellation_charges,
    }
