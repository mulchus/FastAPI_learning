from fastapi import APIRouter, Query, Path
from pydantic import BaseModel
from typing import Annotated
import re


router = APIRouter()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@router.post("/post/")
async def create_item(item: Item):
    item.name = item.name.strip().title()
    item.description = (item.description + ", ") * 3
    return item


@router.put("/update/{item_id}")
async def update_item(
    item_id: Annotated[int, Path(ge=0, le=50)],
    item: Item,
    q: Annotated[
        str | None, Query(max_length=15, min_length=3)
    ] = None,  # regex="^fixedquery$"
):
    item.name = item.name.strip().title()
    item.description = ((item.description + ", ") * 5).rstrip(", ")
    if item.tax:
        item.price += item.tax
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q[::-1]})
    return result


@router.get("/")
def list_items():
    return [
        "item1",
        "item2",
        "item3",
    ]


@router.get("/latest/")
def read_last_item(q: Annotated[list[str], Query()] = ("foo", "bar")):
    return {"item_id": "latest", "q": q}


@router.get("/{item_id}/")  # example: http://127.0.0.1:8000/items-new/1/?q=qwerty
def read_item(
    item_id: int,
    q: Annotated[
        str | None,
        Query(
            regex="[a-zA-Zйцуке][^0-9]123$",
        ),
    ] = None,
):
    return {"item_id": item_id, "q": q} if q else {"item_id": item_id}


@router.get("/var2/{item_id}")  # !! automatically delete '/'
# example http://127.0.0.1:8000/items-new/var2/1?q=%27asdass%27&short=0
async def read_item(
    item_id: str, q: Annotated[str | None, Query()] = "fixedquery", short: bool = False
):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
