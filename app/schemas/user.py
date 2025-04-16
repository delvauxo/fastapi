from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID = Field(default_factory=uuid4)

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True
