import os.path

from typing import Any
from fastapi import FastAPI, Response
from pydantic import BaseModel, EmailStr
from fastapi.responses import JSONResponse, RedirectResponse

from calc_views import router as calc_router
from item_views import router as item_router
from totem_views import router as totem_router
from users.views import router as user_router
from model_views import router as model_router


app = FastAPI()
app.include_router(user_router, tags=["users"])
app.include_router(model_router, tags=["models"])
app.include_router(calc_router, tags=["calc"])
app.include_router(item_router, prefix="/items-new", tags=["items-new"])
app.include_router(totem_router, tags=["totems"])


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


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


@app.get("/", name="hello123")
async def start(args: str = "World"):
    names = [name.strip().title() for name in args.split()]
    return {"message": f"Hello {', '.join(names)}"}


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
