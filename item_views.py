from fastapi import APIRouter


router = APIRouter()


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
