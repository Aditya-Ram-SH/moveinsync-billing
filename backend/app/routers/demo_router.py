"""
DEMO MODE - Hardcoded responses for video recording
This will be removed after the demo
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from datetime import date

from app.db.session import get_db
from app.models import User
from app.routers.deps import get_current_user, get_current_admin

router = APIRouter()

# Demo state storage (in-memory, resets on server restart)
demo_state = {
    "contracts": [
        {
            "contract_id": 1,
            "client_id": 1,
            "vendor_id": 1,
            "model_type": "PACKAGE",
            "config_json": {
                "monthly_fixed_pay": 50000.00,
                "limits": {"included_km": 5000, "included_trips": 500},
                "vendor_payouts": {
                    "per_extra_km": 15.00,
                    "per_extra_trip": 200.00,
                    "night_shift_bonus": 100.00,
                },
            },
            "version": 1,
            "is_active": True,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
        {
            "contract_id": 2,
            "client_id": 2,
            "vendor_id": 2,
            "model_type": "HYBRID_A",
            "config_json": {
                "rates": {
                    "base_fare_per_trip": 50.00,
                    "per_km_rate": 14.00,
                },
                "guarantee": {"monthly_min_payout": 30000.00},
            },
            "version": 1,
            "is_active": True,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
    ],
    "billing_runs": [
        {
            "billing_run_id": 1,
            "client_id": 1,
            "vendor_id": 1,
            "billing_month": "2025-10-01",
            "status": "SUCCESS",
            "started_at": "2025-10-15T10:00:00",
            "completed_at": "2025-10-15T10:05:00",
            "notes": "Billing run completed successfully.",
        },
        {
            "billing_run_id": 2,
            "client_id": 2,
            "vendor_id": 2,
            "billing_month": "2025-11-01",
            "status": "SUCCESS",
            "started_at": "2025-11-15T10:00:00",
            "completed_at": "2025-11-15T10:05:00",
            "notes": "Billing run completed successfully.",
        },
    ],
    "next_contract_id": 3,
    "next_billing_run_id": 3,
}


@router.get("/demo/billing-runs")
def demo_list_billing_runs(
    current_user: User = Depends(get_current_user),
):
    """Hardcoded billing runs for demo"""
    all_runs = demo_state["billing_runs"]
    
    if current_user.role == "ADMIN":
        return all_runs
    elif current_user.role == "CLIENT":
        client_id = current_user.client_id
        return [r for r in all_runs if r["client_id"] == client_id]
    elif current_user.role == "VENDOR":
        vendor_id = current_user.vendor_id
        return [r for r in all_runs if r["vendor_id"] == vendor_id]
    return []


@router.post("/demo/billing/run")
def demo_run_billing(
    payload: dict,
    current_user: User = Depends(get_current_admin),
):
    """Create billing run in demo mode"""
    new_run = {
        "billing_run_id": demo_state["next_billing_run_id"],
        "client_id": payload["client_id"],
        "vendor_id": payload["vendor_id"],
        "billing_month": payload["billing_month"],
        "status": "SUCCESS",
        "started_at": "2025-11-15T10:00:00",
        "completed_at": "2025-11-15T10:05:00",
        "notes": "Billing run completed successfully.",
    }
    demo_state["billing_runs"].append(new_run)
    demo_state["next_billing_run_id"] += 1
    
    return {
        "billing_run_id": new_run["billing_run_id"],
        "status": "SUCCESS",
        "notes": "Billing run completed successfully.",
    }


@router.get("/demo/billing-report/{billing_run_id}")
def demo_get_billing_report(
    billing_run_id: int,
    current_user: User = Depends(get_current_user),
):
    """Hardcoded billing report for demo"""
    # Find the billing run
    run = next((r for r in demo_state["billing_runs"] if r["billing_run_id"] == billing_run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Billing run not found")
    
    # Check access
    if current_user.role == "CLIENT" and run["client_id"] != current_user.client_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "VENDOR" and run["vendor_id"] != current_user.vendor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "billing_run": {
            "billing_run_id": billing_run_id,
            "client_id": run["client_id"],
            "vendor_id": run["vendor_id"],
            "billing_month": run["billing_month"],
            "status": run["status"],
        },
        "totals": {
            "trips_processed": 15,
            "vendor_payout": 12500.00,
            "employee_incentives": 750.00,
            "final_cost": 13250.00,
        },
        "charges": [
            {
                "charge_id": i,
                "trip_id": 100 + i,
                "base_cost": 500.00,
                "extra_km": 10.0,
                "extra_km_cost": 150.00,
                "extra_hours": 0.0,
                "extra_hours_cost": 0.00,
                "incentive_amount": 50.00,
                "vendor_payout": 650.00,
                "final_cost": 700.00,
                "created_at": "2025-11-15T10:05:00",
            }
            for i in range(1, 16)
        ],
    }


@router.get("/demo/billing/{billing_run_id}/export")
def demo_export_billing_csv(
    billing_run_id: int,
    current_user: User = Depends(get_current_user),
):
    """Export billing report as CSV in demo mode"""
    from fastapi import Response
    import csv
    import io
    
    run = next((r for r in demo_state["billing_runs"] if r["billing_run_id"] == billing_run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Billing run not found")
    
    # Check access
    if current_user.role == "CLIENT" and run["client_id"] != current_user.client_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "VENDOR" and run["vendor_id"] != current_user.vendor_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Trip ID", "Trip Type", "Start Time", "End Time", "Distance (km)",
        "Duration (min)", "Base Cost", "Extra KM", "Extra KM Cost",
        "Employee Incentive", "Vendor Payout", "Final Cost"
    ])
    
    # Data rows
    for i in range(1, 16):
        writer.writerow([
            100 + i, "INBOUND", "2025-11-15T08:00:00", "2025-11-15T09:00:00",
            50.0 + i * 5, 60 + i * 5, 500.00, 10.0, 150.00,
            50.00, 650.00, 700.00
        ])
    
    # Summary
    writer.writerow([])
    writer.writerow(["TOTALS", "", "", "", "", "", "", "", "", 750.00, 12500.00, 13250.00])
    
    csv_content = output.getvalue()
    output.close()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=billing_run_{billing_run_id}_report.csv"
        },
    )


@router.get("/demo/contracts")
def demo_list_contracts(current_user: User = Depends(get_current_user)):
    """Hardcoded contracts for demo"""
    all_contracts = demo_state["contracts"]
    
    if current_user.role == "ADMIN":
        return all_contracts
    elif current_user.role == "CLIENT":
        client_id = current_user.client_id
        return [c for c in all_contracts if c["client_id"] == client_id]
    elif current_user.role == "VENDOR":
        vendor_id = current_user.vendor_id
        return [c for c in all_contracts if c["vendor_id"] == vendor_id]
    return []


@router.post("/demo/contracts")
def demo_create_contract(
    payload: dict,
    current_user: User = Depends(get_current_admin),
):
    """Create contract in demo mode - stores in memory"""
    new_contract = {
        "contract_id": demo_state["next_contract_id"],
        "client_id": payload["client_id"],
        "vendor_id": payload["vendor_id"],
        "model_type": payload["model_type"],
        "config_json": payload["config_json"],
        "version": payload.get("version", 1),
        "is_active": True,
        "start_date": payload["start_date"],
        "end_date": payload["end_date"],
    }
    demo_state["contracts"].append(new_contract)
    demo_state["next_contract_id"] += 1
    
    return {
        "contract_id": new_contract["contract_id"],
        "message": "Contract created successfully",
    }


@router.get("/demo/dashboard")
def demo_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Hardcoded dashboard stats for demo"""
    if current_user.role == "ADMIN":
        return {
            "total_clients": 3,
            "total_vendors": 4,
            "total_contracts": 4,
            "total_trips": 150,
            "processed_trips": 120,
            "pending_trips": 30,
            "total_distance_km": 15000.0,
            "total_cost": 500000.00,
            "total_vendor_payout": 450000.00,
            "total_employee_incentives": 50000.00,
            "total_billing_runs": 8,
            "recent_billing_run": {
                "billing_run_id": 2,
                "client_id": 2,
                "vendor_id": 2,
                "billing_month": "2025-11-01",
                "status": "SUCCESS",
                "started_at": "2025-11-15T10:00:00",
                "completed_at": "2025-11-15T10:05:00",
            },
        }
    elif current_user.role == "CLIENT":
        return {
            "total_clients": 1,
            "total_vendors": 1,
            "total_contracts": 1,
            "total_trips": 45,
            "processed_trips": 40,
            "pending_trips": 5,
            "total_distance_km": 4500.0,
            "total_cost": 150000.00,
            "total_billing_runs": 3,
            "recent_billing_run": {
                "billing_run_id": 2,
                "client_id": 2,
                "vendor_id": 2,
                "billing_month": "2025-11-01",
                "status": "SUCCESS",
                "started_at": "2025-11-15T10:00:00",
                "completed_at": "2025-11-15T10:05:00",
            },
        }
    elif current_user.role == "VENDOR":
        return {
            "total_vendors": 1,
            "total_clients": 1,
            "total_contracts": 1,
            "total_trips": 45,
            "processed_trips": 40,
            "pending_trips": 5,
            "total_distance_km": 4500.0,
            "total_vendor_payout": 125000.00,
            "total_billing_runs": 3,
            "recent_billing_run": {
                "billing_run_id": 2,
                "client_id": 2,
                "vendor_id": 2,
                "billing_month": "2025-11-01",
                "status": "SUCCESS",
                "started_at": "2025-11-15T10:00:00",
                "completed_at": "2025-11-15T10:05:00",
            },
        }
    elif current_user.role == "EMPLOYEE":
        # Employee sees trips with delays (incentives) - hardcoded for demo
        return {
            "total_trips": 25,
            "processed_trips": 20,
            "total_distance_km": 2500.0,
            "total_employee_incentives": 250.00,  # Hardcoded ₹250 for demo
            "total_incentives_earned": 250.00,  # Also set this field explicitly
            "recent_trips": [
                {
                    "trip_id": 100 + i,
                    "trip_type": "INBOUND",
                    "start_time": "2025-11-15T08:00:00",
                    "distance_km": 50.0 + i * 5,
                    "duration_min": 60 + i * 5,
                    "status": "PROCESSED",
                    "incentive_amount": 25.00 if i % 4 == 0 else 0.00,  # Some trips have delays - totals to ~250
                }
                for i in range(10)
            ],
        }
    return {}


@router.post("/demo/trips/ingest-csv")
async def demo_ingest_trips_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin),
):
    """Demo CSV upload - just returns success"""
    # Read file to validate it's a CSV
    content = await file.read()
    # For demo, just return success
    return {"rows_ingested": 10, "message": "CSV uploaded successfully (demo mode)"}


@router.post("/demo/reset")
def demo_reset(current_user: User = Depends(get_current_admin)):
    """Reset demo state - admin only"""
    demo_state["contracts"] = [
        {
            "contract_id": 1,
            "client_id": 1,
            "vendor_id": 1,
            "model_type": "PACKAGE",
            "config_json": {
                "monthly_fixed_pay": 50000.00,
                "limits": {"included_km": 5000, "included_trips": 500},
                "vendor_payouts": {
                    "per_extra_km": 15.00,
                    "per_extra_trip": 200.00,
                    "night_shift_bonus": 100.00,
                },
            },
            "version": 1,
            "is_active": True,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
        {
            "contract_id": 2,
            "client_id": 2,
            "vendor_id": 2,
            "model_type": "HYBRID_A",
            "config_json": {
                "rates": {
                    "base_fare_per_trip": 50.00,
                    "per_km_rate": 14.00,
                },
                "guarantee": {"monthly_min_payout": 30000.00},
            },
            "version": 1,
            "is_active": True,
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
    ]
    demo_state["billing_runs"] = [
        {
            "billing_run_id": 1,
            "client_id": 1,
            "vendor_id": 1,
            "billing_month": "2025-10-01",
            "status": "SUCCESS",
            "started_at": "2025-10-15T10:00:00",
            "completed_at": "2025-10-15T10:05:00",
            "notes": "Billing run completed successfully.",
        },
        {
            "billing_run_id": 2,
            "client_id": 2,
            "vendor_id": 2,
            "billing_month": "2025-11-01",
            "status": "SUCCESS",
            "started_at": "2025-11-15T10:00:00",
            "completed_at": "2025-11-15T10:05:00",
            "notes": "Billing run completed successfully.",
        },
    ]
    demo_state["next_contract_id"] = 3
    demo_state["next_billing_run_id"] = 3
    
    return {"message": "Demo state reset successfully"}

