from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventBase(BaseModel):
    event_type: str
    reference_table: Optional[str] = None
    reference_id: Optional[int] = None
    created_by: Optional[int] = None


class EventCreate(EventBase):
    user_ids: list[int]
    notification_channels: list[str] | None = None


class EventRead(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
