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


@router.get("/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
