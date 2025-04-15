from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.revenue import Revenue as RevenueModel
from app.schemas.revenue import Revenue
from app.core.database import get_db

router = APIRouter()

@router.get("/revenue/", response_model=list[Revenue])
def get_all_revenue(db: Session = Depends(get_db)):
    return db.query(RevenueModel).all()

@router.get("/revenue/{month}", response_model=Revenue)
def get_one_revenue(month: str, db: Session = Depends(get_db)):
    revenue = db.query(RevenueModel).filter(RevenueModel.month == month).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Revenue for the month not found")
    return revenue