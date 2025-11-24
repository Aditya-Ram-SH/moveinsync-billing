from typing import Optional

from pydantic import BaseModel

from app.schemas.base import TimestampMixin


class UserBase(BaseModel):
    username: str
    role: str
    client_id: Optional[int] = None
    vendor_id: Optional[int] = None
    employee_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserOut(TimestampMixin, UserBase):
    user_id: int

