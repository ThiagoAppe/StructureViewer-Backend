from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "Departments"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), unique=True, nullable=False)

    SubDepartments = relationship("SubDepartment", back_populates="Department")
