"""
Script to clear all billing runs and related data.
Run: python clear_billing_data.py
"""
from app.db.session import SessionLocal
from app.models import BillingRun, TripCharge, Trip

def clear_billing_data():
    """Clear all billing runs, trip charges, and reset trip status."""
    db = SessionLocal()
    
    try:
        print("🧹 Starting billing data cleanup...")
        
        # Count before deletion
        billing_runs_count = db.query(BillingRun).count()
        trip_charges_count = db.query(TripCharge).count()
        processed_trips_count = db.query(Trip).filter(Trip.status == "PROCESSED").count()
        
        print(f"\n📊 Current data:")
        print(f"   • Billing Runs: {billing_runs_count}")
        print(f"   • Trip Charges: {trip_charges_count}")
        print(f"   • Processed Trips: {processed_trips_count}")
        
        if billing_runs_count == 0 and trip_charges_count == 0:
            print("\n✅ No billing data to clear. Database is already clean.")
            return
        
        # Step 1: Reset trips first (clear billing_run_id and status)
        print("\n🔄 Resetting trip status and clearing billing_run_id...")
        updated_trips = (
            db.query(Trip)
            .filter(Trip.billing_run_id.isnot(None))
            .update({"status": "INGESTED", "billing_run_id": None}, synchronize_session=False)
        )
        print(f"   ✅ Reset {updated_trips} trips (cleared billing_run_id and set status to INGESTED)")
        
        # Step 2: Delete trip charges (foreign key constraint)
        print("\n🗑️  Deleting trip charges...")
        deleted_charges = db.query(TripCharge).delete()
        print(f"   ✅ Deleted {deleted_charges} trip charges")
        
        # Step 3: Now we can delete billing runs (no foreign key references)
        print("\n🗑️  Deleting billing runs...")
        deleted_runs = db.query(BillingRun).delete()
        print(f"   ✅ Deleted {deleted_runs} billing runs")
        
        db.commit()
        
        print("\n" + "="*60)
        print("✨ Billing data cleanup completed successfully!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"   • Deleted {deleted_runs} billing runs")
        print(f"   • Deleted {deleted_charges} trip charges")
        print(f"   • Reset {updated_trips} trips to INGESTED")
        print(f"\n💡 Next steps:")
        print(f"   1. Create new billing runs from the frontend")
        print(f"   2. Make sure users have proper client_id/vendor_id")
        print(f"   3. Use billing month: 2025-11-01")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during cleanup: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    clear_billing_data()

