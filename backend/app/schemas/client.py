from typing import Optional

from pydantic import BaseModel

from app.schemas.base import TimestampMixin


class ClientBase(BaseModel):
    name: str
    timezone: Optional[str] = "UTC"
    status: Optional[str] = "ACTIVE"


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None


class ClientOut(TimestampMixin, ClientBase):
    client_id: int

