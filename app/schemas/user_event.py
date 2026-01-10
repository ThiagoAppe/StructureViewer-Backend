from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from schemas.event import EventRead


class UserEventRead(BaseModel):
    id: int
    is_read: bool
    read_at: Optional[datetime]
    event: EventRead

    class Config:
        from_attributes = True
