"""
Seed script to populate the database with test data.
Run: python seed_data.py
"""
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import Client, Vendor, Employee, User, Contract
from app.core.security import get_password_hash


def seed_database():
    """Populate database with comprehensive test data."""
    db = SessionLocal()
    
    try:
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # Base.metadata.drop_all(bind=engine)
        # Base.metadata.create_all(bind=engine)
        
        # 1. CREATE CLIENTS
        print("\n📊 Creating Clients...")
        clients = []
        client_names = ["TechCorp Solutions", "Global Industries", "MegaRetail Inc"]
        
        for name in client_names:
            client = Client(
                name=name,
                timezone="Asia/Kolkata",
                status="ACTIVE"
            )
            db.add(client)
            clients.append(client)
        
        db.flush()  # Get IDs
        print(f"✅ Created {len(clients)} clients")
        
        # 2. CREATE VENDORS
        print("\n🚐 Creating Vendors...")
        vendors = []
        vendor_data = [
            ("SpeedyRides Transport", "contact@speedyrides.com, +91-9876543210"),
            ("SafeTravel Logistics", "info@safetravel.com, +91-9876543211"),
            ("QuickMove Services", "support@quickmove.com, +91-9876543212"),
            ("EliteFleet Solutions", "hello@elitefleet.com, +91-9876543213")
        ]
        
        for name, contact in vendor_data:
            vendor = Vendor(
                name=name,
                contact_info=contact,
                status="ACTIVE"
            )
            db.add(vendor)
            vendors.append(vendor)
        
        db.flush()
        print(f"✅ Created {len(vendors)} vendors")
        
        # 3. CREATE EMPLOYEES (5 per client)
        print("\n👥 Creating Employees...")
        employees = []
        employee_count = 0
        
        for idx, client in enumerate(clients):
            for emp_num in range(1, 6):
                employee = Employee(
                    client_id=client.client_id,
                    full_name=f"Employee {emp_num} - {client.name[:10]}",
                    email=f"emp{emp_num}.client{idx+1}@company.com",
                    phone=f"+91-98765432{idx}{emp_num}"
                )
                db.add(employee)
                employees.append(employee)
                employee_count += 1
        
        db.flush()
        print(f"✅ Created {employee_count} employees")
        
        # 4. CREATE USERS (Admin, Client users, Vendor users, Employee users)
        print("\n🔐 Creating Users...")
        users = []
        
        # Admin user (already exists, so skip if present)
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if not existing_admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="ADMIN"
            )
            db.add(admin)
            users.append(admin)
        
        # Client users (1 per client)
        for idx, client in enumerate(clients):
            client_user = User(
                username=f"client{idx+1}",
                password_hash=get_password_hash("client123"),
                role="CLIENT",
                client_id=client.client_id
            )
            db.add(client_user)
            users.append(client_user)
        
        # Vendor users (1 per vendor)
        for idx, vendor in enumerate(vendors):
            vendor_user = User(
                username=f"vendor{idx+1}",
                password_hash=get_password_hash("vendor123"),
                role="VENDOR",
                vendor_id=vendor.vendor_id
            )
            db.add(vendor_user)
            users.append(vendor_user)
        
        # Employee users (select a few employees to have login access)
        for idx in [0, 5, 10]:  # First employee from each client
            emp = employees[idx]
            emp_user = User(
                username=f"emp{idx+1}",
                password_hash=get_password_hash("emp123"),
                role="EMPLOYEE",
                client_id=emp.client_id,
                employee_id=emp.employee_id
            )
            db.add(emp_user)
            users.append(emp_user)
        
        db.flush()
        print(f"✅ Created {len(users)} users")
        
        # 5. CREATE CONTRACTS (Different models for testing)
        print("\n📝 Creating Contracts...")
        contracts = []
        admin_user = db.query(User).filter(User.role == "ADMIN").first()
        
        # Contract 1: Client 1 + Vendor 1 → PACKAGE Model
        contract1 = Contract(
            client_id=clients[0].client_id,
            vendor_id=vendors[0].vendor_id,
            model_type="PACKAGE",
            config_json={
                "billing_cycle_months": 1,
                "monthly_fixed_pay": 50000.00,
                "limits": {
                    "included_km": 5000,
                    "included_trips": 500
                },
                "vendor_payouts": {
                    "per_extra_km": 15.00,
                    "per_extra_trip": 200.00,
                    "night_shift_bonus": 100.00
                },
                "employee_incentives": {
                    "delay_threshold_min": 15,
                    "delay_compensation_amount": 50.00
                }
            },
            version=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_active=True,
            created_by=admin_user.user_id
        )
        db.add(contract1)
        contracts.append(contract1)
        
        # Contract 2: Client 1 + Vendor 2 → TRIP Model
        contract2 = Contract(
            client_id=clients[0].client_id,
            vendor_id=vendors[1].vendor_id,
            model_type="TRIP",
            config_json={
                "billing_cycle_months": 1,
                "rates": {
                    "base_fare": 100.00,
                    "per_km_rate": 12.00,
                    "night_multiplier": 1.5
                },
                "employee_incentives": {
                    "delay_threshold_min": 10,
                    "delay_compensation_amount": 30.00
                }
            },
            version=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_active=True,
            created_by=admin_user.user_id
        )
        db.add(contract2)
        contracts.append(contract2)
        
        # Contract 3: Client 2 + Vendor 3 → HYBRID_A (Minimum Guarantee)
        contract3 = Contract(
            client_id=clients[1].client_id,
            vendor_id=vendors[2].vendor_id,
            model_type="HYBRID_A",
            config_json={
                "variant": "MIN_GUARANTEE",
                "billing_cycle_months": 1,
                "rates": {
                    "base_fare_per_trip": 50.00,
                    "per_km_rate": 14.00
                },
                "guarantee": {
                    "monthly_min_payout": 30000.00
                },
                "employee_incentives": {
                    "delay_threshold_min": 20,
                    "delay_compensation_amount": 50.00
                }
            },
            version=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_active=True,
            created_by=admin_user.user_id
        )
        db.add(contract3)
        contracts.append(contract3)
        
        # Contract 4: Client 3 + Vendor 4 → HYBRID_B (Base Distance Tier)
        contract4 = Contract(
            client_id=clients[2].client_id,
            vendor_id=vendors[3].vendor_id,
            model_type="HYBRID_B",
            config_json={
                "variant": "BASE_DISTANCE_TIER",
                "billing_cycle_months": 1,
                "rates": {
                    "fixed_base_pay": 300.00,
                    "per_extra_km_rate": 18.00
                },
                "thresholds": {
                    "included_km_per_trip": 15.0
                },
                "employee_incentives": {
                    "delay_threshold_min": 15,
                    "delay_compensation_amount": 40.00
                }
            },
            version=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            is_active=True,
            created_by=admin_user.user_id
        )
        db.add(contract4)
        contracts.append(contract4)
        
        db.flush()
        print(f"✅ Created {len(contracts)} contracts")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print("✨ Database seeding completed successfully!")
        print("="*60)
        print("\n📋 Summary:")
        print(f"   • {len(clients)} Clients")
        print(f"   • {len(vendors)} Vendors")
        print(f"   • {employee_count} Employees")
        print(f"   • {len(users)} Users")
        print(f"   • {len(contracts)} Contracts")
        
        print("\n🔑 Login Credentials:")
        print("   Admin:    admin / admin123")
        print("   Clients:  client1, client2, client3 / client123")
        print("   Vendors:  vendor1, vendor2, vendor3, vendor4 / vendor123")
        print("   Employees: emp1, emp6, emp11 / emp123")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

