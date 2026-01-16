from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class PermissionLevelEnum(str, enum.Enum):
    """
    Enumeration defining permission levels assigned to a user
    within a sub-department.
    """
    read = "Read"
    write = "Write"


class UserSubAreaPermission(Base):
    """
    Assigns a permission level for a user within a specific sub-department.
    """
    __tablename__ = "user_sub_area_permissions"

    id = Column("Id", Integer, primary_key=True)
    user_id = Column("UserId", Integer, ForeignKey("users.Id"), nullable=False)
    sub_department_id = Column(
        "SubDepartmentId",
        Integer,
        ForeignKey("sub_departments.Id"),
        nullable=False
    )

    user = relationship("User", back_populates="sub_area_permissions")
    sub_department = relationship("SubDepartment", back_populates="sub_area_permissions")
