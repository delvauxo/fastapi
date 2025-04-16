from sqlalchemy.orm import Session
from app.models.revenue import Revenue
from app.schemas.revenue import RevenueUpdate

def update_revenue(db: Session, month: str, revenue_data: RevenueUpdate):
    db_revenue = db.query(Revenue).filter(Revenue.month == month).first()
    if not db_revenue:
        return None

    update_data = revenue_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_revenue, key, value)

    db.commit()
    db.refresh(db_revenue)
    return db_revenue