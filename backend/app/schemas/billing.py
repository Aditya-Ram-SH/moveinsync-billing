from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def normalize_billing_period(year: int, month: int) -> tuple[date, date]:
    """
    Normalize year/month to billing period (first day of month to first day of next month).
    
    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)
    
    Returns:
        Tuple of (billing_start, billing_end) dates
    """
    billing_start = date(year, month, 1)
    if month == 12:
        billing_end = date(year + 1, 1, 1)
    else:
        billing_end = date(year, month + 1, 1)
    return billing_start, billing_end


class BillingRunCreate(BaseModel):
    client_id: int
    vendor_id: int
    year: int = Field(..., ge=2000, le=2100, description="Year (e.g., 2025)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")


class BillingRunResponse(BaseModel):
    billing_run_id: int
    client_id: int
    vendor_id: int
    billing_start: date
    billing_end: date
    status: str
    notes: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

