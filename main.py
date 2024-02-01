import os.path

from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

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


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    return user


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
