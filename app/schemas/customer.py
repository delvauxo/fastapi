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

# Nouveau modèle pour renvoyer les agrégations liées aux factures
class CustomerAggregated(Customer):
    total_invoices: int
    total_pending: float
    total_paid: float

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True