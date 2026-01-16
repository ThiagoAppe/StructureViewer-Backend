from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WarehouseStock(Base):
    """
    SQLAlchemy model representing the current stock level of an item
    at a specific warehouse location.
    """

    __tablename__ = "warehouse_stock"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    warehouse_location_id = Column(
        "WarehouseLocationId",
        Integer,
        ForeignKey("warehouse_locations.Id"),
        nullable=False
    )

    warehouse_location = relationship("WarehouseLocation")
