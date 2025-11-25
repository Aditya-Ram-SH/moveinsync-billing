from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Contract, Trip, TripCharge, User
from app.routers.deps import get_current_admin, get_current_user, get_current_vendor_or_admin
from app.utils.csv_import import parse_trips_csv

router = APIRouter()


@router.post("/ingest-csv")
async def ingest_trips_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_vendor_or_admin),
) -> dict[str, int]:
    """
    Ingest trips from CSV file.
    - Vendors can only upload trips for their own vendor_id
    - Admins can upload trips for any vendor
    """
    content = await file.read()
    try:
        rows = parse_trips_csv(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # If vendor, validate all trips belong to their vendor_id
    if current_user.role == "VENDOR" and current_user.vendor_id:
        for idx, payload in enumerate(rows, start=1):
            if payload.get("vendor_id") != current_user.vendor_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Row {idx}: You can only upload trips for your own vendor (vendor_id: {current_user.vendor_id})"
                )

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
        
        # Additional validation: if vendor, ensure contract belongs to them
        if current_user.role == "VENDOR" and current_user.vendor_id:
            if contract.vendor_id != current_user.vendor_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Contract {payload['contract_id']} does not belong to your vendor"
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
    
    trips = query.order_by(Trip.start_time.desc()).limit(100).all()
    
    return [
        {
            "trip_id": trip.trip_id,
            "trip_type": trip.trip_type,
            "start_time": trip.start_time.isoformat() if trip.start_time else None,
            "end_time": trip.end_time.isoformat() if trip.end_time else None,
            "distance_km": float(trip.distance_km) if trip.distance_km else 0,
            "duration_min": trip.duration_min,
            "status": trip.status,
            "employee_id": trip.employee_id,
        }
        for trip in trips
    ]


@router.get("/employee/my-trips")
def get_employee_trips_with_charges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get employee trips with charge information including incentives.
    Only accessible to employees for their own trips.
    """
    if current_user.role != "EMPLOYEE" or not current_user.employee_id:
        raise HTTPException(status_code=403, detail="This endpoint is only for employees")
    
    # Get all trips for this employee
    trips = (
        db.query(Trip)
        .filter(Trip.employee_id == current_user.employee_id)
        .order_by(Trip.start_time.desc())
        .all()
    )
    
    # Get charges for these trips
    trip_ids = [trip.trip_id for trip in trips]
    charges = {}
    if trip_ids:
        charge_list = (
            db.query(TripCharge)
            .filter(TripCharge.trip_id.in_(trip_ids))
            .all()
        )
        for charge in charge_list:
            charges[charge.trip_id] = charge
    
    # Combine trip and charge data
    result = []
    for trip in trips:
        charge = charges.get(trip.trip_id)
        result.append({
            "trip_id": trip.trip_id,
            "trip_type": trip.trip_type,
            "start_time": trip.start_time.isoformat() if trip.start_time else None,
            "end_time": trip.end_time.isoformat() if trip.end_time else None,
            "booking_time": trip.booking_time.isoformat() if trip.booking_time else None,
            "distance_km": float(trip.distance_km) if trip.distance_km else 0,
            "duration_min": trip.duration_min,
            "status": trip.status,
            "vehicle_type": trip.vehicle_type,
            "vehicle_number": trip.vehicle_number,
            "incentive_amount": float(charge.incentive_amount) if charge and charge.incentive_amount is not None else 0.0,
            "has_charge": charge is not None,
        })
    
    return result

