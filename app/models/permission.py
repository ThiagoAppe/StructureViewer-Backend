from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Permission(Base):
    __tablename__ = "Permissions"

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), unique=True, nullable=False)

    Users = relationship(
        "User",
        secondary="UserPermissions",
        back_populates="Permissions"
    )
