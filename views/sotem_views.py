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
def update_sotem(sotem_id: str, sotem: Sotem) -> Sotem:
    # не ясно зачем!!! если хэндлер все равно возвращает json
    json_compatible_item_data = jsonable_encoder(sotem)
    fake_db[sotem_id] = json_compatible_item_data
    print(sotem)
    print(json_compatible_item_data)
    # fake_db[sotem_id] = sotem
    # return fake_db
    # return fake_db[sotem_id]
    return sotem
