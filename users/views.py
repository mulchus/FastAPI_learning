from fastapi import APIRouter
from users.schemas import User
from users import crud

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
def create_user(user: User):
    return crud.create_user(user=user)
    

@router.get("-hello/")
def hello(name: str = "World"):
    name = name.strip().title()
    return {"message": f"Hello {name}"}
