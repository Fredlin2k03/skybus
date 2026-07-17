"""
Routes router - handles city search, route listing, and schedule queries.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional

from app.database import get_db
from app.models.route import Route, Stop, Schedule, ScheduleStop
from app.models.bus import Bus, BusType, BusAmenity
from app.models.seat import SeatAvailability
from app.models.review import Review
from app.schemas.route import (
    StopResponse, RouteResponse, ScheduleResponse, 
    ScheduleStopResponse, CitySearchResponse, SearchRequest
)
from app.schemas.bus import BusSearchResult, BusResponse, BusTypeResponse, BusAmenityResponse
from app.utils.helpers import get_day_of_week

router = APIRouter(prefix="/api/routes", tags=["Routes & Search"])


@router.get("/cities", response_model=List[CitySearchResponse])
def search_cities(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """
    Autocomplete city search.
    Returns cities matching the query with stop count.
    """
    cities = (
        db.query(
            Stop.city,
            Stop.state,
            func.count(Stop.id).label("stop_count")
        )
        .filter(
            Stop.is_active == True,
            or_(
                Stop.city.ilike(f"%{q}%"),
                Stop.name.ilike(f"%{q}%")
            )
        )
        .group_by(Stop.city, Stop.state)
        .order_by(func.count(Stop.id).desc())
        .limit(10)
        .all()
    )
    
    return [
        CitySearchResponse(city=c.city, state=c.state, stop_count=c.stop_count)
        for c in cities
    ]


@router.get("/popular", response_model=List[RouteResponse])
def get_popular_routes(db: Session = Depends(get_db)):
    """Get popular routes for the homepage."""
    routes = (
        db.query(Route)
        .filter(Route.is_active == True)
        .order_by(Route.id)
        .limit(12)
        .all()
    )
    return [RouteResponse.model_validate(r) for r in routes]


@router.get("/search")
def search_buses(
    source: str = Query(...),
    destination: str = Query(...),
    date: str = Query(...),  # YYYY-MM-DD
    bus_type: Optional[str] = None,
    departure_time: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    sort_by: Optional[str] = "departure",  # departure, price, duration, rating
    db: Session = Depends(get_db)
):
    """
    Search for available buses between two cities on a given date.
    Returns list of matching schedules with availability info.
    """
    # Find routes matching source and destination
    routes = (
        db.query(Route)
        .filter(
            Route.is_active == True,
            func.lower(Route.source_city) == source.lower(),
            func.lower(Route.destination_city) == destination.lower()
        )
        .all()
    )
    
    if not routes:
        return []
    
    route_ids = [r.id for r in routes]
    day_of_week = get_day_of_week(date)
    
    # Get schedules for these routes
    query = (
        db.query(Schedule)
        .options(
            joinedload(Schedule.bus).joinedload(Bus.bus_type),
            joinedload(Schedule.bus).joinedload(Bus.amenities),
            joinedload(Schedule.route),
        )
        .filter(
            Schedule.route_id.in_(route_ids),
            Schedule.is_active == True,
            Schedule.days_of_operation.contains(day_of_week)
        )
    )
    
    schedules = query.all()
    
    results = []
    for schedule in schedules:
        bus = schedule.bus
        bus_type_obj = bus.bus_type
        
        # Apply filters
        if bus_type and bus_type_obj.category.value != bus_type:
            continue
        
        if price_min and schedule.base_fare < price_min:
            continue
        if price_max and schedule.base_fare > price_max:
            continue
        
        # Apply departure time filter
        if departure_time:
            hour = int(schedule.departure_time.split(":")[0])
            if departure_time == "morning" and not (6 <= hour < 12):
                continue
            elif departure_time == "afternoon" and not (12 <= hour < 17):
                continue
            elif departure_time == "evening" and not (17 <= hour < 21):
                continue
            elif departure_time == "night" and not (hour >= 21 or hour < 6):
                continue
        
        # Count available seats
        booked_seats = (
            db.query(func.count(SeatAvailability.id))
            .filter(
                SeatAvailability.schedule_id == schedule.id,
                SeatAvailability.travel_date == date,
                SeatAvailability.is_booked == True
            )
            .scalar()
        )
        
        total_seats = bus_type_obj.total_seats
        available_seats = total_seats - (booked_seats or 0)
        
        # Get average rating
        avg_rating = (
            db.query(func.avg(Review.overall_rating))
            .filter(Review.schedule_id == schedule.id)
            .scalar()
        )
        
        total_reviews = (
            db.query(func.count(Review.id))
            .filter(Review.schedule_id == schedule.id)
            .scalar()
        )
        
        result = {
            "schedule_id": schedule.id,
            "bus": {
                "id": bus.id,
                "registration_number": bus.registration_number,
                "name": bus.name,
                "bus_type": {
                    "id": bus_type_obj.id,
                    "name": bus_type_obj.name,
                    "category": bus_type_obj.category.value,
                    "seat_layout": bus_type_obj.seat_layout.value,
                    "total_seats": bus_type_obj.total_seats,
                    "total_rows": bus_type_obj.total_rows,
                    "has_upper_deck": bus_type_obj.has_upper_deck,
                    "description": bus_type_obj.description,
                },
                "amenities": [
                    {"id": a.id, "name": a.name, "icon": a.icon, "description": a.description}
                    for a in bus.amenities
                ],
                "is_active": bus.is_active,
                "manufacturing_year": bus.manufacturing_year,
            },
            "route_name": schedule.route.name,
            "source_city": schedule.route.source_city,
            "destination_city": schedule.route.destination_city,
            "departure_time": schedule.departure_time,
            "arrival_time": schedule.arrival_time,
            "duration_minutes": schedule.duration_minutes,
            "base_fare": schedule.base_fare,
            "sleeper_fare": schedule.sleeper_fare,
            "available_seats": available_seats,
            "total_seats": total_seats,
            "amenities": [a.name for a in bus.amenities],
            "rating": round(avg_rating, 1) if avg_rating else None,
            "total_reviews": total_reviews or 0,
        }
        results.append(result)
    
    # Sort results
    if sort_by == "price":
        results.sort(key=lambda x: x["base_fare"])
    elif sort_by == "duration":
        results.sort(key=lambda x: x["duration_minutes"])
    elif sort_by == "rating":
        results.sort(key=lambda x: x["rating"] or 0, reverse=True)
    else:  # departure
        results.sort(key=lambda x: x["departure_time"])
    
    return results


@router.get("/schedule/{schedule_id}/stops", response_model=List[ScheduleStopResponse])
def get_schedule_stops(schedule_id: int, db: Session = Depends(get_db)):
    """Get all stops for a specific schedule."""
    stops = (
        db.query(ScheduleStop)
        .options(joinedload(ScheduleStop.stop))
        .filter(ScheduleStop.schedule_id == schedule_id)
        .order_by(ScheduleStop.sequence)
        .all()
    )
    
    if not stops:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return [
        ScheduleStopResponse(
            stop=StopResponse.model_validate(s.stop),
            sequence=s.sequence,
            arrival_offset_minutes=s.arrival_offset_minutes,
            departure_offset_minutes=s.departure_offset_minutes,
            fare_from_origin=s.fare_from_origin,
            is_boarding_point=s.is_boarding_point,
            is_dropping_point=s.is_dropping_point,
        )
        for s in stops
    ]


@router.get("/stops/{city}")
def get_city_stops(city: str, db: Session = Depends(get_db)):
    """Get all boarding/dropping points in a city."""
    stops = (
        db.query(Stop)
        .filter(func.lower(Stop.city) == city.lower(), Stop.is_active == True)
        .all()
    )
    return [StopResponse.model_validate(s) for s in stops]
