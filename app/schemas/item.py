from pydantic import BaseModel
from typing import Optional


class ItemBase(BaseModel):
    code: str
    name: str
    description: Optional[str]
    item_type: str
    unit_id: int
    is_active: bool = True


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int

    class Config:
        from_attributes = True
