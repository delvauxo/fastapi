from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class CustomerBase(BaseModel):
    name: str
    email: str
    image_url: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: UUID = Field(default_factory=uuid4)

    class Config:
        orm_mode = True
