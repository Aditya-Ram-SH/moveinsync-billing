"""
Utility functions to map between usernames and client/vendor IDs.
"""
from sqlalchemy.orm import Session
from app.models import User


def get_client_id_from_username(db: Session, username: str) -> int:
    """Get client_id from username (e.g., 'client1' -> client_id)."""
    user = db.query(User).filter(
        User.username == username,
        User.role == "CLIENT"
    ).first()
    if not user or not user.client_id:
        raise ValueError(f"Client user '{username}' not found or missing client_id")
    return user.client_id


def get_vendor_id_from_username(db: Session, username: str) -> int:
    """Get vendor_id from username (e.g., 'vendor1' -> vendor_id)."""
    user = db.query(User).filter(
        User.username == username,
        User.role == "VENDOR"
    ).first()
    if not user or not user.vendor_id:
        raise ValueError(f"Vendor user '{username}' not found or missing vendor_id")
    return user.vendor_id


def get_username_from_client_id(db: Session, client_id: int) -> str | None:
    """Get username from client_id."""
    user = db.query(User).filter(
        User.client_id == client_id,
        User.role == "CLIENT"
    ).first()
    return user.username if user else None


def get_username_from_vendor_id(db: Session, vendor_id: int) -> str | None:
    """Get username from vendor_id."""
    user = db.query(User).filter(
        User.vendor_id == vendor_id,
        User.role == "VENDOR"
    ).first()
    return user.username if user else None

