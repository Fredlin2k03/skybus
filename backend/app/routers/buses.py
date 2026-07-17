"""
Buses router - handles seat layouts, availability, and live tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
import random
import math
from datetime import datetime, timezone

from app.database import get_db
from app.models.bus import Bus, BusType
from app.models.seat import SeatLayout, SeatAvailability
from app.models.route import Schedule
from app.schemas.bus import SeatLayoutResponse, BusLocationResponse

router = APIRouter(prefix="/api/buses", tags=["Buses"])


@router.get("/{schedule_id}/seats")
def get_seat_layout(
    schedule_id: int,
    date: str = Query(...),  # YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Get seat layout with availability for a schedule on a given date.
    Returns the visual seat map with booking status.
    """
    # Get the schedule and bus
    schedule = (
        db.query(Schedule)
        .options(joinedload(Schedule.bus).joinedload(Bus.bus_type))
        .filter(Schedule.id == schedule_id)
        .first()
    )
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    bus = schedule.bus
    
    # Get seat layout for this bus
    seats = (
        db.query(SeatLayout)
        .filter(SeatLayout.bus_id == bus.id, SeatLayout.is_available == True)
        .order_by(SeatLayout.deck, SeatLayout.row_number, SeatLayout.column_number)
        .all()
    )
    
    if not seats:
        raise HTTPException(status_code=404, detail="Seat layout not configured for this bus")
    
    # Get availability for this date
    booked_seats = (
        db.query(SeatAvailability)
        .filter(
            SeatAvailability.schedule_id == schedule_id,
            SeatAvailability.travel_date == date,
        )
        .all()
    )
    
    booked_map = {sa.seat_number: sa for sa in booked_seats}
    
    # Build response
    seat_data = []
    for seat in seats:
        availability = booked_map.get(seat.seat_number)
        seat_info = {
            "seat_number": seat.seat_number,
            "row_number": seat.row_number,
            "column_number": seat.column_number,
            "seat_type": seat.seat_type.value,
            "deck": seat.deck.value,
            "is_window": seat.is_window,
            "is_aisle": seat.is_aisle,
            "is_ladies_only": seat.is_ladies_only,
            "price_multiplier": seat.price_multiplier,
            "is_available": True,
            "is_booked": False,
            "is_blocked": False,
            "passenger_gender": None,
        }
        
        if availability:
            seat_info["is_booked"] = availability.is_booked
            seat_info["is_blocked"] = availability.is_blocked
            seat_info["is_available"] = not (availability.is_booked or availability.is_blocked)
            seat_info["passenger_gender"] = availability.passenger_gender
        
        seat_data.append(seat_info)
    
    return {
        "bus_id": bus.id,
        "bus_name": bus.name,
        "bus_type": bus.bus_type.name,
        "layout_type": bus.bus_type.seat_layout.value,
        "has_upper_deck": bus.bus_type.has_upper_deck,
        "total_seats": bus.bus_type.total_seats,
        "total_rows": bus.bus_type.total_rows,
        "base_fare": schedule.base_fare,
        "sleeper_fare": schedule.sleeper_fare,
        "seats": seat_data,
    }


@router.get("/{bus_id}/track", response_model=BusLocationResponse)
def track_bus(bus_id: int, db: Session = Depends(get_db)):
    """
    Get live location of a bus (simulated for prototype).
    In production, this would read from GPS device data.
    """
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail="Bus not found")
    
    # Simulate GPS movement
    # Generate mock coordinates along a route
    base_lat = bus.current_latitude or 12.9716  # Default: Bangalore
    base_lng = bus.current_longitude or 77.5946
    
    # Add small random movement to simulate travel
    lat_offset = random.uniform(-0.01, 0.01)
    lng_offset = random.uniform(-0.01, 0.01)
    
    new_lat = base_lat + lat_offset
    new_lng = base_lng + lng_offset
    
    # Update bus location
    bus.current_latitude = new_lat
    bus.current_longitude = new_lng
    bus.last_location_update = datetime.now(timezone.utc).isoformat()
    db.commit()
    
    return BusLocationResponse(
        bus_id=bus.id,
        latitude=new_lat,
        longitude=new_lng,
        last_updated=bus.last_location_update,
        speed_kmph=random.uniform(40, 80),
        next_stop="Next Stop",
        eta_minutes=random.randint(15, 120),
    )


@router.get("/types")
def get_bus_types(db: Session = Depends(get_db)):
    """Get all available bus types."""
    types = db.query(BusType).all()
    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category.value,
            "seat_layout": t.seat_layout.value,
            "total_seats": t.total_seats,
            "total_rows": t.total_rows,
            "has_upper_deck": t.has_upper_deck,
            "description": t.description,
        }
        for t in types
    ]
