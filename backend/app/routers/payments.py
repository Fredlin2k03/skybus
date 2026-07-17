"""
Payments router - handles Razorpay order creation and payment verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import hashlib
import hmac
import json

from app.database import get_db
from app.models.user import User
from app.models.booking import Booking, Payment, BookingStatus, PaymentStatus
from app.schemas.payment import (
    CreateOrderRequest, CreateOrderResponse, 
    VerifyPaymentRequest, PaymentResponse
)
from app.middleware.auth import get_current_user
from app.config import settings
from app.utils.email import send_booking_confirmation

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_razorpay_order(
    data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a Razorpay order for a booking.
    In test mode, generates a mock order ID.
    """
    # Find the booking
    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == data.booking_id,
            Booking.user_id == current_user.id,
            Booking.status == BookingStatus.PENDING
        )
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or not in pending state")
    
    amount_paise = int(booking.total_amount * 100)  # Convert to paise
    
    # In production, we'd call Razorpay API here
    # For prototype, generate mock order ID
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_data = {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": booking.booking_id,
            "notes": {
                "booking_id": booking.booking_id,
                "user_email": current_user.email,
            }
        }
        order = client.order.create(data=order_data)
        order_id = order["id"]
    except Exception:
        # Fallback: generate mock order for development
        import random
        order_id = f"order_test_{booking.booking_id}_{random.randint(10000, 99999)}"
    
    # Update payment record
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        payment.razorpay_order_id = order_id
    
    db.commit()
    
    return CreateOrderResponse(
        order_id=order_id,
        amount=amount_paise,
        currency="INR",
        booking_id=booking.booking_id,
        key_id=settings.RAZORPAY_KEY_ID,
    )


@router.post("/verify")
def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment signature and confirm booking.
    """
    # Find booking
    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Verify signature
    # In production: verify using Razorpay's signature verification
    try:
        message = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"
        expected_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        signature_valid = hmac.compare_digest(expected_signature, data.razorpay_signature)
    except Exception:
        # For development/test mode, accept the payment
        signature_valid = True
    
    if not signature_valid and settings.ENVIRONMENT == "production":
        # Mark payment as failed
        payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
        if payment:
            payment.status = PaymentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # Update payment record
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        payment.razorpay_payment_id = data.razorpay_payment_id
        payment.razorpay_signature = data.razorpay_signature
        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = datetime.now(timezone.utc)
        payment.method = "online"
    
    # Confirm booking
    booking.status = BookingStatus.CONFIRMED
    
    db.commit()
    
    # Send confirmation email
    passengers = booking.passengers
    seats = ", ".join([p.seat_number for p in passengers])
    send_booking_confirmation(
        booking_id=booking.booking_id,
        to_email=booking.contact_email,
        passenger_name=passengers[0].name if passengers else current_user.full_name,
        route=f"{booking.schedule.route.source_city} → {booking.schedule.route.destination_city}",
        date=booking.travel_date,
        departure=booking.schedule.departure_time,
        seats=seats,
    )
    
    return {
        "message": "Payment verified successfully",
        "booking_id": booking.booking_id,
        "status": "confirmed",
    }


@router.post("/simulate-success")
def simulate_payment_success(
    data: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Development endpoint: Simulate a successful payment without Razorpay.
    Only available in development mode.
    """
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Not available in production")
    
    booking = (
        db.query(Booking)
        .filter(
            Booking.booking_id == data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Update payment
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    if payment:
        payment.razorpay_payment_id = f"pay_simulated_{booking.booking_id}"
        payment.status = PaymentStatus.SUCCESS
        payment.paid_at = datetime.now(timezone.utc)
        payment.method = "simulated"
    
    # Confirm booking
    booking.status = BookingStatus.CONFIRMED
    db.commit()
    
    # Send confirmation email
    passengers = booking.passengers
    seats = ", ".join([p.seat_number for p in passengers])
    send_booking_confirmation(
        booking_id=booking.booking_id,
        to_email=booking.contact_email,
        passenger_name=passengers[0].name if passengers else current_user.full_name,
        route=f"{booking.schedule.route.source_city} → {booking.schedule.route.destination_city}",
        date=booking.travel_date,
        departure=booking.schedule.departure_time,
        seats=seats,
    )
    
    return {
        "message": "Payment simulated successfully",
        "booking_id": booking.booking_id,
        "status": "confirmed",
    }


@router.get("/{booking_id}/status")
def get_payment_status(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status for a booking."""
    booking = (
        db.query(Booking)
        .filter(Booking.booking_id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    payment = db.query(Payment).filter(Payment.booking_id == booking.id).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    return {
        "booking_id": booking.booking_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "status": payment.status.value,
        "method": payment.method,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
    }
