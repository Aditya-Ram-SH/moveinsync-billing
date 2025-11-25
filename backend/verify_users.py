"""
Script to verify users have proper client_id/vendor_id set.
Run: python verify_users.py
"""
from app.db.session import SessionLocal
from app.models import User

def verify_users():
    """Check that all users have proper IDs set."""
    db = SessionLocal()
    
    try:
        print("🔍 Verifying user data...")
        print("="*60)
        
        users = db.query(User).all()
        issues = []
        
        for user in users:
            status = "✅"
            problems = []
            
            if user.role == "CLIENT" and user.client_id is None:
                status = "❌"
                problems.append("Missing client_id")
            elif user.role == "VENDOR" and user.vendor_id is None:
                status = "❌"
                problems.append("Missing vendor_id")
            elif user.role == "EMPLOYEE" and user.employee_id is None:
                status = "⚠️ "
                problems.append("Missing employee_id")
            
            print(f"{status} {user.username:15} | Role: {user.role:8} | Client: {str(user.client_id):5} | Vendor: {str(user.vendor_id):5} | Employee: {str(user.employee_id):5}")
            
            if problems:
                issues.append(f"{user.username}: {', '.join(problems)}")
        
        print("="*60)
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} user(s) with issues:")
            for issue in issues:
                print(f"   • {issue}")
            print(f"\n💡 Fix: Run 'python seed_data.py' to update user IDs")
        else:
            print(f"\n✅ All {len(users)} users have proper IDs set!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    verify_users()

