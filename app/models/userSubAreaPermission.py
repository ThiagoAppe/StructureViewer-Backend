from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class PermissionLevelEnum(str, enum.Enum):
    Read = "Read"
    Write = "Write"

class UserSubAreaPermission(Base):
    __tablename__ = "UserSubAreaPermissions"

    UserId = Column(Integer, ForeignKey("Users.Id"), primary_key=True)
    SubDepartmentId = Column(Integer, ForeignKey("SubDepartments.Id"), primary_key=True)
    PermissionLevel = Column(Enum(PermissionLevelEnum), nullable=False)

    User = relationship("User", back_populates="SubAreaPermissions")
    SubDepartment = relationship("SubDepartment", back_populates="Permissions")
