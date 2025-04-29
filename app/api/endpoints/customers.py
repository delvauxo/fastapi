from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID 

from app.core.database import get_db
from app.models.customer import Customer as CustomerModel
from app.models.invoice import Invoice as InvoiceModel
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPagesResponse, Customer
from app.crud import customer as crud_customer

router = APIRouter()

# Permet de garder un fallback côté backend.
ITEMS_PER_PAGE = 10

# Récupère tous les clients.
@router.get("/customers", response_model=list)
def get_customers(
    query: str = Query("", alias="query"),
    page: int = Query(1, alias="page"),
    db: Session = Depends(get_db),
    limit: int = Query(ITEMS_PER_PAGE, alias="limit", le=50)
):  
    # Calcul de l'offset pour la pagination.
    offset = (page - 1) * limit

    # Construire la requête principale avec les filtres.
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
     .limit(limit)

    # Exécuter la requête.
    all_customers = customers_query.all()

    # Vérifier si aucun client n'est trouvé.
    if not all_customers:
        return []

    # Retourner les résultats.
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

# Récupère le nombre total de pages.
@router.get("/customers/pages", response_model=CustomerPagesResponse)
def get_customers_pages(
    db: Session = Depends(get_db),
    query: str = Query("", alias="query"),
    limit: int = Query(ITEMS_PER_PAGE, alias="limit", le=50)
):
    total_items = db.query(CustomerModel)\
        .filter(
            (CustomerModel.name.ilike(f"%{query}%")) |
            (CustomerModel.email.ilike(f"%{query}%"))
        ).count()

    total_pages = (total_items + limit - 1) // limit

    return CustomerPagesResponse(totalPages=total_pages)

# Récupère la liste de tous les clients.
@router.get("/customers/all", response_model=List[Customer])
def get_all_customers(db: Session = Depends(get_db)):
    customers = db.query(CustomerModel).order_by(CustomerModel.name.asc()).all()
    return customers

# Récupère le nombre total de clients.
@router.get("/customers/count", response_model=dict)
def get_customer_count(query: Optional[str] = "", db: Session = Depends(get_db)):
    try:
        # Construire la requête principale.
        base_query = db.query(CustomerModel.id).distinct()

        # Appliquer les filtres si la query est présente.
        if query:
            base_query = base_query.filter(
                (CustomerModel.name.ilike(f"%{query}%")) |
                (CustomerModel.email.ilike(f"%{query}%"))
            )
        
        # Compter le nombre total de clients correspondants.
        count = base_query.count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Récupère un client spécifique par son identifiant.
@router.get("/customers/{customer_id}", response_model=Customer)
def get_one_customer(customer_id: UUID, db: Session = Depends(get_db)):
    try:
        customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Crée un nouveau client.
@router.post("/customers", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    try:
        # Appeler la fonction CRUD
        return crud_customer.create_customer(db=db, customer=customer)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Met à jour un client existant.
@router.patch("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    updated_customer = crud_customer.update_customer(db=db, customer_id=customer_id, customer_data=customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer