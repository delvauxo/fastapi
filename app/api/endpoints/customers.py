from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, cast, String, or_
from typing import List, Optional
from uuid import UUID 

from app.core.database import get_db
from app.models.customer import Customer as CustomerModel
from app.models.invoice import Invoice
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerAggregated, Customer
from app.crud import customer as crud_customer

router = APIRouter()

ITEMS_PER_PAGE = 6

@router.get("/customers/", response_model=List[CustomerAggregated])
def get_customers(query: Optional[str] = "", page: int = 1, db: Session = Depends(get_db)):
    # On construit la requête avec agrégation et GROUP BY sur tous les champs non agrégés
    q = db.query(
        CustomerModel.id.label("id"),
        CustomerModel.name.label("name"),
        CustomerModel.email.label("email"),
        CustomerModel.image_url.label("image_url"),
        func.count(Invoice.id).label("total_invoices"),
        func.coalesce(func.sum(case((Invoice.status == 'pending', Invoice.amount), else_=0)), 0).label("total_pending"),
        func.coalesce(func.sum(case((Invoice.status == 'paid', Invoice.amount), else_=0)), 0).label("total_paid")
    ).outerjoin(Invoice, Invoice.customer_id == CustomerModel.id
    ).group_by(
        CustomerModel.id,
        CustomerModel.name,
        CustomerModel.email,
        CustomerModel.image_url
    )
    
    if query:
        # On construit une condition qui vérifie le nom, l'email et les agrégats convertis en chaîne
        filter_condition = or_(
            CustomerModel.name.ilike(f"%{query}%"),
            CustomerModel.email.ilike(f"%{query}%"),
            cast(func.count(Invoice.id), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((Invoice.status == 'pending', Invoice.amount), else_=0)), 0), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((Invoice.status == 'paid', Invoice.amount), else_=0)), 0), String).ilike(f"%{query}%")
        )
        # Comme les agrégats sont dans le GROUP BY, on applique le filtre avec HAVING
        q = q.having(filter_condition)
    
    q = q.offset((page - 1) * ITEMS_PER_PAGE).limit(ITEMS_PER_PAGE)
    
    results = q.all()
    
    aggregated_customers = []
    # Chaque résultat est une ligne contenant les colonnes demandées
    for row in results:
        aggregated_customers.append({
            "id": row.id,
            "name": row.name,
            "email": row.email,
            "image_url": row.image_url,
            "total_invoices": row.total_invoices,
            "total_pending": row.total_pending,
            "total_paid": row.total_paid,
        })
    return aggregated_customers

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
    ).outerjoin(Invoice, Invoice.customer_id == CustomerModel.id
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
            cast(func.count(Invoice.id), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((Invoice.status == 'pending', Invoice.amount), else_=0)), 0), String).ilike(f"%{query}%"),
            cast(func.coalesce(func.sum(case((Invoice.status == 'paid', Invoice.amount), else_=0)), 0), String).ilike(f"%{query}%")
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