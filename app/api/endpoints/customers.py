from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, String, case, cast, or_
from typing import List, Optional
from uuid import UUID 

from app.core.database import get_db
from app.models.customer import Customer as CustomerModel
from app.models.invoice import Invoice as InvoiceModel
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer
from app.crud import customer as crud_customer

router = APIRouter()

ITEMS_PER_PAGE = 6

@router.get("/customers", response_model=list)
def get_customers(
    query: str = Query("", alias="query"),
    page: int = Query(1, alias="page"),
    db: Session = Depends(get_db),
):
    # Calcul de l'offset pour la pagination
    offset = (page - 1) * ITEMS_PER_PAGE

    # Construire la requête principale avec les filtres
    customers_query = db.query(
        CustomerModel.id,
        CustomerModel.name,
        CustomerModel.email,
        CustomerModel.image_url,
        func.count(InvoiceModel.id).label("total_invoices"),
        func.coalesce(func.sum(InvoiceModel.amount).filter(InvoiceModel.status == "pending"), 0).label("total_pending"),
        func.coalesce(func.sum(InvoiceModel.amount).filter(InvoiceModel.status == "paid"), 0).label("total_paid"),
    ).outerjoin(InvoiceModel, InvoiceModel.customer_id == CustomerModel.id)\
     .group_by(CustomerModel.id, CustomerModel.name, CustomerModel.email, CustomerModel.image_url)\
     .filter(
         (CustomerModel.name.ilike(f"%{query}%")) |
         (CustomerModel.email.ilike(f"%{query}%"))
     )\
     .order_by(CustomerModel.name.asc())\
     .offset(offset)\
     .limit(ITEMS_PER_PAGE)

    # Exécuter la requête
    all_customers = customers_query.all()

    # Vérifier si aucun client n'est trouvé
    if not all_customers:
        return []

    # Retourner les résultats
    return [
        {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "image_url": customer.image_url,
            "total_invoices": customer.total_invoices,
            "total_pending": customer.total_pending,
            "total_paid": customer.total_paid,
        }
        for customer in all_customers
    ]

# Récupère la liste de tous les clients.
@router.get("/customers/all", response_model=List[Customer])
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(CustomerModel).order_by(CustomerModel.name.asc()).all()
    return customers

# Récupère le nombre total de clients.
@router.get("/customers/count", response_model=dict)
def get_customer_count(query: Optional[str] = "", db: Session = Depends(get_db)):
    q = db.query(
        CustomerModel.id
    ).outerjoin(InvoiceModel, InvoiceModel.customer_id == CustomerModel.id
    ).group_by(
        CustomerModel.id,
        CustomerModel.name,
        CustomerModel.email,
        CustomerModel.image_url
    )
    
    if query:
        filter_condition = or_(
            CustomerModel.name.ilike(f"%{query}%"),
            CustomerModel.email.ilike(f"%{query}%"),
            cast(func.count(InvoiceModel.id), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((InvoiceModel.status == 'pending', InvoiceModel.amount), else_=0)), 0), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((InvoiceModel.status == 'paid', InvoiceModel.amount), else_=0)), 0), String).ilike(f"%{query}%")
        )
        q = q.having(filter_condition)
    
    # Le count() ici retourne le nombre de groupes (donc de clients)
    count = q.count()
    return {"count": count}


# Récupère un client spécifique par son identifiant.
@router.get("/customers/{customer_id}", response_model=Customer)
def get_one_customer(customer_id: UUID, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Crée un nouveau client.
@router.post("/customers/", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return crud_customer.create_customer(db=db, customer=customer)

# Met à jour un client existant.
@router.patch("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    updated_customer = crud_customer.update_customer(db=db, customer_id=customer_id, customer_data=customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer