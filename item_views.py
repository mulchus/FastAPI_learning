from fastapi import APIRouter


router = APIRouter(prefix="/items")


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


@router.get("/{item_id}/")
def read_item(item_id: int):
    return {"item_id": item_id}
