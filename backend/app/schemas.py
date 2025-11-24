from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


class TripCreate(BaseModel):
    contract_id: int
    client_id: int
    vendor_id: int
    employee_id: Optional[int] = None
    trip_type: Optional[str] = None
    booking_time: Optional[datetime] = None
    start_time: datetime
    end_time: datetime
    distance_km: float
    duration_min: int
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    currency: Optional[str] = "INR"
    raw_data: Dict[str, Any] = Field(default_factory=dict)


class ContractCreate(BaseModel):
    client_id: int
    vendor_id: int
    model_type: str
    config_json: Dict[str, Any]
    version: int = 1
    start_date: date
    end_date: date
    is_active: bool = True


class BillingRunCreate(BaseModel):
    client_id: int
    vendor_id: int
    billing_month: date

