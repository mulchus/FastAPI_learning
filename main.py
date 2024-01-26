from typing import Annotated
from fastapi import FastAPI, Path
from pydantic import BaseModel, EmailStr


app = FastAPI()


class User(BaseModel):
    name: str
    email: EmailStr


class Items(BaseModel):
    var1: int
    var2: int
    

@app.get("/")
def start():
    return {"message2": "Hello World"}


@app.post("/user/")
def create_user(user: User):
    return {"name": user.name.title(), "email": user.email}


@app.post("/calc/add/")
def add(items: Items):
    return {
        "a": items.var1,
        "b": items.var2,
        "sum": items.var1 + items.var2
    }


@app.post("/calc2/add/")
def add2(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "sum": a + b
    }


@app.get("/calc3/add/{a} {b}")
# def add3(a: int, b: int):
def add3(a: Annotated[int, Path(ge=0, le=1_000)], b: Annotated[int, Path(ge=0, le=10)]):
    return {
        "a": a,
        "b": b,
        "sum": a + b
    }


@app.get("/hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}"}


@app.get("/items/")
def list_items():
    return [
        "item1",
        "item2",
        "item3",
    ]
    
    
@app.get("/items/latest/")
def read_last_item():
    return {"item_id": "latest"}


@app.get("/items/{item_id}/")
def read_item(item_id: int):
    return {"item_id": item_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
    