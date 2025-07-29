from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SubDepartment(Base):
    __tablename__ = "SubDepartments"

    Id = Column(Integer, primary_key=True, index=True)
    DepartmentId = Column(Integer, ForeignKey("Departments.Id"), nullable=False)
    Name = Column(String(100), nullable=False)

    Department = relationship("Department", back_populates="SubDepartments")
    Permissions = relationship("UserSubAreaPermission", back_populates="SubDepartment")
