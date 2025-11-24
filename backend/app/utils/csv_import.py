import csv
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List


def parse_trips_csv(payload: bytes) -> List[Dict[str, Any]]:
    decoded = payload.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    trips: List[Dict[str, Any]] = []
    for row in reader:
        trips.append(
            {
                "contract_id": int(row["contract_id"]),
                "client_id": int(row["client_id"]),
                "vendor_id": int(row["vendor_id"]),
                "employee_id": int(row["employee_id"]) if row.get("employee_id") else None,
                "trip_type": row.get("trip_type") or None,
                "booking_time": _parse_dt(row.get("booking_time")),
                "start_time": _parse_dt(row.get("start_time"), required=True),
                "end_time": _parse_dt(row.get("end_time"), required=True),
                "distance_km": float(row["distance_km"]),
                "duration_min": int(row["duration_min"]),
                "vehicle_type": row.get("vehicle_type"),
                "vehicle_number": row.get("vehicle_number"),
                "currency": row.get("currency") or "INR",
                "raw_data": row,
            }
        )
    return trips


def _parse_dt(value: str | None, *, required: bool = False) -> datetime | None:
    if not value:
        if required:
            raise ValueError("Missing datetime field in CSV upload")
        return None
    return datetime.fromisoformat(value)

