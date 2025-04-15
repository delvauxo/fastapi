from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate

def create_invoice(db: Session, invoice: InvoiceCreate):
    db_invoice = Invoice(
        customer_id=invoice.customer_id,
        amount=invoice.amount,
        status=invoice.status,
        date=invoice.date
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def update_invoice(db: Session, invoice_id: str, invoice_data: InvoiceUpdate):
    db_invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not db_invoice:
        return None

    update_data = invoice_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_invoice, key, value)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice