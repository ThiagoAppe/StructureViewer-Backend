from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SubDepartment(Base):
    """
    SQLAlchemy model representing a subdepartment entity.
    """
    __tablename__ = "sub_departments"

    id = Column("Id", Integer, primary_key=True, index=True)
    department_id = Column("DepartmentId", Integer, ForeignKey("departments.Id"), nullable=False)
    name = Column("Name", String(100), nullable=False)

    department = relationship("Department", back_populates="sub_departments")
    sub_area_permissions = relationship(
        "UserSubAreaPermission",
        back_populates="sub_department",
        cascade="all, delete-orphan"
    )
