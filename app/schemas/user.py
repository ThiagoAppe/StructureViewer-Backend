from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    UserName: str
    Email: EmailStr
    DepartmentId: Optional[int] = None


class UserCreate(UserBase):
    Password: str


class UserRead(UserBase):
    Id: int
    IsActive: bool
    IsSuperuser: bool
    LastToken: Optional[str] = None

    class Config:
        orm_mode = True
