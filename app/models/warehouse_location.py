from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class WarehouseLocation(Base):
    __tablename__ = "warehouse_locations"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    warehouse_id = Column(
        "WarehouseId",
        Integer,
        ForeignKey("warehouses.Id"),
        nullable=False
    )

    warehouse = relationship("Warehouse")
