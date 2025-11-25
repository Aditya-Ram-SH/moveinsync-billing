import csv
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List


def parse_trips_csv(payload: bytes) -> List[Dict[str, Any]]:
    """Parse CSV file with trip data.
    
    Expected columns (all required except currency which defaults to INR):
    - contract_id (required)
    - client_id (required) 
    - vendor_id (required)
    - employee_id (required)
    - trip_type (required)
    - booking_time (required, ISO format)
    - start_time (required, ISO format)
    - end_time (required, ISO format)
    - distance_km (required)
    - duration_min (required)
    - vehicle_type (required)
    - vehicle_number (required)
    - currency (optional, defaults to INR)
    """
    decoded = payload.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    
    # Check if file has headers
    if not reader.fieldnames:
        raise ValueError("CSV file appears to be empty or has no headers")
    
    # All columns are required except currency
    required_columns = [
        "contract_id", "client_id", "vendor_id", "employee_id", 
        "trip_type", "booking_time", "start_time", "end_time", 
        "distance_km", "duration_min", "vehicle_type", "vehicle_number"
    ]
    available_columns = list(reader.fieldnames) if reader.fieldnames else []
    missing_headers = [col for col in required_columns if col not in available_columns]
    
    if missing_headers:
        raise ValueError(
            f"CSV file is missing required columns: {', '.join(missing_headers)}. "
            f"Available columns: {', '.join(available_columns)}. "
            f"Required columns: {', '.join(required_columns)}. "
            f"Note: currency is optional and defaults to INR."
        )
    
    trips: List[Dict[str, Any]] = []
    for idx, row in enumerate(reader, start=2):  # Start at 2 (row 1 is header, row 2 is first data)
        # Check for required columns in this row
        missing = [col for col in required_columns if col not in row or not str(row[col]).strip()]
        if missing:
            raise ValueError(
                f"Row {idx}: Missing required values for columns: {', '.join(missing)}"
            )
        
        try:
            trips.append(
                {
                    "contract_id": int(row["contract_id"]),
                    "client_id": int(row["client_id"]),
                    "vendor_id": int(row["vendor_id"]),
                    "employee_id": int(row["employee_id"]),
                    "trip_type": row["trip_type"].strip(),
                    "booking_time": _parse_dt(row.get("booking_time"), required=True),
                    "start_time": _parse_dt(row.get("start_time"), required=True),
                    "end_time": _parse_dt(row.get("end_time"), required=True),
                    "distance_km": float(row["distance_km"]),
                    "duration_min": int(row["duration_min"]),
                    "vehicle_type": row["vehicle_type"].strip(),
                    "vehicle_number": row["vehicle_number"].strip(),
                    "currency": row.get("currency", "INR").strip() or "INR",
                    "raw_data": row,
                }
            )
        except (ValueError, KeyError) as e:
            raise ValueError(f"Row {idx}: Invalid data - {str(e)}") from e
    
    if not trips:
        raise ValueError("CSV file is empty or has no valid data rows")
    
    return trips


def _parse_dt(value: str | None, *, required: bool = False) -> datetime | None:
    if not value:
        if required:
            raise ValueError("Missing datetime field in CSV upload")
        return None
    return datetime.fromisoformat(value)

