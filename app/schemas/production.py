from pydantic import BaseModel
from decimal import Decimal


class ProductionOrderCreate(BaseModel):
    item_id: int
    quantity: Decimal


class ProductionConsumptionCreate(BaseModel):
    production_order_id: int
    item_id: int
    quantity_used: Decimal
