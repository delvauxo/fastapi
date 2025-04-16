from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.customer import Customer as CustomerModel
from app.schemas.customer import CustomerCreate, CustomerUpdate, Customer
from app.crud import customer as crud_customer

router = APIRouter()

@router.get("/customers/", response_model=list[Customer])
def get_all_customers(db: Session = Depends(get_db)):
    return db.query(CustomerModel).all()

@router.get("/customers/{customer_id}", response_model=Customer)
def get_one_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/customers/", response_model=Customer)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return crud_customer.create_customer(db=db, customer=customer)

@router.patch("/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, customer: CustomerUpdate, db: Session = Depends(get_db)):
    updated_customer = crud_customer.update_customer(db=db, customer_id=customer_id, customer_data=customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer