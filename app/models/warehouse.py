from sqlalchemy import Column, Integer, String
from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    name = Column("Name", String(100), nullable=False)
