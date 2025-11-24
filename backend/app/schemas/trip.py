from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class TripBase(BaseModel):
    contract_id: int
    client_id: int
    vendor_id: int
    employee_id: Optional[int] = None
    trip_type: Optional[str] = "INBOUND"
    start_time: datetime
    end_time: datetime
    distance_km: float
    distance_unit: Optional[str] = "KM"
    duration_min: int
    currency: Optional[str] = "INR"
    raw_data: dict[str, Any]
    status: Optional[str] = "INGESTED"
    billing_run_id: Optional[int] = None


class TripCreate(TripBase):
    pass


class TripOut(TripBase):
    trip_id: int
    ingested_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

