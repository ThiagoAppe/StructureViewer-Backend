from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey
from app.database import Base


class StockMovement(Base):
    """
    SQLAlchemy model representing a stock movement operation,
    defining the type of movement and its audit information.
    """
    __tablename__ = "stock_movements"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    movement_type = Column(
        "MovementType",
        Enum("in", "out", "adjustment", "production"),
        nullable=False
    )
    created_at = Column("CreatedAt", DateTime, nullable=False)
    created_by = Column("CreatedBy", Integer, ForeignKey("users.Id"), nullable=False)
