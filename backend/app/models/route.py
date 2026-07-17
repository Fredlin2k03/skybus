"""
Route models - Routes, Stops, and Schedules.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Stop(Base):
    """Bus stops/stations in the SkyBus network."""

    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    address = Column(String(500), nullable=True)
    landmark = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    stop_type = Column(String(50), default="regular")  # terminal, regular, pickup, drop

    def __repr__(self):
        return f"<Stop(id={self.id}, name={self.name}, city={self.city})>"


class Route(Base):
    """Routes connecting two cities with intermediate stops."""

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # e.g., "Chennai - Bangalore"
    source_city = Column(String(100), nullable=False, index=True)
    destination_city = Column(String(100), nullable=False, index=True)
    distance_km = Column(Float, nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="route")

    def __repr__(self):
        return f"<Route(id={self.id}, name={self.name})>"


class Schedule(Base):
    """Bus schedules - which bus runs on which route at what time."""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False)
    bus_id = Column(Integer, ForeignKey("buses.id"), nullable=False)
    
    # Timing
    departure_time = Column(String(5), nullable=False)  # "HH:MM" format
    arrival_time = Column(String(5), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Days of operation (JSON-like string of days: "Mon,Tue,Wed,Thu,Fri,Sat,Sun")
    days_of_operation = Column(String(100), default="Mon,Tue,Wed,Thu,Fri,Sat,Sun")
    
    # Pricing (base fare, can vary by seat type)
    base_fare = Column(Float, nullable=False)
    sleeper_fare = Column(Float, nullable=True)  # If bus has sleeper seats
    
    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(String(10), nullable=True)  # "YYYY-MM-DD"
    effective_until = Column(String(10), nullable=True)
    
    # Relationships
    route = relationship("Route", back_populates="schedules")
    bus = relationship("Bus", back_populates="schedules")
    stops = relationship("ScheduleStop", back_populates="schedule", order_by="ScheduleStop.sequence")
    bookings = relationship("Booking", back_populates="schedule")
    seat_availability = relationship("SeatAvailability", back_populates="schedule")

    def __repr__(self):
        return f"<Schedule(id={self.id}, route_id={self.route_id}, dep={self.departure_time})>"


class ScheduleStop(Base):
    """Intermediate stops for a schedule with timing and fare info."""

    __tablename__ = "schedule_stops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    stop_id = Column(Integer, ForeignKey("stops.id"), nullable=False)
    sequence = Column(Integer, nullable=False)  # Order of stop
    
    # Timing relative to departure
    arrival_offset_minutes = Column(Integer, nullable=False)  # Minutes from departure
    departure_offset_minutes = Column(Integer, nullable=False)
    
    # Fare from origin to this stop
    fare_from_origin = Column(Float, nullable=False)
    
    # Stop type in this schedule
    is_boarding_point = Column(Boolean, default=True)
    is_dropping_point = Column(Boolean, default=True)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="stops")
    stop = relationship("Stop")

    def __repr__(self):
        return f"<ScheduleStop(schedule={self.schedule_id}, stop={self.stop_id}, seq={self.sequence})>"
