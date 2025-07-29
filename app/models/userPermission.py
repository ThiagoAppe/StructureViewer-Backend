from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base


class UserPermission(Base):
    __tablename__ = "UserPermissions"

    UserId = Column(Integer, ForeignKey("Users.Id"), primary_key=True)
    PermissionId = Column(Integer, ForeignKey("Permissions.Id"), primary_key=True)
