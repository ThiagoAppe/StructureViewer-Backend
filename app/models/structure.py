from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.database import Base


class Structure(Base):
    """
    SQLAlchemy model representing the bill of materials structure,
    defining the relationship between a parent item and its components
    with their required quantities.
    """
    __tablename__ = "structure"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    parent_item_id = Column(
        "ParentItemId",
        Integer,
        ForeignKey("items.Id"),
        nullable=False
    )
    component_item_id = Column(
        "ComponentItemId",
        Integer,
        ForeignKey("items.Id"),
        nullable=False
    )
    quantity = Column("Quantity", Numeric(12, 4), nullable=False)
