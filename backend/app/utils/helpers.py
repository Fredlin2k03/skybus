"""
Helper utilities for the SkyBus application.
"""

import random
import string
from datetime import datetime, timezone
from typing import Optional


def generate_booking_id() -> str:
    """
    Generate a unique booking ID in format SB-XXXXXXXX.
    Uses timestamp + random chars for uniqueness.
    """
    timestamp_part = datetime.now(timezone.utc).strftime("%y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"SB-{timestamp_part}{random_part}"


def generate_pnr() -> str:
    """Generate a PNR number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def format_duration(minutes: int) -> str:
    """
    Format duration in minutes to human-readable string.
    E.g., 370 -> "6h 10m"
    """
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"


def calculate_gst(amount: float, gst_rate: float = 5.0) -> float:
    """
    Calculate GST on the fare amount.
    Bus travel in India attracts 5% GST.
    """
    return round(amount * gst_rate / 100, 2)


def calculate_cancellation_charges(
    total_amount: float,
    travel_date: str,
    cancellation_time: Optional[datetime] = None
) -> float:
    """
    Calculate cancellation charges based on how far in advance the cancellation is.
    
    Policy:
    - >48 hours before departure: 10% charge
    - 24-48 hours: 25% charge
    - 12-24 hours: 50% charge
    - <12 hours: 75% charge (no refund for <4 hours)
    """
    if not cancellation_time:
        cancellation_time = datetime.now(timezone.utc)
    
    travel_datetime = datetime.strptime(travel_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    hours_before = (travel_datetime - cancellation_time).total_seconds() / 3600
    
    if hours_before > 48:
        charge_percent = 10
    elif hours_before > 24:
        charge_percent = 25
    elif hours_before > 12:
        charge_percent = 50
    elif hours_before > 4:
        charge_percent = 75
    else:
        charge_percent = 100  # No refund
    
    return round(total_amount * charge_percent / 100, 2)


def get_day_of_week(date_str: str) -> str:
    """Get day of week abbreviation from date string."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return days[dt.weekday()]


def validate_travel_date(date_str: str) -> bool:
    """Validate that travel date is today or in the future."""
    try:
        travel_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        return travel_date >= today
    except ValueError:
        return False


def mask_email(email: str) -> str:
    """Mask email for privacy. e.g., j***n@gmail.com"""
    parts = email.split("@")
    if len(parts[0]) <= 2:
        masked = parts[0][0] + "***"
    else:
        masked = parts[0][0] + "***" + parts[0][-1]
    return f"{masked}@{parts[1]}"


def mask_phone(phone: str) -> str:
    """Mask phone number. e.g., ******7890"""
    if len(phone) >= 10:
        return "******" + phone[-4:]
    return "***" + phone[-2:]
