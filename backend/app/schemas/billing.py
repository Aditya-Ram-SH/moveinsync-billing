from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BillingRunRequest(BaseModel):
    client_id: int
    vendor_id: int
    billing_month: date


class BillingRunOut(BaseModel):
    billing_run_id: int
    client_id: int
    vendor_id: int
    billing_month: date
    status: str
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

