from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.revenue import update_revenue
from app.models.revenue import Revenue as RevenueModel
from app.schemas.revenue import RevenueUpdate, Revenue
from app.core.database import get_db

router = APIRouter()

@router.get("/revenue/", response_model=list[Revenue])
def get_all_revenue(db: Session = Depends(get_db)):
    return db.query(Revenue).order_by(Revenue.month).all()


@router.get("/revenue/{month}", response_model=Revenue)
def get_one_revenue(month: str, db: Session = Depends(get_db)):
    revenue = db.query(RevenueModel).filter(RevenueModel.month == month).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Revenue for the month not found")
    return revenue

@router.patch("/revenue/{month}", response_model=Revenue)
def patch_revenue(month: str, revenue_data: RevenueUpdate, db: Session = Depends(get_db)):
    updated_revenue = update_revenue(db=db, month=month, revenue_data=revenue_data)
    if not updated_revenue:
        raise HTTPException(status_code=404, detail="Revenue for the month not found")
    return updated_revenue