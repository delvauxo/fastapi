from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    # Vérifier s'il y a une erreur concernant le paramètre 'limit'
    for error in exc.errors():
        if error.get("loc") and error.get("loc")[-1] == "limit":
            return JSONResponse(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "The value of the 'limit' parameter must be less than or equal to 50. Please check your input."
                },
            )
    # Sinon, renvoyer un message d'erreur générique
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Some parameters are invalid. Please check your entries."},
    )
