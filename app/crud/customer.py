from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

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