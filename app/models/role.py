from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

from app.models.permission import Permission

# Tabla intermedia user_roles
user_roles = Table(
    "userroles",
    Base.metadata,
    Column("UserId", Integer, ForeignKey("users.Id", ondelete="CASCADE"), primary_key=True),
    Column("RoleId", Integer, ForeignKey("roles.Id", ondelete="CASCADE"), primary_key=True)
)

# Tabla intermedia role_permissions
role_permissions = Table(
    "rolepermissions",
    Base.metadata,
    Column("RoleId", Integer, ForeignKey("roles.Id", ondelete="CASCADE"), primary_key=True),
    Column("PermissionId", Integer, ForeignKey("permissions.Id", ondelete="CASCADE"), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"

    id = Column("Id", Integer, primary_key=True, index=True)
    name = Column("Name", String(100), unique=True, nullable=False)

    # Relación con usuarios
    users = relationship("User", secondary=user_roles, back_populates="roles")

    # Relación con permisos
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
