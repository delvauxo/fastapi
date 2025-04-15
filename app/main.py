from fastapi import FastAPI
from app.api.endpoints import users, invoices, customers, revenue

app = FastAPI()

# Inclure les routes utilisateur et factures séparément
app.include_router(users.router)  
app.include_router(invoices.router)
app.include_router(customers.router)
app.include_router(revenue.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
