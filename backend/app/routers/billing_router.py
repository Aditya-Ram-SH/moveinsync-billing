import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AuditLog, BillingRun, Trip, TripCharge, User
from app.routers.deps import get_current_admin, get_current_user
from app.schemas import BillingRunCreate
from app.services.billing_engine import BillingEngine

router = APIRouter()


@router.get("/")
def list_billing_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List billing runs filtered by user role."""
    # Re-query user to ensure we have fresh data with all relationships
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    # Debug: Log user info
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"User {user.username} (role={user.role}, client_id={user.client_id}, vendor_id={user.vendor_id}) requesting billing runs")
    
    query = db.query(BillingRun)
    
    # Role-based filtering - ensure we use the correct IDs
    if user.role == "CLIENT":
        client_id = user.client_id
        if client_id is None:
            logger.warning(f"User {user.username} has no client_id")
            return []
        # Client sees billing runs where they are the client
        # Use explicit int() to ensure type matching
        query = query.filter(BillingRun.client_id == int(client_id))
        logger.info(f"Filtering billing runs for CLIENT with client_id={client_id} (type={type(client_id)})")
    elif user.role == "VENDOR":
        vendor_id = user.vendor_id
        if vendor_id is None:
            logger.warning(f"User {user.username} has no vendor_id")
            return []
        # Vendor sees billing runs where they are the vendor
        # Use explicit int() to ensure type matching
        query = query.filter(BillingRun.vendor_id == int(vendor_id))
        logger.info(f"Filtering billing runs for VENDOR with vendor_id={vendor_id} (type={type(vendor_id)})")
    elif user.role == "EMPLOYEE":
        # Employees don't see billing runs
        return []
    # ADMIN sees all (no filter)
    
    # Get all billing runs for comparison
    all_runs = db.query(BillingRun).all()
    logger.info(f"Total billing runs in DB: {len(all_runs)}")
    for r in all_runs:
        logger.info(f"  All Run {r.billing_run_id}: client_id={r.client_id}, vendor_id={r.vendor_id}")
    
    # Order by started_at desc
    runs = query.order_by(BillingRun.started_at.desc()).all()
    
    logger.info(f"Found {len(runs)} billing runs for user {user.username} after filtering")
    for run in runs:
        logger.info(f"  Run {run.billing_run_id}: client_id={run.client_id}, vendor_id={run.vendor_id}, status={run.status}")
    
    # Serialize properly
    result = [
        {
            "billing_run_id": run.billing_run_id,
            "client_id": run.client_id,
            "vendor_id": run.vendor_id,
            "billing_month": run.billing_month.isoformat() if run.billing_month else None,
            "status": run.status,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "notes": run.notes,
        }
        for run in runs
    ]
    
    return result


@router.post("/run", status_code=status.HTTP_201_CREATED)
def run_billing(
    payload: BillingRunCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    if payload.billing_month.day != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="billing_month must be the first day of the month",
        )

    engine = BillingEngine(db)
    try:
        billing_run = engine.run(
            client_id=payload.client_id,
            vendor_id=payload.vendor_id,
            billing_month=payload.billing_month,
            triggered_by=current_user.user_id,
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    db.commit()
    db.refresh(billing_run)
    return {
        "billing_run_id": billing_run.billing_run_id,
        "status": billing_run.status,
        "notes": billing_run.notes,
    }


@router.get("/{billing_run_id}/report")
def get_billing_report(
    billing_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = db.query(BillingRun).filter(BillingRun.billing_run_id == billing_run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing run not found")
    
    # Role-based access control
    if current_user.role == "CLIENT" and run.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "VENDOR" and run.vendor_id != current_user.vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "EMPLOYEE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    charges = db.query(TripCharge).filter(TripCharge.billing_run_id == billing_run_id).all()
    totals = {
        "trips_processed": len(charges),
        "vendor_payout": float(sum((charge.vendor_payout or 0) for charge in charges)),
        "employee_incentives": float(sum((charge.incentive_amount or 0) for charge in charges)),
        "final_cost": float(sum((charge.final_cost or 0) for charge in charges)),
    }

    charge_rows = [
        {
            "charge_id": charge.charge_id,
            "trip_id": charge.trip_id,
            "base_cost": float(charge.base_cost or 0),
            "extra_km": float(charge.extra_km or 0),
            "extra_km_cost": float(charge.extra_km_cost or 0),
            "extra_hours": float(charge.extra_hours or 0),
            "extra_hours_cost": float(charge.extra_hours_cost or 0),
            "incentive_amount": float(charge.incentive_amount or 0),
            "vendor_payout": float(charge.vendor_payout or 0),
            "final_cost": float(charge.final_cost or 0),
            "created_at": charge.created_at.isoformat() if charge.created_at else None,
        }
        for charge in charges
    ]

    return {
        "billing_run": {
            "billing_run_id": run.billing_run_id,
            "client_id": run.client_id,
            "vendor_id": run.vendor_id,
            "billing_month": run.billing_month.isoformat(),
            "status": run.status,
            "notes": run.notes,
        },
        "totals": totals,
        "charges": charge_rows,
    }


@router.get("/{billing_run_id}/export")
def export_billing_report_csv(
    billing_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export billing report as CSV."""
    run = db.query(BillingRun).filter(BillingRun.billing_run_id == billing_run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing run not found")
    
    # Role-based access control
    if current_user.role == "CLIENT" and run.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "VENDOR" and run.vendor_id != current_user.vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "EMPLOYEE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Query charges with trip data in one go
    results = (
        db.query(TripCharge, Trip)
        .join(Trip, Trip.trip_id == TripCharge.trip_id)
        .filter(TripCharge.billing_run_id == billing_run_id)
        .order_by(Trip.start_time)
        .all()
    )

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        "Trip ID",
        "Trip Type",
        "Start Time",
        "Distance (km)",
        "Duration (min)",
        "Base Cost",
        "Extra KM",
        "Extra KM Cost",
        "Extra Hours",
        "Extra Hours Cost",
        "Employee Incentive",
        "Vendor Payout",
        "Final Cost",
    ])
    
    # Data rows
    charges = []
    for charge, trip in results:
        charges.append(charge)
        writer.writerow([
            charge.trip_id,
            trip.trip_type if trip.trip_type else "N/A",
            trip.start_time.isoformat() if trip.start_time else "N/A",
            float(trip.distance_km) if trip.distance_km else 0,
            trip.duration_min if trip.duration_min else 0,
            float(charge.base_cost or 0),
            float(charge.extra_km or 0),
            float(charge.extra_km_cost or 0),
            float(charge.extra_hours or 0),
            float(charge.extra_hours_cost or 0),
            float(charge.incentive_amount or 0),
            float(charge.vendor_payout or 0),
            float(charge.final_cost or 0),
        ])
    
    # Summary row
    totals = {
        "trips": len(charges),
        "vendor_payout": float(sum((charge.vendor_payout or 0) for charge in charges)),
        "employee_incentives": float(sum((charge.incentive_amount or 0) for charge in charges)),
        "final_cost": float(sum((charge.final_cost or 0) for charge in charges)),
    }
    writer.writerow([])
    writer.writerow(["TOTALS", "", "", "", "", "", "", "", "", "", totals["employee_incentives"], totals["vendor_payout"], totals["final_cost"]])

    csv_content = output.getvalue()
    output.close()

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=billing_run_{billing_run_id}_report.csv"
        },
    )


@router.get("/{billing_run_id}/audit")
def get_billing_audit_logs(
    billing_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get audit logs for a billing run."""
    run = db.query(BillingRun).filter(BillingRun.billing_run_id == billing_run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Billing run not found")
    
    # Role-based access control
    if current_user.role == "CLIENT" and run.client_id != current_user.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "VENDOR" and run.vendor_id != current_user.vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    elif current_user.role == "EMPLOYEE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    audit_logs = (
        db.query(AuditLog)
        .filter(
            AuditLog.entity == "BILLING_RUN",
            AuditLog.entity_id == str(billing_run_id),
        )
        .order_by(AuditLog.timestamp.desc())
        .all()
    )

    return [
        {
            "audit_id": log.audit_id,
            "action": log.action,
            "snapshot": log.snapshot,
            "performed_by": log.performed_by,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
        }
        for log in audit_logs
    ]


@router.get("/debug/my-billing-runs")
def debug_my_billing_runs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Debug endpoint to see what billing runs should be visible to current user."""
    # Re-query user
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    if not user:
        return {"error": "User not found"}
    
    # Get all billing runs
    all_runs = db.query(BillingRun).all()
    
    # Get filtered runs (same logic as list_billing_runs)
    query = db.query(BillingRun)
    filter_applied = "ADMIN (no filter)"
    if user.role == "CLIENT":
        if user.client_id is None:
            filter_applied = f"CLIENT with client_id=None (returning empty)"
        else:
            query = query.filter(BillingRun.client_id == user.client_id)
            filter_applied = f"CLIENT with client_id={user.client_id}"
    elif user.role == "VENDOR":
        if user.vendor_id is None:
            filter_applied = f"VENDOR with vendor_id=None (returning empty)"
        else:
            query = query.filter(BillingRun.vendor_id == user.vendor_id)
            filter_applied = f"VENDOR with vendor_id={user.vendor_id}"
    elif user.role == "EMPLOYEE":
        filter_applied = "EMPLOYEE (returning empty)"
    
    filtered_runs = query.order_by(BillingRun.started_at.desc()).all()
    
    return {
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role,
            "client_id": user.client_id,
            "vendor_id": user.vendor_id,
        },
        "all_billing_runs": [
            {
                "billing_run_id": r.billing_run_id,
                "client_id": r.client_id,
                "vendor_id": r.vendor_id,
                "billing_month": r.billing_month.isoformat() if r.billing_month else None,
                "status": r.status,
            }
            for r in all_runs
        ],
        "filtered_billing_runs": [
            {
                "billing_run_id": r.billing_run_id,
                "client_id": r.client_id,
                "vendor_id": r.vendor_id,
                "billing_month": r.billing_month.isoformat() if r.billing_month else None,
                "status": r.status,
            }
            for r in filtered_runs
        ],
        "filter_applied": filter_applied,
        "match_explanation": [
            {
                "run_id": r.billing_run_id,
                "run_client_id": r.client_id,
                "run_vendor_id": r.vendor_id,
                "user_client_id": user.client_id,
                "user_vendor_id": user.vendor_id,
                "should_see": (
                    (user.role == "CLIENT" and r.client_id == user.client_id) or
                    (user.role == "VENDOR" and r.vendor_id == user.vendor_id) or
                    (user.role == "ADMIN")
                )
            }
            for r in all_runs
        ]
    }


@router.get("/debug/check-data")
def debug_check_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Debug endpoint to check data alignment (admin only)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    
    from app.models import Contract, Trip, User as UserModel
    
    # Check contracts
    contracts = db.query(Contract).all()
    contract_info = [
        {
            "contract_id": c.contract_id,
            "client_id": c.client_id,
            "vendor_id": c.vendor_id,
            "model_type": c.model_type,
            "is_active": c.is_active,
        }
        for c in contracts
    ]
    
    # Check trips
    trips = db.query(Trip).all()
    trip_summary = {
        "total": len(trips),
        "by_status": {},
        "by_client_vendor": {},
        "by_month": {},
    }
    for trip in trips:
        trip_summary["by_status"][trip.status] = trip_summary["by_status"].get(trip.status, 0) + 1
        key = f"c{trip.client_id}_v{trip.vendor_id}"
        trip_summary["by_client_vendor"][key] = trip_summary["by_client_vendor"].get(key, 0) + 1
        if trip.start_time:
            month_key = trip.start_time.strftime("%Y-%m")
            trip_summary["by_month"][month_key] = trip_summary["by_month"].get(month_key, 0) + 1
    
    # Check users
    users = db.query(UserModel).all()
    user_info = [
        {
            "user_id": u.user_id,
            "username": u.username,
            "role": u.role,
            "client_id": u.client_id,
            "vendor_id": u.vendor_id,
            "employee_id": u.employee_id,
        }
        for u in users
    ]
    
    # Check billing runs
    billing_runs = db.query(BillingRun).all()
    run_info = [
        {
            "billing_run_id": r.billing_run_id,
            "client_id": r.client_id,
            "vendor_id": r.vendor_id,
            "billing_month": r.billing_month.isoformat() if r.billing_month else None,
            "status": r.status,
            "charge_count": db.query(TripCharge).filter(TripCharge.billing_run_id == r.billing_run_id).count(),
        }
        for r in billing_runs
    ]
    
    return {
        "contracts": contract_info,
        "trips": trip_summary,
        "users": user_info,
        "billing_runs": run_info,
    }
