from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.invoice import Invoice as InvoiceModel
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, Invoice
from app.crud import invoice as crud_invoice

router = APIRouter()

@router.get("/invoices/", response_model=list[Invoice])
def get_all_invoices(db: Session = Depends(get_db)):
    return db.query(InvoiceModel).all()

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