from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class FileStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    done = "done"
    cancelled = "cancelled"

class UserFile(Base):
    """
    File entity uploaded and managed per user.
    """
    __tablename__ = "userfiles"

    id = Column("Id", Integer, primary_key=True, index=True)
    user_id = Column("UserId", Integer, ForeignKey("users.Id"), nullable=False)
    file_name = Column("Filename", String(255), nullable=False)
    file_uuid = Column("FileUuid", String(32), unique=True, nullable=False)
    status = Column("Status", Enum(FileStatus), default=FileStatus.pending, nullable=False)
    upload_date = Column("UploadDate", DateTime, server_default=text("CURRENT_TIMESTAMP"))
    last_access = Column("LastAccess", DateTime, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="user_files")
