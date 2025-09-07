from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    user_name: str
    email: EmailStr
    department_id: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    last_token: Optional[str] = None

    class Config:
        from_attributes = True
