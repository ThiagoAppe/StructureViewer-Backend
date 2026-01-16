from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.role import user_roles


class User(Base):
    """
    User model representing system users and their associations.
    """
    __tablename__ = "users"

    id = Column("Id", Integer, primary_key=True, index=True)
    user_name = Column("UserName", String(50), unique=True, nullable=False)
    email = Column("Email", String(100), unique=True, nullable=False)
    department_id = Column("DepartmentId", Integer, ForeignKey("departments.Id"), nullable=True)
    is_active = Column("IsActive", Boolean, default=True)
    is_superuser = Column("IsSuperuser", Boolean, default=False)
    hashed_password = Column("HashedPassword", String(255), nullable=False)
    last_token = Column("LastToken", String(255), nullable=True)

    user_files = relationship(
        "UserFile",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    sub_area_permissions = relationship(
        "UserSubAreaPermission",
        back_populates="user"
    )

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users"
    )

    permissions = relationship(
        "Permission",
        secondary="user_permissions",
        back_populates="users"
    )
