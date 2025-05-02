from typing import Annotated, Any

from fastapi import APIRouter, Body

from users import crud
from users.schemas import User
from views.item_views import Item


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/")
def create_user(user: User) -> dict[str, Any]:
    return crud.create_user(user=user)


@router.get("-hello/")
def hello(name: str = "World") -> dict[str, str]:
    name = name.strip().title()
    return {"message": f"Hello {name}"}


@router.get("/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False,
) -> dict[str, Any]:
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"},
        )
    return item


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    user: User,
    importance: Annotated[int, Body()],
    q: str | None = None,
) -> dict[str, Any]:
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    if q:
        results.update({"q": q})
    return results
