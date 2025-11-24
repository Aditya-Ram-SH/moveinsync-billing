from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Contract, Trip, User
from app.routers.deps import get_current_admin, get_current_user
from app.utils.csv_import import parse_trips_csv

router = APIRouter()


@router.post("/ingest-csv")
async def ingest_trips_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_admin),
) -> dict[str, int]:
    content = await file.read()
    try:
        rows = parse_trips_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for payload in rows:
        contract = db.query(Contract).filter(Contract.contract_id == payload["contract_id"]).first()
        if not contract:
            raise HTTPException(
                status_code=400,
                detail=f"Contract {payload['contract_id']} does not exist",
            )
        if contract.client_id != payload["client_id"] or contract.vendor_id != payload["vendor_id"]:
            raise HTTPException(
                status_code=400,
                detail=f"Trip client/vendor mismatch for contract {payload['contract_id']}",
            )
        trip = Trip(
            contract_id=payload["contract_id"],
            client_id=payload["client_id"],
            vendor_id=payload["vendor_id"],
            employee_id=payload.get("employee_id"),
            trip_type=payload.get("trip_type") or "INBOUND",
            booking_time=payload.get("booking_time"),
            start_time=payload["start_time"],
            end_time=payload["end_time"],
            distance_km=payload["distance_km"],
            duration_min=payload["duration_min"],
            vehicle_type=payload.get("vehicle_type"),
            vehicle_number=payload.get("vehicle_number"),
            currency=payload.get("currency"),
            raw_data=payload.get("raw_data", {}),
        )
        db.add(trip)
    db.commit()
    return {"rows_ingested": len(rows)}


@router.get("/")
def list_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List trips filtered by user role.
    - Employees see only their own trips
    - Clients see trips for their company
    - Vendors see trips for their vendors
    - Admins see all trips
    """
    query = db.query(Trip)
    
    if current_user.role == "EMPLOYEE" and current_user.employee_id:
        query = query.filter(Trip.employee_id == current_user.employee_id)
    elif current_user.role == "CLIENT" and current_user.client_id:
        query = query.filter(Trip.client_id == current_user.client_id)
    elif current_user.role == "VENDOR" and current_user.vendor_id:
        query = query.filter(Trip.vendor_id == current_user.vendor_id)
    # Admin sees all trips (no filter)
    
    trips = query.order_by(Trip.start_time.desc()).limit(10).all()
    
    return [
        {
            "trip_id": trip.trip_id,
            "trip_type": trip.trip_type,
            "start_time": trip.start_time.isoformat() if trip.start_time else None,
            "end_time": trip.end_time.isoformat() if trip.end_time else None,
            "distance_km": float(trip.distance_km) if trip.distance_km else 0,
            "duration_min": trip.duration_min,
            "status": trip.status,
        }
        for trip in trips
    ]

