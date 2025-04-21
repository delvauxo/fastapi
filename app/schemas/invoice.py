from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional
from datetime import date as Date, date


class InvoiceBase(BaseModel):
    customer_id: UUID
    amount: int
    status: str
    date: date

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: UUID = Field(default_factory=uuid4)

# Nouveau schéma pour l'endpoint "invoices/latest"
class InvoiceLatest(Invoice):
    name: str
    email: str
    image_url: str

# Nouveau schéma pour l'endpoint "invoices/pages"
class InvoicePagesResponse(BaseModel):
    totalPages: int

class InvoiceUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    amount: Optional[int] = None
    status: Optional[str] = None
    date: Optional[Date] = None

    class Config:
        from_attributes = True
