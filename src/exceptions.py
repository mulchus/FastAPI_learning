from fastapi import Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse


class UnicornError(Exception):
    def __init__(self, name: str):
        self.name = name


async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


async def validation_exception_handler2(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def unicorn_exception_handler(request: Request, exc: UnicornError) -> JSONResponse:
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )
