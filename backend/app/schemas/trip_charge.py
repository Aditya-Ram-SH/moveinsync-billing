from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class TripChargeBase(BaseModel):
    trip_id: int
    billing_run_id: int
    base_cost: Optional[float] = None
    extra_km: Optional[float] = None
    extra_km_cost: Optional[float] = None
    extra_hours: Optional[float] = None
    extra_hours_cost: Optional[float] = None
    final_cost: float
    formula_snapshot: dict[str, Any]


class TripChargeOut(TripChargeBase):
    charge_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

