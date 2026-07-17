"""
Coupon validation service.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from app.models.coupon import Coupon, CouponUsage
from app.schemas.coupon import CouponApplyResponse


def validate_coupon(
    code: str, 
    booking_amount: float, 
    user_id: int, 
    route_id: int = None, 
    db: Session = None
) -> CouponApplyResponse:
    """
    Validate and calculate discount for a coupon code.
    
    Args:
        code: Coupon code
        booking_amount: Total booking amount before discount
        user_id: Current user's ID
        route_id: Optional route ID for route-specific coupons
        db: Database session
    
    Returns:
        CouponApplyResponse with validation result
    """
    coupon = db.query(Coupon).filter(
        Coupon.code == code.upper(), 
        Coupon.is_active == True
    ).first()
    
    if not coupon:
        return CouponApplyResponse(
            valid=False, code=code, discount_amount=0,
            message="Invalid coupon code"
        )
    
    # Check validity period
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if today < coupon.valid_from or today > coupon.valid_until:
        return CouponApplyResponse(
            valid=False, code=code, discount_amount=0,
            message="Coupon has expired or is not yet active"
        )
    
    # Check minimum booking amount
    if booking_amount < coupon.min_booking_amount:
        return CouponApplyResponse(
            valid=False, code=code, discount_amount=0,
            message=f"Minimum booking amount of ₹{coupon.min_booking_amount} required"
        )
    
    # Check total usage limit
    if coupon.max_uses and coupon.current_uses >= coupon.max_uses:
        return CouponApplyResponse(
            valid=False, code=code, discount_amount=0,
            message="Coupon usage limit reached"
        )
    
    # Check per-user usage limit
    user_uses = db.query(func.count(CouponUsage.id)).filter(
        CouponUsage.coupon_id == coupon.id,
        CouponUsage.user_id == user_id
    ).scalar()
    
    if user_uses >= coupon.max_uses_per_user:
        return CouponApplyResponse(
            valid=False, code=code, discount_amount=0,
            message="You have already used this coupon"
        )
    
    # Check route applicability
    if coupon.applicable_routes and route_id:
        applicable_ids = [int(x) for x in coupon.applicable_routes.split(",")]
        if route_id not in applicable_ids:
            return CouponApplyResponse(
                valid=False, code=code, discount_amount=0,
                message="Coupon not applicable for this route"
            )
    
    # Calculate discount
    if coupon.discount_type.value == "percentage":
        discount = booking_amount * coupon.discount_value / 100
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value
    
    discount = min(discount, booking_amount)
    
    return CouponApplyResponse(
        valid=True,
        code=code,
        discount_amount=round(discount, 2),
        message=f"Coupon applied! You save ₹{discount:.0f}",
        description=coupon.description,
    )
