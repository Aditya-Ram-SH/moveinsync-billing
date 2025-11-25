"""
Apply billing schema migration manually.
This script applies the migration to change billing_month to billing_start/billing_end.
Run: python apply_billing_migration.py
"""
from sqlalchemy import text
from app.db.session import SessionLocal, engine

def apply_migration():
    """Apply the billing schema migration."""
    db = SessionLocal()
    
    try:
        print("🔄 Applying billing schema migration...")
        print("=" * 60)
        
        # Check current schema
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'billing_runs' 
            AND column_name IN ('billing_month', 'billing_start', 'billing_end')
        """))
        existing_columns = [row[0] for row in result]
        print(f"\n📊 Current columns: {existing_columns}")
        
        if 'billing_start' in existing_columns and 'billing_end' in existing_columns:
            print("\n✅ Migration already applied! Database has billing_start and billing_end.")
            return
        
        if 'billing_month' not in existing_columns:
            print("\n⚠️  Warning: billing_month column not found. Schema may be in unexpected state.")
            return
        
        print("\n📝 Step 1: Dropping trigger and function...")
        db.execute(text("DROP TRIGGER IF EXISTS chk_billing_month_firstday ON billing_runs;"))
        db.execute(text("DROP FUNCTION IF EXISTS enforce_first_day_month();"))
        print("   ✅ Dropped trigger and function")
        
        print("\n📝 Step 2: Dropping old UNIQUE constraint...")
        db.execute(text("ALTER TABLE billing_runs DROP CONSTRAINT IF EXISTS uniq_billing_run;"))
        print("   ✅ Dropped old constraint")
        
        print("\n📝 Step 3: Adding new columns...")
        db.execute(text("ALTER TABLE billing_runs ADD COLUMN IF NOT EXISTS billing_start DATE;"))
        db.execute(text("ALTER TABLE billing_runs ADD COLUMN IF NOT EXISTS billing_end DATE;"))
        print("   ✅ Added billing_start and billing_end columns")
        
        print("\n📝 Step 4: Migrating existing data...")
        # Convert existing billing_month to billing_start/billing_end
        db.execute(text("""
            UPDATE billing_runs 
            SET 
                billing_start = DATE_TRUNC('month', billing_month)::DATE,
                billing_end = (DATE_TRUNC('month', billing_month) + INTERVAL '1 month')::DATE
            WHERE billing_start IS NULL OR billing_end IS NULL
        """))
        print("   ✅ Migrated existing data")
        
        print("\n📝 Step 5: Making columns NOT NULL...")
        db.execute(text("ALTER TABLE billing_runs ALTER COLUMN billing_start SET NOT NULL;"))
        db.execute(text("ALTER TABLE billing_runs ALTER COLUMN billing_end SET NOT NULL;"))
        print("   ✅ Set columns to NOT NULL")
        
        print("\n📝 Step 6: Dropping old billing_month column...")
        db.execute(text("ALTER TABLE billing_runs DROP COLUMN IF EXISTS billing_month;"))
        print("   ✅ Dropped billing_month column")
        
        print("\n📝 Step 7: Adding new UNIQUE constraint...")
        db.execute(text("""
            ALTER TABLE billing_runs 
            ADD CONSTRAINT uniq_billing_run 
            UNIQUE (client_id, vendor_id, billing_start)
        """))
        print("   ✅ Added new UNIQUE constraint")
        
        print("\n📝 Step 8: Adding check constraint...")
        db.execute(text("""
            ALTER TABLE billing_runs 
            ADD CONSTRAINT chk_billing_period 
            CHECK (billing_end > billing_start)
        """))
        print("   ✅ Added check constraint")
        
        print("\n📝 Step 9: Updating indexes...")
        db.execute(text("DROP INDEX IF EXISTS idx_billing_month;"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_billing_start ON billing_runs(billing_start);"))
        print("   ✅ Updated indexes")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✨ Migration completed successfully!")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   • Removed billing_month column")
        print("   • Added billing_start and billing_end columns")
        print("   • Updated UNIQUE constraint")
        print("   • Removed trigger and function")
        print("   • Added check constraint")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error during migration: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    apply_migration()

