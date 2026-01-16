from sqlalchemy import Column, Integer, String, Text, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Item(Base):
    """
    SQLAlchemy model representing an item entity, which can be a material,
    set, or finished product, including its unit of measurement and status.
    """
    __tablename__ = "items"

    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    code = Column("Code", String(50), unique=True, nullable=False)
    name = Column("Name", String(150), nullable=False)
    description = Column("Description", Text)
    item_type = Column(
        "ItemType",
        Enum("material", "conjunto", "producto"),
        nullable=False
    )
    unit_id = Column(
        "UnitId",
        Integer,
        ForeignKey("item_units.Id"),
        nullable=False
    )
    is_active = Column("IsActive", Boolean, nullable=False, default=True)

    unit = relationship("ItemUnit")
