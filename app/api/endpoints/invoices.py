from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, String, cast
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID 

from app.core.database import get_db
from app.models.invoice import Invoice as InvoiceModel
from app.models.customer import Customer as CustomerModel
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceLatest, InvoicePagesResponse, Invoice
from app.crud import invoice as crud_invoice

router = APIRouter()

# Doit correspondre au nombre d'item par page côté frond pour ne pas créer de désalignement.
ITEMS_PER_PAGE = 6 

# Récupère toutes les factures
@router.get("/invoices", response_model=list[InvoiceLatest])
def get_all_invoices(
    db: Session = Depends(get_db),
    query: str = Query("", alias="query"),
    page: int = Query(1, alias="page"),
    limit: int = Query(ITEMS_PER_PAGE, alias="limit")
):
    # Calculer l'offset
    offset = (page - 1) * limit

    # Construire la requête avec filtre, limite et offset
    invoices_query = db.query(InvoiceModel, CustomerModel)\
        .join(CustomerModel, InvoiceModel.customer_id == CustomerModel.id)\
        .filter(
            (CustomerModel.name.ilike(f"%{query}%")) |
            (CustomerModel.email.ilike(f"%{query}%")) |
            (InvoiceModel.status.ilike(f"%{query}%")) |
            (func.cast(InvoiceModel.amount, String).ilike(f"%{query}%"))
        )\
        .order_by(InvoiceModel.date.desc(), InvoiceModel.id.desc())\
        .limit(limit)\
        .offset(offset)

    # Récupérer les résultats
    all_invoices = invoices_query.all()

    # Vérifier si aucun résultat n'est trouvé
    if not all_invoices:
        return []

    # Retourner les résultats formatés
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
        for invoice, customer in all_invoices
    ]

# Récupère le nombre total de pages.
@router.get("/invoices/pages", response_model=InvoicePagesResponse)
def get_invoices_pages(
    db: Session = Depends(get_db),
    query: str = Query("", alias="query")
):
    total_items = db.query(InvoiceModel)\
        .join(CustomerModel, InvoiceModel.customer_id == CustomerModel.id)\
        .filter(
            (CustomerModel.name.ilike(f"%{query}%")) |
            (CustomerModel.email.ilike(f"%{query}%")) |
            (InvoiceModel.status.ilike(f"%{query}%")) |
            (func.cast(InvoiceModel.amount, String).ilike(f"%{query}%"))
        ).count()

    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    return InvoicePagesResponse(totalPages=total_pages)

# Récupère le nombre total de factures.
@router.get("/invoices/count", response_model=dict)
def get_invoices_count(query: Optional[str] = "", db: Session = Depends(get_db)):
    try:
        # Construire la requête principale
        base_query = db.query(InvoiceModel.id)

        # Appliquer les filtres si la query est présente
        if query:
            base_query = base_query.filter(
                (InvoiceModel.status.ilike(f"%{query}%")) |
                (cast(InvoiceModel.amount, String).ilike(f"%{query}%"))
            )
        
        # Retourner le nombre total
        return {"count": base_query.count()}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Récupère les montants des factures payées et en attente.
@router.get("/invoices/status", response_model=dict)
def get_invoices_status(db: Session = Depends(get_db)):
    try:
        paid_amount = db.query(func.sum(InvoiceModel.amount)) \
                        .filter(InvoiceModel.status == 'paid') \
                        .scalar() or 0
        pending_amount = db.query(func.sum(InvoiceModel.amount)) \
                        .filter(InvoiceModel.status == 'pending') \
                        .scalar() or 0
        return {"paid": paid_amount, "pending": pending_amount}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Récupère les 5 dernières factures avec les informations du client associé.
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

# Récupère une facture spécifique par son identifiant.
@router.get("/invoices/{invoice_id}", response_model=Invoice)
def get_one_invoice(invoice_id: UUID, db: Session = Depends(get_db)):
    invoice = db.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

# Crée une nouvelle facture.
@router.post("/invoices/", response_model=Invoice)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    return crud_invoice.create_invoice(db=db, invoice=invoice)

# Met à jour une facture existante.
@router.patch("/invoices/{invoice_id}", response_model=Invoice)
def update_invoice(invoice_id: str, invoice: InvoiceUpdate, db: Session = Depends(get_db)):
    updated_invoice = crud_invoice.update_invoice(db=db, invoice_id=invoice_id, invoice_data=invoice)
    if not updated_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated_invoice