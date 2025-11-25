"""
Complete database reset - clears everything and starts fresh.
Run: python reset_database.py
WARNING: This will delete ALL data!
"""
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models import (
    AuditLog, BillingRun, Client, Contract, Employee, 
    Trip, TripCharge, User, Vendor
)

def reset_database():
    """Clear all data from the database."""
    db = SessionLocal()
    
    try:
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("="*60)
        
        # Count before deletion
        print("\n📊 Current data counts:")
        print(f"   • Clients: {db.query(Client).count()}")
        print(f"   • Vendors: {db.query(Vendor).count()}")
        print(f"   • Employees: {db.query(Employee).count()}")
        print(f"   • Users: {db.query(User).count()}")
        print(f"   • Contracts: {db.query(Contract).count()}")
        print(f"   • Trips: {db.query(Trip).count()}")
        print(f"   • Billing Runs: {db.query(BillingRun).count()}")
        print(f"   • Trip Charges: {db.query(TripCharge).count()}")
        print(f"   • Audit Logs: {db.query(AuditLog).count()}")
        
        print("\n🗑️  Deleting all data...")
        
        # Delete in correct order (respecting foreign keys)
        # 1. Trip charges (references trips and billing runs)
        deleted_charges = db.query(TripCharge).delete()
        print(f"   ✅ Deleted {deleted_charges} trip charges")
        
        # 2. Reset trips (clear foreign keys)
        updated_trips = db.query(Trip).update({
            "billing_run_id": None,
            "status": "INGESTED"
        }, synchronize_session=False)
        print(f"   ✅ Reset {updated_trips} trips")
        
        # 3. Delete trips
        deleted_trips = db.query(Trip).delete()
        print(f"   ✅ Deleted {deleted_trips} trips")
        
        # 4. Delete billing runs
        deleted_runs = db.query(BillingRun).delete()
        print(f"   ✅ Deleted {deleted_runs} billing runs")
        
        # 5. Delete contracts
        deleted_contracts = db.query(Contract).delete()
        print(f"   ✅ Deleted {deleted_contracts} contracts")
        
        # 6. Delete audit logs
        deleted_audits = db.query(AuditLog).delete()
        print(f"   ✅ Deleted {deleted_audits} audit logs")
        
        # 7. Delete users
        deleted_users = db.query(User).delete()
        print(f"   ✅ Deleted {deleted_users} users")
        
        # 8. Delete employees
        deleted_employees = db.query(Employee).delete()
        print(f"   ✅ Deleted {deleted_employees} employees")
        
        # 9. Delete vendors
        deleted_vendors = db.query(Vendor).delete()
        print(f"   ✅ Deleted {deleted_vendors} vendors")
        
        # 10. Delete clients
        deleted_clients = db.query(Client).delete()
        print(f"   ✅ Deleted {deleted_clients} clients")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✨ Database reset completed successfully!")
        print("="*60)
        print("\n💡 Next steps:")
        print("   1. Run: python seed_data.py")
        print("   2. Run: python seed_trips.py")
        print("   3. Verify: python verify_users.py")
        print("   4. Create billing runs from frontend")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during reset: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_database()

