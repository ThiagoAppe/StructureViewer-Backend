from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class ProductionConsumption(Base):
    """
    SQLAlchemy model representing the consumption of a specific item
    within a production order, including the quantity used.
    """

    __tablename__ = "production_consumption"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    production_order_id = Column(
        "ProductionOrderId",
        Integer,
        ForeignKey("production_orders.Id"),
        nullable=False
    )
    item_id = Column(
        "ItemId",
        Integer,
        ForeignKey("items.Id"),
        nullable=False
    )
    quantity = Column("Quantity", Numeric(12, 4), nullable=False)

    production_order = relationship("ProductionOrder")
    item = relationship("Item")
