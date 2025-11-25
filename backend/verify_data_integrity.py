"""
Verify data integrity - check that contracts match actual clients/vendors.
Run: python verify_data_integrity.py
"""
from app.db.session import SessionLocal
from app.models import Client, Contract, Vendor, User

def verify_data_integrity():
    """Check that all contracts reference valid clients/vendors."""
    db = SessionLocal()
    
    try:
        print("🔍 Verifying data integrity...")
        print("="*60)
        
        # Get all clients and vendors
        all_clients = {c.client_id: c for c in db.query(Client).all()}
        all_vendors = {v.vendor_id: v for v in db.query(Vendor).all()}
        
        print(f"\n📊 Database state:")
        print(f"   • Clients: {len(all_clients)} (IDs: {sorted(all_clients.keys())})")
        print(f"   • Vendors: {len(all_vendors)} (IDs: {sorted(all_vendors.keys())})")
        
        # Check contracts
        contracts = db.query(Contract).all()
        print(f"   • Contracts: {len(contracts)}")
        
        issues = []
        valid_contracts = []
        
        for contract in contracts:
            client_exists = contract.client_id in all_clients
            vendor_exists = contract.vendor_id in all_vendors
            
            if not client_exists or not vendor_exists:
                issues.append({
                    "contract_id": contract.contract_id,
                    "client_id": contract.client_id,
                    "vendor_id": contract.vendor_id,
                    "client_exists": client_exists,
                    "vendor_exists": vendor_exists,
                })
            else:
                valid_contracts.append(contract)
        
        print("\n" + "="*60)
        
        if issues:
            print(f"❌ Found {len(issues)} contract(s) with mismatched IDs:")
            for issue in issues:
                print(f"\n   Contract #{issue['contract_id']}:")
                print(f"      Client ID {issue['client_id']}: {'✅ Exists' if issue['client_exists'] else '❌ NOT FOUND'}")
                print(f"      Vendor ID {issue['vendor_id']}: {'✅ Exists' if issue['vendor_exists'] else '❌ NOT FOUND'}")
            
            print(f"\n💡 Solution: Run 'python reset_database.py' then 'python seed_data.py'")
        else:
            print(f"✅ All {len(contracts)} contracts reference valid clients and vendors!")
        
        # Check user IDs match clients/vendors
        print("\n" + "="*60)
        print("🔍 Verifying user IDs...")
        
        user_issues = []
        users = db.query(User).all()
        
        for user in users:
            if user.role == "CLIENT" and user.client_id not in all_clients:
                user_issues.append(f"{user.username}: client_id={user.client_id} doesn't exist")
            elif user.role == "VENDOR" and user.vendor_id not in all_vendors:
                user_issues.append(f"{user.username}: vendor_id={user.vendor_id} doesn't exist")
        
        if user_issues:
            print(f"❌ Found {len(user_issues)} user(s) with mismatched IDs:")
            for issue in user_issues:
                print(f"   • {issue}")
        else:
            print(f"✅ All {len(users)} users reference valid clients/vendors!")
        
        print("\n" + "="*60)
        
        if issues or user_issues:
            print("\n⚠️  Data integrity issues found. Run reset and re-seed:")
            print("   1. python reset_database.py")
            print("   2. python seed_data.py")
            print("   3. python seed_trips.py")
        else:
            print("\n✅ Data integrity check passed! Everything looks good.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    verify_data_integrity()

