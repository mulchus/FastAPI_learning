from datetime import datetime

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

fake_db = {}

router = APIRouter()


class Sotem(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


@router.put("/sotems/{id}")
def update_sotem(id: str, sotem: Sotem):
    # не ясно зачем!!! если хэндлер все равно возвращает json
    json_compatible_item_data = jsonable_encoder(sotem)
    fake_db[id] = json_compatible_item_data
    print(sotem)
    print(json_compatible_item_data)
    # fake_db[id] = sotem
    # return fake_db
    # return fake_db[id]
    return sotem
