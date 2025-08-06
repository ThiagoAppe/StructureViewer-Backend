from pydantic import BaseModel
from typing import List

class DocumentosSchema(BaseModel):
    Title: str
    Description: str
    Path: str
    Functions: List[str]

    class Config:
        orm_mode = True
        alias_generator = lambda s: s.lower()
        populate_by_name = True
