"""
Statistics and dashboard endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    BillingRun,
    Client,
    Contract,
    Trip,
    TripCharge,
    User,
    Vendor,
)
from app.routers.deps import get_current_user

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated statistics for the dashboard.
    Filters data based on user role.
    """
    from decimal import Decimal
    
    # Base counts
    stats = {
        "total_clients": 0,
        "total_vendors": 0,
        "total_contracts": 0,
        "total_trips": 0,
        "processed_trips": 0,
        "pending_trips": 0,
        "total_distance_km": 0.0,
        "total_billing_runs": 0,
        "total_cost": 0.0,
        "total_vendor_payout": 0.0,
        "total_employee_incentives": 0.0,
        "recent_billing_run": None,
    }
    
    # Role-based filtering
    if current_user.role == "ADMIN":
        # Admin sees everything
        stats["total_clients"] = db.query(func.count(Client.client_id)).scalar() or 0
        stats["total_vendors"] = db.query(func.count(Vendor.vendor_id)).scalar() or 0
        stats["total_contracts"] = db.query(func.count(Contract.contract_id)).scalar() or 0
        stats["total_trips"] = db.query(func.count(Trip.trip_id)).scalar() or 0
        stats["processed_trips"] = db.query(func.count(Trip.trip_id)).filter(Trip.status == "PROCESSED").scalar() or 0
        stats["pending_trips"] = db.query(func.count(Trip.trip_id)).filter(Trip.status == "INGESTED").scalar() or 0
        stats["total_distance_km"] = float(db.query(func.sum(Trip.distance_km)).scalar() or 0)
        stats["total_billing_runs"] = db.query(func.count(BillingRun.billing_run_id)).scalar() or 0
        
        # Get cost totals from trip charges
        total_cost = db.query(func.sum(TripCharge.final_cost)).scalar() or Decimal("0")
        total_payout = db.query(func.sum(TripCharge.vendor_payout)).scalar() or Decimal("0")
        total_incentives = db.query(func.sum(TripCharge.incentive_amount)).scalar() or Decimal("0")
        stats["total_cost"] = float(total_cost)
        stats["total_vendor_payout"] = float(total_payout)
        stats["total_employee_incentives"] = float(total_incentives)
        
        # Get most recent billing run
        recent_run = (
            db.query(BillingRun)
            .order_by(BillingRun.started_at.desc())
            .first()
        )
        
    elif current_user.role == "CLIENT":
        # Client sees only their data
        stats["total_clients"] = 1
        stats["total_vendors"] = (
            db.query(func.count(func.distinct(Contract.vendor_id)))
            .filter(Contract.client_id == current_user.client_id)
            .scalar() or 0
        )
        stats["total_contracts"] = (
            db.query(func.count(Contract.contract_id))
            .filter(Contract.client_id == current_user.client_id)
            .scalar() or 0
        )
        stats["total_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.client_id == current_user.client_id)
            .scalar() or 0
        )
        stats["processed_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.client_id == current_user.client_id, Trip.status == "PROCESSED")
            .scalar() or 0
        )
        stats["pending_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.client_id == current_user.client_id, Trip.status == "INGESTED")
            .scalar() or 0
        )
        stats["total_distance_km"] = float(
            db.query(func.sum(Trip.distance_km))
            .filter(Trip.client_id == current_user.client_id)
            .scalar() or 0
        )
        stats["total_billing_runs"] = (
            db.query(func.count(BillingRun.billing_run_id))
            .filter(BillingRun.client_id == current_user.client_id)
            .scalar() or 0
        )
        
        # Get cost totals for this client
        total_cost = (
            db.query(func.sum(TripCharge.final_cost))
            .join(Trip, Trip.trip_id == TripCharge.trip_id)
            .filter(Trip.client_id == current_user.client_id)
            .scalar() or Decimal("0")
        )
        stats["total_cost"] = float(total_cost)
        
        recent_run = (
            db.query(BillingRun)
            .filter(BillingRun.client_id == current_user.client_id)
            .order_by(BillingRun.started_at.desc())
            .first()
        )
        
    elif current_user.role == "VENDOR":
        # Vendor sees only their data
        stats["total_vendors"] = 1
        stats["total_clients"] = (
            db.query(func.count(func.distinct(Contract.client_id)))
            .filter(Contract.vendor_id == current_user.vendor_id)
            .scalar() or 0
        )
        stats["total_contracts"] = (
            db.query(func.count(Contract.contract_id))
            .filter(Contract.vendor_id == current_user.vendor_id)
            .scalar() or 0
        )
        stats["total_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.vendor_id == current_user.vendor_id)
            .scalar() or 0
        )
        stats["processed_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.vendor_id == current_user.vendor_id, Trip.status == "PROCESSED")
            .scalar() or 0
        )
        stats["pending_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.vendor_id == current_user.vendor_id, Trip.status == "INGESTED")
            .scalar() or 0
        )
        stats["total_distance_km"] = float(
            db.query(func.sum(Trip.distance_km))
            .filter(Trip.vendor_id == current_user.vendor_id)
            .scalar() or 0
        )
        stats["total_billing_runs"] = (
            db.query(func.count(BillingRun.billing_run_id))
            .filter(BillingRun.vendor_id == current_user.vendor_id)
            .scalar() or 0
        )
        
        # Get vendor payout total
        total_payout = (
            db.query(func.sum(TripCharge.vendor_payout))
            .join(Trip, Trip.trip_id == TripCharge.trip_id)
            .filter(Trip.vendor_id == current_user.vendor_id)
            .scalar() or Decimal("0")
        )
        stats["total_vendor_payout"] = float(total_payout)
        
        recent_run = (
            db.query(BillingRun)
            .filter(BillingRun.vendor_id == current_user.vendor_id)
            .order_by(BillingRun.started_at.desc())
            .first()
        )
        
    elif current_user.role == "EMPLOYEE":
        # Employee sees only their trips
        stats["total_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.employee_id == current_user.employee_id)
            .scalar() or 0
        )
        stats["processed_trips"] = (
            db.query(func.count(Trip.trip_id))
            .filter(Trip.employee_id == current_user.employee_id, Trip.status == "PROCESSED")
            .scalar() or 0
        )
        stats["total_distance_km"] = float(
            db.query(func.sum(Trip.distance_km))
            .filter(Trip.employee_id == current_user.employee_id)
            .scalar() or 0
        )
        
        # Get employee incentives total
        incentives_total = (
            db.query(func.sum(TripCharge.incentive_amount))
            .join(Trip, Trip.trip_id == TripCharge.trip_id)
            .filter(Trip.employee_id == current_user.employee_id)
            .scalar() or 0
        )
        stats["total_incentives_earned"] = float(incentives_total)
        stats["total_employee_incentives"] = float(incentives_total)  # Also set for consistency
        
        recent_run = None
    else:
        recent_run = None
    
    # Format recent billing run
    if recent_run:
        stats["recent_billing_run"] = {
            "billing_run_id": recent_run.billing_run_id,
            "client_id": recent_run.client_id,
            "vendor_id": recent_run.vendor_id,
            "billing_month": recent_run.billing_month.isoformat() if recent_run.billing_month else None,
            "status": recent_run.status,
            "started_at": recent_run.started_at.isoformat() if recent_run.started_at else None,
            "completed_at": recent_run.completed_at.isoformat() if recent_run.completed_at else None,
            "notes": recent_run.notes,
        }
    
    return stats

