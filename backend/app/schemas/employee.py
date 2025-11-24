from typing import Optional

from pydantic import BaseModel

from app.schemas.base import TimestampMixin


class EmployeeBase(BaseModel):
    client_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    client_id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployeeOut(TimestampMixin, EmployeeBase):
    employee_id: int

