from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional
from datetime import date

class InvoiceBase(BaseModel):
    customer_id: UUID
    amount: int
    status: str
    date: date

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: UUID = Field(default_factory=uuid4)

class InvoiceUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    amount: Optional[int] = None
    status: Optional[str] = None
    date: Optional[date] = None

    class Config:
        from_attributes = True
