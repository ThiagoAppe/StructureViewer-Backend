from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

user_permissions = Table(
    "userpermissions",
    Base.metadata,
    Column("UserId", Integer, ForeignKey("users.Id", ondelete="CASCADE"), primary_key=True),
    Column("PermissionId", Integer, ForeignKey("permissions.Id", ondelete="CASCADE"), primary_key=True)
)


class Permission(Base):
    """
    SQLAlchemy model representing a permission entity.
    """
    __tablename__ = "permissions"

    id = Column("Id", Integer, primary_key=True, index=True)
    name = Column("Name", String(100), unique=True, nullable=False)

    users = relationship(
        "User",
        secondary=user_permissions,
        back_populates="permissions"
    )

    roles = relationship(
        "Role",
        secondary="rolepermissions",
        back_populates="permissions"
    )
