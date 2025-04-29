from fastapi import FastAPI
from app.core.exception_handlers import custom_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from app.api.endpoints import users, invoices, customers, revenue

app = FastAPI()

# Enregistre le gestionnaire d’exception global pour RequestValidationError
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)

# Inclusion des routes
app.include_router(users.router)
app.include_router(invoices.router)
app.include_router(customers.router)
app.include_router(revenue.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
