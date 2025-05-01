import os.path
from enum import Enum

from typing import Any, Annotated
from fastapi import (
    FastAPI,
    Request,
    Response,
    status,
    Form,
    File,
    UploadFile,
    Depends,
    HTTPException,
    Header,
    Query,
    Path,
)
from pydantic import BaseModel, EmailStr
from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
    HTMLResponse,
    PlainTextResponse,
)
from fastapi.exceptions import (
    RequestValidationError,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.security import OAuth2PasswordBearer

from calc_views import router as calc_router
from item_views import router as item_router
from totem_views import router as totem_router
from sotem_views import router as sotem_router
from users.views import router as user_router
from model_views import router as model_router
from security_views import router as security_router

from starlette.exceptions import HTTPException as StarletteHTTPException

# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])  # add path dependencies for all routes
app = FastAPI()
app.include_router(user_router, tags=["users"])
app.include_router(model_router, tags=["models"])
app.include_router(calc_router, tags=["calc"])
app.include_router(item_router, prefix="/items", tags=["items"])
app.include_router(totem_router, tags=["totems"])
app.include_router(sotem_router, tags=["sotems"])
app.include_router(security_router, tags=["security"])


# it's for first example
# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}
# CommonsDep = Annotated[dict, Depends(common_parameters)]



# it's for first example
# @app.get("/users-dep/")
# # async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
# async def read_items(commons: CommonsDep):
#     return commons


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


@app.get("/portal2", response_model=None)  # without Response type check
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return {"message": "Here's your interdimensional portal."}


# class UserIn(BaseModel):
#     username: str
#     password: str
#     email: EmailStr
#     full_name: str | None = None
# class UserOut(BaseModel):
#     username: str
#     email: EmailStr
#     full_name: str | None = None
# class UserInDB(BaseModel):
#     username: str
#     hashed_password: str
#     email: EmailStr
#     full_name: str | None = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print(f"User saved! ..not really, hashed_password: {hashed_password}")
    print(user_in_db)
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


# получение информации из файла
@app.get("/files/{file_path:path}")
async def read_file_or_dir(file_path: str):
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return {"file_path": file_path, "data": f.read(200)}
    elif os.path.isdir(file_path):
        return {"file_path": file_path, "files": os.listdir(file_path)}
    return {"file_path": file_path, "exists": False}


@app.get(
    "/keyword-weights/",
    response_model=dict[str, float],
    status_code=status.HTTP_226_IM_USED,
    response_description="Not Successful Response (Joke)",
)
async def read_keyword_weights():
    return {"foo": 2.3, "bar": "3.4"}


@app.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]):
    return {"username": username}


@app.post("/files/")
async def create_files(
    # files: Annotated[list[bytes], File()]
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/files2/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


@app.post("/uploadfiles/")
async def create_upload_files(
    # files: list[UploadFile]
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile")
    ],
):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/files2/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input name="fileb" type="file">
<input name="token" type="text">
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@app.get("/hello")
async def root():
    # return {"message": "Hello World"}
    return 545121.34


@app.get("/hello/{name}")
async def read_unicorn(
        name: Annotated[str, Path(pattern="^[a-zA-Zа-яА-Я]{2,30}$")],
):
    if not isinstance(name, str):
        raise UnicornException(name=name)
    return {"massage": f"Hello, {name.title()}"}


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/names/", name="hello123")
async def start(args: str = "World"):
    names = [name.strip().title() for name in args.split()]
    return {"message": f"Hello {', '.join(names)}"}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# @app.exception_handler(StarletteHTTPException)
# async def http_exception_handler(request, exc):
#     return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
#
#
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print(f"OMG! The client sent invalid data!: {exc}")
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
