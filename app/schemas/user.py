from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True
