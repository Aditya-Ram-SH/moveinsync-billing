"""
Seed script to create sample trip data for testing billing.
Run: python seed_trips.py
"""
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.db.session import SessionLocal
from app.models import Trip, Contract, Employee


def seed_trips():
    """Create sample trips for November 2025."""
    db = SessionLocal()
    
    try:
        print("🚗 Starting trip data seeding...")
        
        # Get all active contracts
        contracts = db.query(Contract).filter(Contract.is_active == True).all()
        
        if not contracts:
            print("❌ No contracts found. Please run seed_data.py first.")
            return
        
        # November 2025 date range
        start_date = datetime(2025, 11, 1, 8, 0, 0)
        end_date = datetime(2025, 11, 30, 20, 0, 0)
        
        trips_created = 0
        
        for contract in contracts:
            print(f"\n📋 Creating trips for Contract {contract.contract_id} ({contract.model_type})")
            
            # Get employees for this client
            employees = db.query(Employee).filter(
                Employee.client_id == contract.client_id
            ).all()
            
            if not employees:
                print(f"   ⚠️  No employees found for client {contract.client_id}")
                continue
            
            # Create 20-30 trips per contract for November
            num_trips = random.randint(20, 30)
            
            for i in range(num_trips):
                # Random day in November
                day = random.randint(1, 28)  # Avoid edge cases
                
                # Random time - mix of day and night shifts
                is_night_shift = random.random() < 0.2  # 20% night shifts
                if is_night_shift:
                    hour = random.choice([22, 23, 0, 1, 2, 3, 4, 5])
                else:
                    hour = random.choice([7, 8, 9, 17, 18, 19, 20])
                
                minute = random.choice([0, 15, 30, 45])
                
                # Booking time (scheduled)
                booking_time = datetime(2025, 11, day, hour, minute, 0)
                
                # Actual pickup time (with potential delay)
                delay_minutes = random.choice([0, 0, 0, 5, 10, 15, 20, 25, 30])  # Most on time
                start_time = booking_time + timedelta(minutes=delay_minutes)
                
                # Trip duration and distance
                duration_min = random.randint(20, 60)
                distance_km = Decimal(str(random.uniform(5.0, 25.0))).quantize(Decimal('0.01'))
                
                end_time = start_time + timedelta(minutes=duration_min)
                
                # Random employee - ensure we have employees
                if not employees:
                    print(f"   ⚠️  No employees available for contract {contract.contract_id}, skipping trip")
                    continue
                
                employee = random.choice(employees)
                
                # Validate trip dates are within contract period
                trip_date = start_time.date()
                if trip_date < contract.start_date or trip_date > contract.end_date:
                    print(f"   ⚠️  Skipping trip outside contract date range: {trip_date}")
                    continue
                
                # Create trip with all required fields
                vehicle_type = random.choice(["SEDAN", "SUV", "HATCHBACK"])
                vehicle_number = f"KA-{random.randint(10,99)}-{random.choice(['AB','CD','EF'])}-{random.randint(1000,9999)}"
                trip_type = random.choice(["INBOUND", "OUTBOUND"])
                
                trip = Trip(
                    contract_id=contract.contract_id,
                    client_id=contract.client_id,
                    vendor_id=contract.vendor_id,
                    employee_id=employee.employee_id,  # Always set employee_id
                    booking_time=booking_time,
                    vehicle_type=vehicle_type,
                    vehicle_number=vehicle_number,
                    trip_type=trip_type,
                    start_time=start_time,
                    end_time=end_time,
                    distance_km=distance_km,
                    duration_min=duration_min,
                    currency="INR",
                    raw_data={
                        "source": "seed_script",
                        "pickup_location": f"Location_{random.randint(1,10)}",
                        "drop_location": f"Location_{random.randint(1,10)}",
                        "driver_id": f"DRV_{random.randint(100,999)}",
                        "delay_minutes": delay_minutes,
                        "is_night_shift": is_night_shift
                    },
                    status="INGESTED"
                )
                
                db.add(trip)
                trips_created += 1
            
            print(f"   ✅ Created {num_trips} trips")
        
        db.commit()
        
        print("\n" + "="*60)
        print(f"✨ Trip seeding completed successfully!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"   • {trips_created} Trips created for November 2025")
        print(f"   • {len(contracts)} Contracts covered")
        print(f"\n💡 Next steps:")
        print(f"   1. Create billing runs for November 2025:")
        print(f"      - Use billing_month: 2025-11-01 (must be first day of month)")
        print(f"      - Example: Client ID 1, Vendor ID 1, Month: 2025-11")
        print(f"   2. View results in the frontend")
        print(f"\n⚠️  IMPORTANT: Billing month must be 2025-11-01 to process these trips!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during trip seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_trips()

