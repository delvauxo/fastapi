from pydantic import BaseModel

class RevenueBase(BaseModel):
    month: str
    revenue: int

class RevenueCreate(RevenueBase):
    pass

class Revenue(RevenueBase):
    class Config:
        orm_mode = True