from pydantic import BaseModel
from typing import List

class MainFunctions(BaseModel):
    title: str
    description: str
    path: str
    functions: List[str]

class InventarioMainFunctions(BaseModel):
    title: str
    path: str