"""
Endpoints to get clients and vendors for dropdowns.
Shows usernames (client1, client2, etc.) instead of company names.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Client, User, Vendor
from app.routers.deps import get_current_user

router = APIRouter()


@router.get("/clients")
def list_clients(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Get all active clients with their usernames for dropdown selection."""
    clients = db.query(Client).filter(Client.status == "ACTIVE").order_by(Client.client_id).all()
    
    result = []
    for client in clients:
        # Find the user associated with this client
        user = db.query(User).filter(
            User.role == "CLIENT",
            User.client_id == client.client_id
        ).first()
        
        # Use username if available, otherwise fall back to company name
        display_name = user.username if user else client.name
        
        result.append({
            "client_id": client.client_id,
            "name": display_name,  # This will be the username (client1, client2, etc.)
            "company_name": client.name,  # Keep company name for reference
        })
    
    return result


@router.get("/vendors")
def list_vendors(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Get all active vendors with their usernames for dropdown selection."""
    vendors = db.query(Vendor).filter(Vendor.status == "ACTIVE").order_by(Vendor.vendor_id).all()
    
    result = []
    for vendor in vendors:
        # Find the user associated with this vendor
        user = db.query(User).filter(
            User.role == "VENDOR",
            User.vendor_id == vendor.vendor_id
        ).first()
        
        # Use username if available, otherwise fall back to company name
        display_name = user.username if user else vendor.name
        
        result.append({
            "vendor_id": vendor.vendor_id,
            "name": display_name,  # This will be the username (vendor1, vendor2, etc.)
            "company_name": vendor.name,  # Keep company name for reference
        })
    
    return result

