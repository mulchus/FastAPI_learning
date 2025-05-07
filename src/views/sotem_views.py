from datetime import datetime

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, model_validator
from typing_extensions import Self


fake_db = {}

router = APIRouter()


class Sotem(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None

    @model_validator(mode='after')
    def verify_title(self) -> Self:
        if self.title == 'string':
            raise ValueError("Title don't may be 'string'")
        return self


@router.put("/sotems/{sotem_id}/{ext_value}")
def update_sotem(ext_value: int, sotem_id: str, sotem: Sotem) -> Sotem:
    print(f'{ext_value=} ')

    json_compatible_item_data = jsonable_encoder(sotem)
    print(sotem)
    print(json_compatible_item_data)

    # fake_db[sotem_id] = json_compatible_item_data
    fake_db[sotem_id] = sotem
    # return fake_db
    return fake_db[sotem_id]  # in DB saved as Sotem instance
    # return sotem
