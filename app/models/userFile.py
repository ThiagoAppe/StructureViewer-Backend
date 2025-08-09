from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class FileStatus(PyEnum):
    pending = "pending"
    processing = "processing"
    done = "done"
    cancelled = "cancelled"

class UserFile(Base):
    __tablename__ = "UserFiles"

    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, ForeignKey("Users.Id"), nullable=False)
    FileName = Column(String(255), nullable=False)
    FileUuid = Column(String(255), unique=True, nullable=False)
    Status = Column(Enum(FileStatus), default=FileStatus.pending, nullable=False)
    UploadDate = Column(DateTime, default=datetime.utcnow)
    LastAccess = Column(DateTime, default=datetime.utcnow)

    User = relationship("User", back_populates="UserFiles")
