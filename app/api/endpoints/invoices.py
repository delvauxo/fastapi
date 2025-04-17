from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.invoice import Invoice as InvoiceModel
from app.models.customer import Customer as CustomerModel
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceLatest, Invoice
from app.crud import invoice as crud_invoice

router = APIRouter()

@router.get("/invoices/", response_model=list[Invoice])
def get_all_invoices(db: Session = Depends(get_db)):
    return db.query(InvoiceModel).all()

@router.get("/invoices/latest", response_model=list[InvoiceLatest])
def get_latest_invoices(db: Session = Depends(get_db)):
    latest_invoices = db.query(InvoiceModel, CustomerModel)\
                        .join(CustomerModel, InvoiceModel.customer_id == CustomerModel.id)\
                        .order_by(InvoiceModel.date.desc())\
                        .limit(5)\
                        .all()

    if not latest_invoices:
        raise HTTPException(status_code=404, detail="No invoices found.")

    return [
        {
            "id": invoice.id,
            "customer_id": invoice.customer_id,
            "status": invoice.status,
            "amount": invoice.amount,
            "name": customer.name,
            "email": customer.email,
            "image_url": customer.image_url,
            "date": invoice.date.isoformat(),
        }
        for invoice, customer in latest_invoices  # Décomposition du tuple
    ]

@router.get("/invoices/{invoice_id}", response_model=Invoice)
def get_one_invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/invoices/", response_model=Invoice)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    return crud_invoice.create_invoice(db=db, invoice=invoice)

@router.patch("/invoices/{invoice_id}", response_model=Invoice)
def update_invoice(invoice_id: str, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    updated_invoice = crud_invoice.update_invoice(db=db, invoice_id=invoice_id, invoice_data=invoice)
    if not updated_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated_invoice