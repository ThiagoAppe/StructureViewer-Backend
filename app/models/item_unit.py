from sqlalchemy import Column, Integer, String
from app.database import Base


class ItemUnit(Base):
    """
    SQLAlchemy model representing a unit of measurement used by items
    for stock, consumption, and production operations.
    """
    __tablename__ = "item_units"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    name = Column("Name", String(50), nullable=False)
    symbol = Column("Symbol", String(10), nullable=False)
