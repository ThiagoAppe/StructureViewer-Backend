from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NotificationRead(BaseModel):
    id: int
    channel: str
    sent: bool
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True
