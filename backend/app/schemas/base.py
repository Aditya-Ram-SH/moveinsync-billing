from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(ORMBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

