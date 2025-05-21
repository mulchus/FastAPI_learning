import os.path
from enum import Enum
from typing import Annotated, Any

from exceptions import UnicornError
from fastapi import APIRouter, Depends, File, Form, Path, Request, Response, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, EmailStr


router = APIRouter()


@router.get("/hello")
async def root(request: Request) -> Any:
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(',')[0]
    else:
        client_ip = request.client.host if request.client else "unknown"
    return {"message": f"Hello World from client ip {client_ip}"}
    # return 545121.34


@router.get("/hello/{name}")
async def read_unicorn(
    name: Annotated[str, Path(pattern="^[a-zA-Zа-яА-Я]{2,30}$")],
) -> dict[str, str]:
    if not isinstance(name, str):
        print('Catch in read_unicorn url')
        raise UnicornError(name=name)
    return {"message": f"Hello, {name.title()}"}


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100) -> dict[str, Any]:
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[dict, Depends(common_parameters)]


@router.get("/users-dep/")
# async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
async def read_items(commons: CommonsDep) -> CommonsDep:
    return commons


@router.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


@router.get("/portal2", response_model=None)  # without Response type check
async def get_portal2(teleport: bool = False) -> Response | dict:
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


def fake_password_hasher(raw_password: str) -> str:
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn) -> UserInDB:
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print(f"User saved! ..not really, hashed_password: {hashed_password}")
    print(user_in_db)
    return user_in_db


@router.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn) -> UserInDB:
    user_saved = fake_save_user(user_in)
    return user_saved


# получение информации из файла
@router.get("/files/{file_path:path}")
async def read_file_or_dir(file_path: str) -> dict[str, Any]:
    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            return {"file_path": file_path, "data": f.read(200)}
    elif os.path.isdir(file_path):
        return {"file_path": file_path, "files": os.listdir(file_path)}
    return {"file_path": file_path, "exists": False}


@router.get(
    "/keyword-weights/",
    response_model=dict[str, float],
    status_code=status.HTTP_226_IM_USED,
    response_description="Not Successful Response (Joke)",
)
async def read_keyword_weights() -> dict[str, Any]:
    return {"foo": 2.3, "bar": "3.4"}


@router.post("/login/")
async def login(username: Annotated[str, Form()], password: Annotated[str, Form()]) -> dict[str, str]:
    return {"username": username}


@router.post("/files/")
async def create_files(
    # files: Annotated[list[bytes], File()]
    files: Annotated[list[bytes], File(description="Multiple files as bytes")],
) -> dict[str, list[int]]:
    return {"file_sizes": [len(file) for file in files]}


@router.post("/files2/")
async def create_file(
    file: Annotated[bytes, File()],
    fileb: Annotated[UploadFile, File()],
    token: Annotated[str, Form()],
) -> dict[str, Any]:
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


@router.post("/uploadfiles/")
async def create_upload_files(
    # files: list[UploadFile]
    files: Annotated[
        list[UploadFile], File(description="Multiple files as UploadFile"),
    ],
) -> dict[str, list[str | None]]:
    return {"filenames": [file.filename for file in files]}


@router.get("/")
async def main_path() -> HTMLResponse:
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


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@router.get("/names/", name="hello123")
async def start(args: str = "World") -> dict[str, str]:
    names = [name.strip().title() for name in args.split()]
    return {"message": f"Hello {', '.join(names)}"}


@router.get("/models/{model_name}")
async def get_model(model_name: ModelName) -> dict[str, str]:
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
