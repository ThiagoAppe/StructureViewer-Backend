from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class FileStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    cancelled = "cancelled"

class userfileBase(BaseModel):
    FileName: str
    Status: FileStatus

class userfileCreate(userfileBase):
    UserId: int

class userfileRead(userfileBase):
    Id: int
    UserId: int
    UploadDate: datetime
    LastAccess: datetime

    class Config:
        orm_mode = True
