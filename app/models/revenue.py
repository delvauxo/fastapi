from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Revenue(Base):
    __tablename__ = "revenue"

    month = Column(String, primary_key=True, unique=True, nullable=False)
    revenue = Column(Integer, nullable=False)
