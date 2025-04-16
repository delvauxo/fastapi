from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = Customer(
        name=customer.name, 
        email=customer.email, 
        image_url=customer.image_url
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: str, customer_data: CustomerUpdate):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not db_customer:
        return None

    update_data = customer_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer
