from fastapi import APIRouter
from pydantic import BaseModel


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
async def update_item(item_id: int, item: Item):
    item.name = item.name.strip().title()
    item.description = ((item.description + ", ") * 5).rstrip(", ")
    if item.tax:
        item.price += item.tax
    return {"item_id": item_id, **item.model_dump()}


@router.get("/")
def list_items():
    return [
        "item1",
        "item2",
        "item3",
    ]


@router.get("/latest/")
def read_last_item():
    return {"item_id": "latest"}


@router.get("/{item_id}/")  # example: http://127.0.0.1:8000/items-new/1/?q=qwerty
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q} if q else {"item_id": item_id}


@router.get("/var2/{item_id}")  # !! automatically delete '/'
# example http://127.0.0.1:8000/items-new/var2/1?q=%27asdass%27&short=0
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
