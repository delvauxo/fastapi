from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, User
from app.crud import user as crud_user

router = APIRouter()

@router.get("/users/", response_model=list[User])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()

@router.get("/users/{user_id}", response_model=User)
def get_one_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)

@router.patch("/users/{user_id}", response_model=User)
def update_user(user_id: str, user: UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud_user.update_user(db=db, user_id=user_id, user_data=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user