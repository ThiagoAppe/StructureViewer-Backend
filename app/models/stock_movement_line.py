from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.database import Base


class StockMovementLine(Base):
    """
    SQLAlchemy model representing a single line of a stock movement,
    detailing the item, warehouse location, and quantity involved.
    """
        
    __tablename__ = "stock_movement_lines"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    stock_movement_id = Column(
        "StockMovementId",
        Integer,
        ForeignKey("stock_movements.Id"),
        nullable=False
    )
    quantity = Column("Quantity", Numeric(12, 4), nullable=False)

    stock_movement = relationship("StockMovement")
