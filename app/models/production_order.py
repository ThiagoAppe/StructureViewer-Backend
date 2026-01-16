from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ProductionOrder(Base):
    """
    SQLAlchemy model representing a production order, including the item
    to be produced, its quantity, current status, and audit information.
    """
    __tablename__ = "production_orders"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    item_id = Column(
        "ItemId",
        Integer,
        ForeignKey("items.Id"),
        nullable=False
    )
    created_at = Column("CreatedAt", DateTime, default=datetime.utcnow)

    item = relationship("Item")
