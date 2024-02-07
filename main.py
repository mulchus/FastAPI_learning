import os.path
import asyncio

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
)  # , HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)

from calc_views import router as calc_router
from item_views import router as item_router
from totem_views import router as totem_router
from sotem_views import router as sotem_router
from users.views import router as user_router
from model_views import router as model_router


app = FastAPI()
app.include_router(user_router, tags=["users"])
app.include_router(model_router, tags=["models"])
app.include_router(calc_router, tags=["calc"])
app.include_router(item_router, prefix="/items-new", tags=["items-new"])
app.include_router(totem_router, tags=["totems"])
app.include_router(sotem_router, tags=["sotems"])

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


# it's for first example
# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}
# CommonsDep = Annotated[dict, Depends(common_parameters)]


# it's for second example
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items-dep/")
# it's for null and first examples
# async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
# async def read_items(commons: CommonsDep):
# it's for second example
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
    # return commons


# it's for first example
# @app.get("/users-dep/")
# # async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
# async def read_items(commons: CommonsDep):
#     return commons


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items-path-dep/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items_path_dep():
    return [{"item": "Foo"}, {"item": "Bar"}]


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


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10, reverse: bool = False):
    return (
        fake_items_db[skip : skip + limit][::-1]
        if reverse
        else fake_items_db[skip : skip + limit]
    )


# @app.get("/", name="hello123")
# async def start(args: str = "World"):
#     names = [name.strip().title() for name in args.split()]
#     return {"message": f"Hello {', '.join(names)}"}


# получение информации из файла
@app.get("/files/{file_path:path}")
async def read_file_or_dir(file_path: str):
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return {"file_path": file_path, "data": f.read(200)}
    elif os.path.isdir(file_path):
        return {"file_path": file_path, "files": os.listdir(file_path)}
    else:
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


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


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


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 3:
        # raise HTTPException(status_code=418, detail="Nope! I don't like 3.")
        raise StarletteHTTPException(status_code=418, detail="Nope! I don't like 3.")
    return {"item_id": item_id}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


class Item(BaseModel):
    title: str
    size: int


@app.post("/items/")
async def create_item(item: Item):
    return item


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
