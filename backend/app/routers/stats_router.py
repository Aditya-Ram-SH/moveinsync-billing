"""
Statistics and dashboard endpoints.
"""
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
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
from app.utils.username_mapping import get_username_from_client_id, get_username_from_vendor_id

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
            "client_username": get_username_from_client_id(db, recent_run.client_id),
            "vendor_username": get_username_from_vendor_id(db, recent_run.vendor_id),
            "billing_start": recent_run.billing_start.isoformat() if recent_run.billing_start else None,
            "billing_end": recent_run.billing_end.isoformat() if recent_run.billing_end else None,
            "status": recent_run.status,
            "started_at": recent_run.started_at.isoformat() if recent_run.started_at else None,
            "completed_at": recent_run.completed_at.isoformat() if recent_run.completed_at else None,
            "notes": recent_run.notes,
        }
    
    return stats


@router.get("/client-analytics")
def get_client_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed analytics data for client dashboard charts.
    Returns cost trends, vendor breakdown, trips over time, etc.
    """
    if current_user.role != "CLIENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for CLIENT users"
        )
    
    if current_user.client_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account missing client_id. Please contact administrator."
        )
    
    client_id = current_user.client_id
    
    # Calculate date range (last 12 months)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    # 1. Cost Trends Over Time (monthly)
    cost_trends_query = (
        db.query(
            func.date_trunc('month', BillingRun.billing_start).label('month'),
            func.sum(TripCharge.final_cost).label('total_cost'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .join(TripCharge, TripCharge.billing_run_id == BillingRun.billing_run_id)
        .join(Trip, Trip.trip_id == TripCharge.trip_id)
        .filter(
            BillingRun.client_id == client_id,
            BillingRun.status == "SUCCESS",
            BillingRun.billing_start >= start_date.date()
        )
        .group_by(func.date_trunc('month', BillingRun.billing_start))
        .order_by(func.date_trunc('month', BillingRun.billing_start))
    )
    cost_trends = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "total_cost": float(row.total_cost or 0),
            "trip_count": row.trip_count or 0
        }
        for row in cost_trends_query.all()
    ]
    
    # 2. Cost Breakdown by Vendor
    cost_by_vendor_query = (
        db.query(
            Trip.vendor_id,
            func.sum(TripCharge.final_cost).label('total_cost'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .join(TripCharge, TripCharge.trip_id == Trip.trip_id)
        .filter(Trip.client_id == client_id)
        .group_by(Trip.vendor_id)
        .order_by(func.sum(TripCharge.final_cost).desc())
    )
    cost_by_vendor = []
    for row in cost_by_vendor_query.all():
        vendor_name = get_username_from_vendor_id(db, row.vendor_id) or f"vendor_{row.vendor_id}"
        cost_by_vendor.append({
            "vendor_id": row.vendor_id,
            "vendor_name": vendor_name,
            "total_cost": float(row.total_cost or 0),
            "trip_count": row.trip_count or 0
        })
    
    # 3. Trips Over Time (monthly)
    trips_over_time_query = (
        db.query(
            func.date_trunc('month', Trip.start_time).label('month'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .filter(
            Trip.client_id == client_id,
            Trip.start_time >= start_date
        )
        .group_by(func.date_trunc('month', Trip.start_time))
        .order_by(func.date_trunc('month', Trip.start_time))
    )
    trips_over_time = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "trip_count": row.trip_count or 0
        }
        for row in trips_over_time_query.all()
    ]
    
    # 4. Trip Status Distribution
    status_distribution_query = (
        db.query(
            Trip.status,
            func.count(Trip.trip_id).label('count')
        )
        .filter(Trip.client_id == client_id)
        .group_by(Trip.status)
    )
    trip_status_distribution = [
        {
            "status": row.status or "UNKNOWN",
            "count": row.count or 0
        }
        for row in status_distribution_query.all()
    ]
    
    # 5. Distance Over Time (monthly)
    distance_over_time_query = (
        db.query(
            func.date_trunc('month', Trip.start_time).label('month'),
            func.sum(Trip.distance_km).label('total_distance')
        )
        .filter(
            Trip.client_id == client_id,
            Trip.start_time >= start_date
        )
        .group_by(func.date_trunc('month', Trip.start_time))
        .order_by(func.date_trunc('month', Trip.start_time))
    )
    distance_over_time = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "total_distance": float(row.total_distance or 0)
        }
        for row in distance_over_time_query.all()
    ]
    
    # 6. Billing Runs Timeline
    billing_runs_query = (
        db.query(BillingRun)
        .filter(
            BillingRun.client_id == client_id,
            BillingRun.billing_start >= start_date.date()
        )
        .order_by(BillingRun.billing_start.desc())
        .limit(12)
    )
    
    billing_runs_timeline = []
    for run in billing_runs_query.all():
        # Get total cost for this billing run
        total_cost = (
            db.query(func.sum(TripCharge.final_cost))
            .filter(TripCharge.billing_run_id == run.billing_run_id)
            .scalar() or Decimal("0")
        )
        
        billing_runs_timeline.append({
            "billing_run_id": run.billing_run_id,
            "billing_start": run.billing_start.isoformat() if run.billing_start else None,
            "billing_end": run.billing_end.isoformat() if run.billing_end else None,
            "status": run.status,
            "total_cost": float(total_cost),
            "started_at": run.started_at.isoformat() if run.started_at else None,
        })
    
    return {
        "cost_trends": cost_trends,
        "cost_by_vendor": cost_by_vendor,
        "trips_over_time": trips_over_time,
        "trip_status_distribution": trip_status_distribution,
        "distance_over_time": distance_over_time,
        "billing_runs_timeline": billing_runs_timeline,
    }


@router.get("/vendor-analytics")
def get_vendor_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed analytics data for vendor dashboard charts.
    Returns payout trends, client breakdown, trips over time, etc.
    """
    if current_user.role != "VENDOR":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for VENDOR users"
        )
    
    if current_user.vendor_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account missing vendor_id. Please contact administrator."
        )
    
    vendor_id = current_user.vendor_id
    
    # Calculate date range (last 12 months)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    # 1. Payout Trends Over Time (monthly)
    payout_trends_query = (
        db.query(
            func.date_trunc('month', BillingRun.billing_start).label('month'),
            func.sum(TripCharge.vendor_payout).label('total_payout'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .join(TripCharge, TripCharge.billing_run_id == BillingRun.billing_run_id)
        .join(Trip, Trip.trip_id == TripCharge.trip_id)
        .filter(
            BillingRun.vendor_id == vendor_id,
            BillingRun.status == "SUCCESS",
            BillingRun.billing_start >= start_date.date()
        )
        .group_by(func.date_trunc('month', BillingRun.billing_start))
        .order_by(func.date_trunc('month', BillingRun.billing_start))
    )
    payout_trends = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "total_payout": float(row.total_payout or 0),
            "trip_count": row.trip_count or 0
        }
        for row in payout_trends_query.all()
    ]
    
    # 2. Payout Breakdown by Client
    payout_by_client_query = (
        db.query(
            Trip.client_id,
            func.sum(TripCharge.vendor_payout).label('total_payout'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .join(TripCharge, TripCharge.trip_id == Trip.trip_id)
        .filter(Trip.vendor_id == vendor_id)
        .group_by(Trip.client_id)
        .order_by(func.sum(TripCharge.vendor_payout).desc())
    )
    payout_by_client = []
    for row in payout_by_client_query.all():
        client_name = get_username_from_client_id(db, row.client_id) or f"client_{row.client_id}"
        payout_by_client.append({
            "client_id": row.client_id,
            "client_name": client_name,
            "total_payout": float(row.total_payout or 0),
            "trip_count": row.trip_count or 0
        })
    
    # 3. Trips Over Time (monthly)
    trips_over_time_query = (
        db.query(
            func.date_trunc('month', Trip.start_time).label('month'),
            func.count(Trip.trip_id).label('trip_count')
        )
        .filter(
            Trip.vendor_id == vendor_id,
            Trip.start_time >= start_date
        )
        .group_by(func.date_trunc('month', Trip.start_time))
        .order_by(func.date_trunc('month', Trip.start_time))
    )
    trips_over_time = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "trip_count": row.trip_count or 0
        }
        for row in trips_over_time_query.all()
    ]
    
    # 4. Trip Status Distribution
    status_distribution_query = (
        db.query(
            Trip.status,
            func.count(Trip.trip_id).label('count')
        )
        .filter(Trip.vendor_id == vendor_id)
        .group_by(Trip.status)
    )
    trip_status_distribution = [
        {
            "status": row.status or "UNKNOWN",
            "count": row.count or 0
        }
        for row in status_distribution_query.all()
    ]
    
    # 5. Distance Over Time (monthly)
    distance_over_time_query = (
        db.query(
            func.date_trunc('month', Trip.start_time).label('month'),
            func.sum(Trip.distance_km).label('total_distance')
        )
        .filter(
            Trip.vendor_id == vendor_id,
            Trip.start_time >= start_date
        )
        .group_by(func.date_trunc('month', Trip.start_time))
        .order_by(func.date_trunc('month', Trip.start_time))
    )
    distance_over_time = [
        {
            "month": row.month.strftime("%Y-%m") if row.month else None,
            "total_distance": float(row.total_distance or 0)
        }
        for row in distance_over_time_query.all()
    ]
    
    # 6. Billing Runs Timeline
    billing_runs_query = (
        db.query(BillingRun)
        .filter(
            BillingRun.vendor_id == vendor_id,
            BillingRun.billing_start >= start_date.date()
        )
        .order_by(BillingRun.billing_start.desc())
        .limit(12)
    )
    
    billing_runs_timeline = []
    for run in billing_runs_query.all():
        # Get total payout for this billing run
        total_payout = (
            db.query(func.sum(TripCharge.vendor_payout))
            .filter(TripCharge.billing_run_id == run.billing_run_id)
            .scalar() or Decimal("0")
        )
        
        billing_runs_timeline.append({
            "billing_run_id": run.billing_run_id,
            "billing_start": run.billing_start.isoformat() if run.billing_start else None,
            "billing_end": run.billing_end.isoformat() if run.billing_end else None,
            "status": run.status,
            "total_payout": float(total_payout),
            "started_at": run.started_at.isoformat() if run.started_at else None,
        })
    
    return {
        "payout_trends": payout_trends,
        "payout_by_client": payout_by_client,
        "trips_over_time": trips_over_time,
        "trip_status_distribution": trip_status_distribution,
        "distance_over_time": distance_over_time,
        "billing_runs_timeline": billing_runs_timeline,
    }

