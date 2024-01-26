from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

from calc_views import router as calc_router
from item_views import router as item_router

app = FastAPI()
app.include_router(calc_router, tags=["calc"])
app.include_router(item_router, prefix="/items-new", tags=["items-new"])


class User(BaseModel):
    name: str
    email: EmailStr
    

@app.get("/")
def start():
    return {"message2": "Hello World"}


@app.post("/user/")
def create_user(user: User):
    return {"name": user.name.title(), "email": user.email}


@app.get("/user-hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
    