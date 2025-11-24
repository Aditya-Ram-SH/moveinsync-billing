from typing import Optional

from pydantic import BaseModel

from app.schemas.base import TimestampMixin


class VendorBase(BaseModel):
    name: str
    contact_info: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    status: Optional[str] = None


class VendorOut(TimestampMixin, VendorBase):
    vendor_id: int

