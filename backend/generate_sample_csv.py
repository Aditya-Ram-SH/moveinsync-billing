"""
Generate a sample CSV file with trip data based on actual contracts in the database.
Run: python generate_sample_csv.py
"""
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models import Contract, Employee

def generate_sample_csv():
    """Generate sample CSV with trips for existing contracts."""
    db = SessionLocal()
    
    try:
        print("📋 Generating sample trip CSV...")
        
        # Get all active contracts
        contracts = db.query(Contract).filter(Contract.is_active == True).limit(4).all()
        
        if not contracts:
            print("❌ No active contracts found. Please create contracts first.")
            return
        
        print(f"✅ Found {len(contracts)} active contracts")
        
        # Generate CSV content
        csv_lines = [
            "contract_id,client_id,vendor_id,employee_id,trip_type,booking_time,start_time,end_time,distance_km,duration_min,vehicle_type,vehicle_number,currency"
        ]
        
        for contract in contracts:
            # Get employees for this client
            employees = db.query(Employee).filter(
                Employee.client_id == contract.client_id
            ).all()
            
            if not employees:
                print(f"⚠️  No employees found for client {contract.client_id}, skipping contract {contract.contract_id}")
                continue
            
            # Generate 2-3 sample trips per contract
            num_trips = min(3, len(employees))  # Generate trips for available employees
            for i in range(num_trips):
                # Use November 2025 dates
                day = 15 + i
                hour = 8 if i == 0 else 18
                
                booking_time = datetime(2025, 11, day, hour, 0, 0)
                start_time = booking_time + timedelta(minutes=5)
                end_time = start_time + timedelta(minutes=40 + (i * 10))
                
                # Use employee from database, cycling through available employees
                employee = employees[i % len(employees)]
                trip_type = "INBOUND" if i == 0 else "OUTBOUND"
                distance = 15.5 + (i * 5)
                duration = 40 + (i * 10)
                vehicle_type = ["SEDAN", "SUV", "HATCHBACK"][i % 3]
                vehicle_number = f"KA-{10+i*2}-AB-{1000+i*100}"
                
                csv_lines.append(
                    f"{contract.contract_id},"
                    f"{contract.client_id},"
                    f"{contract.vendor_id},"
                    f"{employee.employee_id},"
                    f"{trip_type},"
                    f"{booking_time.isoformat()},"
                    f"{start_time.isoformat()},"
                    f"{end_time.isoformat()},"
                    f"{distance},"
                    f"{duration},"
                    f"{vehicle_type},"
                    f"{vehicle_number},"
                    f"INR"
                )
        
        # Write to file
        csv_content = "\n".join(csv_lines)
        import os
        # Write to sample directory if it exists, otherwise to backend directory
        sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample")
        if os.path.exists(sample_dir):
            file_path = os.path.join(sample_dir, "sample_trips.csv")
        else:
            file_path = os.path.join(os.path.dirname(__file__), "sample_trips.csv")
        
        with open(file_path, "w") as f:
            f.write(csv_content)
        
        print(f"\n✅ Generated sample_trips.csv with {len(csv_lines) - 1} trips")
        print(f"\n📁 File location: {file_path}")
        print(f"\n💡 You can now upload this file via the frontend!")
        print(f"\n📋 Sample trips created for contracts: {[c.contract_id for c in contracts]}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    generate_sample_csv()

