from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    email: str
    image_url: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: UUID = Field(default_factory=uuid4)

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True