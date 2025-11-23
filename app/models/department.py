from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Department(Base):
    """
    SQLAlchemy model representing a department entity.
    """
    __tablename__ = "departments"

    id = Column("Id", Integer, primary_key=True, index=True)
    name = Column("Name", String(100), nullable=False)

    sub_departments = relationship(
        "SubDepartment",
        back_populates="department",
        cascade="all, delete-orphan"
    )
