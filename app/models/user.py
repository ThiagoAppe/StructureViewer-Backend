from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "Users"

    Id = Column(Integer, primary_key=True, index=True)
    UserName = Column(String(50), unique=True, nullable=False)
    Email = Column(String(100), unique=True, nullable=False)
    DepartmentId = Column(Integer, ForeignKey("Departments.Id"), nullable=True)
    IsActive = Column(Boolean, default=True)
    IsSuperuser = Column(Boolean, default=False)
    HashedPassword = Column(String(255), nullable=False)
    LastToken = Column(String(255), nullable=True)

    SubAreaPermissions = relationship("UserSubAreaPermission", back_populates="User")
