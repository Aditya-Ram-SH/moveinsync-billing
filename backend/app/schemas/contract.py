from datetime import date
from typing import Any, Optional

from pydantic import BaseModel

from app.schemas.base import TimestampMixin


class ContractBase(BaseModel):
    client_id: int
    vendor_id: int
    model_type: str
    config_json: dict[str, Any]
    version: int = 1
    start_date: date
    end_date: date
    is_active: bool = True
    created_by: Optional[int] = None


class ContractCreate(ContractBase):
    pass


class ContractCreateWithUsernames(BaseModel):
    """Contract creation with usernames instead of IDs."""
    client_username: str
    vendor_username: str
    model_type: str
    config_json: dict[str, Any]
    version: int = 1
    start_date: date
    end_date: date
    is_active: bool = True


class ContractUpdate(BaseModel):
    model_type: Optional[str] = None
    config_json: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None


class ContractOut(TimestampMixin, ContractBase):
    contract_id: int

