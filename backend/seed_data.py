"""
Seed Data Script for SkyBus
Populates the database with sample data for testing and development.
Run: python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal, Base
from app.models import *
from app.middleware.auth import hash_password
from datetime import datetime, timezone


def seed():
    """Seed the database with sample data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return
        
        print("🚌 Seeding SkyBus database...")
        
        # ===== USERS =====
        print("  Creating users...")
        admin_user = User(
            email="admin@skybus.in",
            phone="9999999999",
            password_hash=hash_password("admin123"),
            full_name="SkyBus Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            email_verified=True,
            phone_verified=True,
        )
        
        test_user = User(
            email="test@example.com",
            phone="9876543210",
            password_hash=hash_password("test123"),
            full_name="Rahul Sharma",
            gender="male",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True,
            email_verified=True,
        )
        
        test_user2 = User(
            email="priya@example.com",
            phone="9876543211",
            password_hash=hash_password("test123"),
            full_name="Priya Patel",
            gender="female",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True,
            email_verified=True,
        )
        
        db.add_all([admin_user, test_user, test_user2])
        db.flush()
        
        # ===== AMENITIES =====
        print("  Creating amenities...")
        amenities_data = [
            ("WiFi", "wifi", "Free high-speed WiFi onboard"),
            ("Charging Point", "charging", "USB and power socket at every seat"),
            ("Blanket", "blanket", "Clean blanket provided"),
            ("Water Bottle", "water", "Complimentary water bottle"),
            ("Entertainment", "entertainment", "Personal entertainment screen"),
            ("GPS Tracking", "gps", "Real-time GPS tracking"),
            ("Reading Light", "light", "Individual reading light"),
            ("Air Conditioning", "ac", "Fully air-conditioned"),
            ("Snacks", "snacks", "Complimentary snacks"),
            ("Emergency Exit", "emergency", "Marked emergency exits"),
        ]
        
        amenities = []
        for name, icon, desc in amenities_data:
            amenity = BusAmenity(name=name, icon=icon, description=desc)
            amenities.append(amenity)
        
        db.add_all(amenities)
        db.flush()
        
        # ===== BUS TYPES =====
        print("  Creating bus types...")
        bus_types_data = [
            {
                "name": "SkyBus Platinum (AC Sleeper)",
                "category": BusCategory.AC_SLEEPER,
                "seat_layout": SeatLayoutType.SLEEPER_2X1,
                "total_seats": 30,
                "total_rows": 10,
                "has_upper_deck": True,
                "description": "Premium AC Sleeper with 2+1 layout, upper and lower berths",
            },
            {
                "name": "SkyBus Gold (AC Seater)",
                "category": BusCategory.AC_SEATER,
                "seat_layout": SeatLayoutType.SEATER_2X2,
                "total_seats": 40,
                "total_rows": 10,
                "has_upper_deck": False,
                "description": "Comfortable AC Seater with pushback seats",
            },
            {
                "name": "SkyBus Silver (Non-AC Sleeper)",
                "category": BusCategory.NON_AC_SLEEPER,
                "seat_layout": SeatLayoutType.SLEEPER_2X1,
                "total_seats": 30,
                "total_rows": 10,
                "has_upper_deck": True,
                "description": "Budget-friendly sleeper bus",
            },
            {
                "name": "SkyBus Economy (Non-AC Seater)",
                "category": BusCategory.NON_AC_SEATER,
                "seat_layout": SeatLayoutType.SEATER_2X2,
                "total_seats": 45,
                "total_rows": 12,
                "has_upper_deck": False,
                "description": "Affordable seater for short routes",
            },
            {
                "name": "SkyBus Imperial (Volvo Multi-Axle)",
                "category": BusCategory.VOLVO_MULTI_AXLE,
                "seat_layout": SeatLayoutType.SEMI_SLEEPER_2X2,
                "total_seats": 36,
                "total_rows": 9,
                "has_upper_deck": False,
                "description": "Luxury Volvo Multi-Axle with semi-sleeper seats",
            },
        ]
        
        bus_types = []
        for bt_data in bus_types_data:
            bt = BusType(**bt_data)
            bus_types.append(bt)
        
        db.add_all(bus_types)
        db.flush()
        
        # ===== BUSES =====
        print("  Creating buses...")
        buses_data = [
            ("KA01AB1234", bus_types[0].id, "SkyBus Platinum Express", 2022, [0, 1, 2, 3, 5, 7]),
            ("KA01CD5678", bus_types[1].id, "SkyBus Gold Comfort", 2023, [0, 1, 4, 5, 7]),
            ("MH01EF9012", bus_types[2].id, "SkyBus Silver Night", 2021, [1, 5, 9]),
            ("TN01GH3456", bus_types[3].id, "SkyBus Economy Plus", 2022, [1, 5, 9]),
            ("KA01IJ7890", bus_types[4].id, "SkyBus Imperial Volvo", 2023, [0, 1, 2, 3, 4, 5, 6, 7, 8]),
            ("MH02KL1234", bus_types[0].id, "SkyBus Platinum Night", 2023, [0, 1, 2, 3, 5, 7]),
            ("AP01MN5678", bus_types[1].id, "SkyBus Gold Express", 2022, [0, 1, 4, 5, 7]),
            ("TN02OP9012", bus_types[4].id, "SkyBus Imperial Plus", 2024, [0, 1, 2, 3, 4, 5, 6, 7, 8]),
            ("RJ01QR3456", bus_types[1].id, "SkyBus Gold Royal", 2023, [0, 1, 4, 5, 7]),
            ("KA03ST7890", bus_types[2].id, "SkyBus Silver Express", 2022, [1, 5, 9]),
        ]
        
        buses = []
        for reg, type_id, name, year, amenity_indices in buses_data:
            bus = Bus(
                registration_number=reg,
                bus_type_id=type_id,
                name=name,
                manufacturing_year=year,
                is_active=True,
                current_latitude=12.9716,
                current_longitude=77.5946,
            )
            bus.amenities = [amenities[i] for i in amenity_indices]
            buses.append(bus)
        
        db.add_all(buses)
        db.flush()
        
        # ===== SEAT LAYOUTS =====
        print("  Creating seat layouts...")
        
        def create_seater_2x2(bus_id, total_rows, total_seats):
            """Create a 2+2 seater layout."""
            seats = []
            seat_num = 1
            for row in range(1, total_rows + 1):
                for col in range(1, 5):  # 4 seats per row
                    if seat_num > total_seats:
                        break
                    is_window = col in [1, 4]
                    is_aisle = col in [2, 3]
                    seat = SeatLayout(
                        bus_id=bus_id,
                        seat_number=f"{row}{chr(64+col)}",  # 1A, 1B, 1C, 1D
                        row_number=row,
                        column_number=col,
                        seat_type=SeatType.SEATER,
                        deck=DeckType.LOWER,
                        is_window=is_window,
                        is_aisle=is_aisle,
                        price_multiplier=1.1 if is_window else 1.0,
                        is_available=True,
                    )
                    seats.append(seat)
                    seat_num += 1
            return seats
        
        def create_sleeper_2x1(bus_id, total_rows):
            """Create a 2+1 sleeper layout with upper and lower."""
            seats = []
            for deck_type, deck_label in [(DeckType.LOWER, "L"), (DeckType.UPPER, "U")]:
                for row in range(1, total_rows + 1):
                    # Left side: 2 berths (A, B)
                    for col in range(1, 3):
                        seat = SeatLayout(
                            bus_id=bus_id,
                            seat_number=f"{deck_label}{row}{chr(64+col)}",
                            row_number=row,
                            column_number=col,
                            seat_type=SeatType.SLEEPER,
                            deck=deck_type,
                            is_window=(col == 1),
                            is_aisle=(col == 2),
                            price_multiplier=1.2 if deck_type == DeckType.LOWER else 1.0,
                            is_available=True,
                        )
                        seats.append(seat)
                    # Right side: 1 berth (C)
                    seat = SeatLayout(
                        bus_id=bus_id,
                        seat_number=f"{deck_label}{row}C",
                        row_number=row,
                        column_number=4,
                        seat_type=SeatType.SLEEPER,
                        deck=deck_type,
                        is_window=True,
                        is_aisle=False,
                        price_multiplier=1.3 if deck_type == DeckType.LOWER else 1.1,
                        is_available=True,
                    )
                    seats.append(seat)
            return seats
        
        def create_semi_sleeper_2x2(bus_id, total_rows, total_seats):
            """Create a 2+2 semi-sleeper layout."""
            seats = []
            seat_num = 1
            for row in range(1, total_rows + 1):
                for col in range(1, 5):
                    if seat_num > total_seats:
                        break
                    is_window = col in [1, 4]
                    seat = SeatLayout(
                        bus_id=bus_id,
                        seat_number=f"{row}{chr(64+col)}",
                        row_number=row,
                        column_number=col,
                        seat_type=SeatType.SEMI_SLEEPER,
                        deck=DeckType.LOWER,
                        is_window=is_window,
                        is_aisle=col in [2, 3],
                        price_multiplier=1.15 if is_window else 1.0,
                        is_available=True,
                    )
                    seats.append(seat)
                    seat_num += 1
            return seats
        
        all_seats = []
        for bus in buses:
            bt = db.query(BusType).filter(BusType.id == bus.bus_type_id).first()
            if bt.seat_layout == SeatLayoutType.SEATER_2X2:
                all_seats.extend(create_seater_2x2(bus.id, bt.total_rows, bt.total_seats))
            elif bt.seat_layout in [SeatLayoutType.SLEEPER_2X1, SeatLayoutType.SLEEPER_2X1_UPPER_LOWER]:
                all_seats.extend(create_sleeper_2x1(bus.id, bt.total_rows))
            elif bt.seat_layout == SeatLayoutType.SEMI_SLEEPER_2X2:
                all_seats.extend(create_semi_sleeper_2x2(bus.id, bt.total_rows, bt.total_seats))
        
        db.add_all(all_seats)
        db.flush()
        
        # ===== STOPS =====
        print("  Creating stops...")
        stops_data = [
            # Chennai
            ("Koyambedu Bus Terminal", "Chennai", "Tamil Nadu", "Koyambedu", 13.0694, 80.1948),
            ("Chennai CMBT", "Chennai", "Tamil Nadu", "CMBT Main", 13.0686, 80.1920),
            # Bangalore
            ("Majestic Bus Station", "Bangalore", "Karnataka", "Majestic", 12.9772, 77.5721),
            ("Electronic City", "Bangalore", "Karnataka", "Infosys Gate", 12.8458, 77.6692),
            ("Silk Board", "Bangalore", "Karnataka", "Silk Board Junction", 12.9172, 77.6227),
            # Mumbai
            ("Dadar Bus Terminal", "Mumbai", "Maharashtra", "Dadar TT", 19.0178, 72.8478),
            ("Borivali Bus Station", "Mumbai", "Maharashtra", "Borivali East", 19.2307, 72.8567),
            # Pune
            ("Shivajinagar Bus Stand", "Pune", "Maharashtra", "Shivajinagar", 18.5314, 73.8446),
            ("Swargate Bus Stand", "Pune", "Maharashtra", "Swargate", 18.5018, 73.8636),
            # Delhi
            ("Kashmere Gate ISBT", "Delhi", "Delhi", "Kashmere Gate", 28.6674, 77.2289),
            ("Anand Vihar ISBT", "Delhi", "Delhi", "Anand Vihar", 28.6468, 77.3158),
            # Jaipur
            ("Sindhi Camp Bus Stand", "Jaipur", "Rajasthan", "Sindhi Camp", 26.9214, 75.7870),
            ("Narayan Singh Circle", "Jaipur", "Rajasthan", "Narayan Singh", 26.9070, 75.8005),
            # Hyderabad
            ("MGBS Bus Station", "Hyderabad", "Telangana", "Mahatma Gandhi", 17.3784, 78.4866),
            ("JBS Jubilee", "Hyderabad", "Telangana", "Jubilee Bus Station", 17.4533, 78.4989),
            # Vizag (Visakhapatnam)
            ("RTC Complex Vizag", "Visakhapatnam", "Andhra Pradesh", "RTC Complex", 17.7215, 83.3013),
            # Goa
            ("Kadamba Bus Stand", "Goa", "Goa", "Panaji", 15.4989, 73.8278),
            # Coimbatore
            ("Gandhipuram Bus Stand", "Coimbatore", "Tamil Nadu", "Gandhipuram", 11.0168, 76.9558),
            # Mysore
            ("Mysore Bus Stand", "Mysore", "Karnataka", "Central Bus Stand", 12.2958, 76.6394),
            # Ahmedabad
            ("Paldi Bus Stand", "Ahmedabad", "Gujarat", "Paldi", 23.0225, 72.5714),
        ]
        
        stops = []
        for name, city, state, landmark, lat, lng in stops_data:
            stop = Stop(
                name=name, city=city, state=state,
                landmark=landmark, latitude=lat, longitude=lng,
                is_active=True, stop_type="terminal"
            )
            stops.append(stop)
        
        db.add_all(stops)
        db.flush()
        
        # ===== ROUTES =====
        print("  Creating routes...")
        routes_data = [
            ("Chennai - Bangalore", "Chennai", "Bangalore", 350, 360),
            ("Bangalore - Chennai", "Bangalore", "Chennai", 350, 360),
            ("Mumbai - Pune", "Mumbai", "Pune", 150, 180),
            ("Pune - Mumbai", "Pune", "Mumbai", 150, 180),
            ("Delhi - Jaipur", "Delhi", "Jaipur", 280, 300),
            ("Jaipur - Delhi", "Jaipur", "Delhi", 280, 300),
            ("Hyderabad - Visakhapatnam", "Hyderabad", "Visakhapatnam", 620, 660),
            ("Visakhapatnam - Hyderabad", "Visakhapatnam", "Hyderabad", 620, 660),
            ("Bangalore - Goa", "Bangalore", "Goa", 560, 600),
            ("Mumbai - Goa", "Mumbai", "Goa", 590, 630),
            ("Chennai - Coimbatore", "Chennai", "Coimbatore", 500, 480),
            ("Bangalore - Mysore", "Bangalore", "Mysore", 150, 180),
            ("Mumbai - Ahmedabad", "Mumbai", "Ahmedabad", 530, 540),
            ("Hyderabad - Bangalore", "Hyderabad", "Bangalore", 570, 600),
        ]
        
        routes = []
        for name, src, dst, dist, duration in routes_data:
            route = Route(
                name=name, source_city=src, destination_city=dst,
                distance_km=dist, estimated_duration_minutes=duration,
                is_active=True
            )
            routes.append(route)
        
        db.add_all(routes)
        db.flush()
        
        # ===== SCHEDULES =====
        print("  Creating schedules...")
        schedules_data = [
            # Chennai - Bangalore (multiple departures)
            (routes[0].id, buses[0].id, "21:00", "03:00", 360, 899, 1199),
            (routes[0].id, buses[1].id, "22:30", "04:30", 360, 699, None),
            (routes[0].id, buses[4].id, "23:00", "05:00", 360, 999, None),
            (routes[0].id, buses[3].id, "20:00", "02:00", 360, 499, None),
            # Bangalore - Chennai
            (routes[1].id, buses[0].id, "21:30", "03:30", 360, 899, 1199),
            (routes[1].id, buses[1].id, "22:00", "04:00", 360, 699, None),
            # Mumbai - Pune (multiple)
            (routes[2].id, buses[1].id, "06:00", "09:00", 180, 399, None),
            (routes[2].id, buses[4].id, "08:00", "11:00", 180, 599, None),
            (routes[2].id, buses[3].id, "10:00", "13:00", 180, 299, None),
            (routes[2].id, buses[1].id, "14:00", "17:00", 180, 399, None),
            # Pune - Mumbai
            (routes[3].id, buses[1].id, "07:00", "10:00", 180, 399, None),
            (routes[3].id, buses[4].id, "16:00", "19:00", 180, 599, None),
            # Delhi - Jaipur
            (routes[4].id, buses[4].id, "06:00", "11:00", 300, 799, None),
            (routes[4].id, buses[8].id, "22:00", "03:00", 300, 599, None),
            (routes[4].id, buses[5].id, "23:00", "04:00", 300, 999, 1299),
            # Jaipur - Delhi
            (routes[5].id, buses[4].id, "06:00", "11:00", 300, 799, None),
            (routes[5].id, buses[8].id, "22:00", "03:00", 300, 599, None),
            # Hyderabad - Vizag
            (routes[6].id, buses[0].id, "19:00", "06:00", 660, 1099, 1499),
            (routes[6].id, buses[5].id, "20:00", "07:00", 660, 1199, 1599),
            (routes[6].id, buses[2].id, "21:00", "08:00", 660, 799, 999),
            # Vizag - Hyderabad
            (routes[7].id, buses[0].id, "19:00", "06:00", 660, 1099, 1499),
            # Bangalore - Goa
            (routes[8].id, buses[4].id, "20:00", "06:00", 600, 1199, None),
            (routes[8].id, buses[0].id, "21:00", "07:00", 600, 1399, 1799),
            # Mumbai - Goa
            (routes[9].id, buses[4].id, "19:00", "05:30", 630, 1099, None),
            (routes[9].id, buses[5].id, "21:00", "07:30", 630, 1299, 1699),
            # Chennai - Coimbatore
            (routes[10].id, buses[1].id, "22:00", "06:00", 480, 599, None),
            (routes[10].id, buses[7].id, "23:00", "07:00", 480, 799, None),
            # Bangalore - Mysore
            (routes[11].id, buses[1].id, "06:00", "09:00", 180, 349, None),
            (routes[11].id, buses[3].id, "08:00", "11:00", 180, 249, None),
            (routes[11].id, buses[4].id, "10:00", "13:00", 180, 499, None),
            # Mumbai - Ahmedabad
            (routes[12].id, buses[4].id, "20:00", "05:00", 540, 999, None),
            (routes[12].id, buses[5].id, "22:00", "07:00", 540, 1299, 1699),
            # Hyderabad - Bangalore
            (routes[13].id, buses[4].id, "20:00", "06:00", 600, 999, None),
            (routes[13].id, buses[0].id, "21:00", "07:00", 600, 1199, 1599),
            (routes[13].id, buses[6].id, "22:00", "08:00", 600, 799, None),
        ]
        
        schedules = []
        for route_id, bus_id, dep, arr, duration, base_fare, sleeper_fare in schedules_data:
            schedule = Schedule(
                route_id=route_id,
                bus_id=bus_id,
                departure_time=dep,
                arrival_time=arr,
                duration_minutes=duration,
                days_of_operation="Mon,Tue,Wed,Thu,Fri,Sat,Sun",
                base_fare=base_fare,
                sleeper_fare=sleeper_fare,
                is_active=True,
            )
            schedules.append(schedule)
        
        db.add_all(schedules)
        db.flush()
        
        # ===== SCHEDULE STOPS (sample for first few schedules) =====
        print("  Creating schedule stops...")
        # Chennai - Bangalore via Electronic City
        for sched in schedules[:4]:  # First 4 Chennai-Bangalore schedules
            ss1 = ScheduleStop(
                schedule_id=sched.id, stop_id=stops[0].id,  # Koyambedu
                sequence=1, arrival_offset_minutes=0, departure_offset_minutes=0,
                fare_from_origin=0, is_boarding_point=True, is_dropping_point=False
            )
            ss2 = ScheduleStop(
                schedule_id=sched.id, stop_id=stops[1].id,  # CMBT
                sequence=2, arrival_offset_minutes=15, departure_offset_minutes=20,
                fare_from_origin=0, is_boarding_point=True, is_dropping_point=False
            )
            ss3 = ScheduleStop(
                schedule_id=sched.id, stop_id=stops[3].id,  # Electronic City
                sequence=3, arrival_offset_minutes=300, departure_offset_minutes=305,
                fare_from_origin=sched.base_fare * 0.8, is_boarding_point=False, is_dropping_point=True
            )
            ss4 = ScheduleStop(
                schedule_id=sched.id, stop_id=stops[4].id,  # Silk Board
                sequence=4, arrival_offset_minutes=330, departure_offset_minutes=335,
                fare_from_origin=sched.base_fare * 0.9, is_boarding_point=False, is_dropping_point=True
            )
            ss5 = ScheduleStop(
                schedule_id=sched.id, stop_id=stops[2].id,  # Majestic
                sequence=5, arrival_offset_minutes=360, departure_offset_minutes=360,
                fare_from_origin=sched.base_fare, is_boarding_point=False, is_dropping_point=True
            )
            db.add_all([ss1, ss2, ss3, ss4, ss5])
        
        # ===== COUPONS =====
        print("  Creating coupons...")
        coupons_data = [
            {
                "code": "WELCOME50",
                "description": "50% off on your first booking (max ₹200)",
                "discount_type": "percentage",
                "discount_value": 50,
                "max_discount": 200,
                "min_booking_amount": 300,
                "max_uses": 1000,
                "max_uses_per_user": 1,
                "valid_from": "2024-01-01",
                "valid_until": "2027-12-31",
                "first_booking_only": True,
            },
            {
                "code": "SKYBUS100",
                "description": "Flat ₹100 off on bookings above ₹500",
                "discount_type": "flat",
                "discount_value": 100,
                "max_discount": None,
                "min_booking_amount": 500,
                "max_uses": 5000,
                "max_uses_per_user": 3,
                "valid_from": "2024-01-01",
                "valid_until": "2027-12-31",
                "first_booking_only": False,
            },
            {
                "code": "SUMMER25",
                "description": "25% off on all summer travel (max ₹300)",
                "discount_type": "percentage",
                "discount_value": 25,
                "max_discount": 300,
                "min_booking_amount": 400,
                "max_uses": 2000,
                "max_uses_per_user": 2,
                "valid_from": "2024-03-01",
                "valid_until": "2027-09-30",
                "first_booking_only": False,
            },
            {
                "code": "VOLVO200",
                "description": "₹200 off on Volvo Multi-Axle buses",
                "discount_type": "flat",
                "discount_value": 200,
                "max_discount": None,
                "min_booking_amount": 800,
                "max_uses": 1000,
                "max_uses_per_user": 2,
                "valid_from": "2024-01-01",
                "valid_until": "2027-12-31",
                "first_booking_only": False,
            },
            {
                "code": "FLAT150",
                "description": "Flat ₹150 off on any booking above ₹600",
                "discount_type": "flat",
                "discount_value": 150,
                "max_discount": None,
                "min_booking_amount": 600,
                "max_uses": 3000,
                "max_uses_per_user": 5,
                "valid_from": "2024-01-01",
                "valid_until": "2027-12-31",
                "first_booking_only": False,
            },
        ]
        
        for c_data in coupons_data:
            coupon = Coupon(**c_data)
            db.add(coupon)
        
        # ===== COMMIT ALL =====
        db.commit()
        print("\n✅ Database seeded successfully!")
        print(f"   - {len(stops)} stops created")
        print(f"   - {len(routes)} routes created")
        print(f"   - {len(buses)} buses created")
        print(f"   - {len(schedules)} schedules created")
        print(f"   - {len(amenities_data)} amenities created")
        print(f"   - {len(coupons_data)} coupons created")
        print(f"\n📧 Admin: admin@skybus.in / admin123")
        print(f"📧 Test User: test@example.com / test123")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
