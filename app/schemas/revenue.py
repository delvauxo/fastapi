from pydantic import BaseModel
from typing import Optional

class RevenueBase(BaseModel):
    month: str
    revenue: int

class RevenueCreate(RevenueBase):
    pass

class Revenue(RevenueBase):
    class Config:
        from_attributes = True

class RevenueUpdate(BaseModel):
    revenue: Optional[int] = None

    class Config:
        from_attributes = True