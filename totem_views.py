from datetime import datetime, time, timedelta
from fastapi import APIRouter, Query, Path, Body, Header, Cookie
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated


router = APIRouter()


class Totem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = 10.5  # default value
    tags: list[str] = []


totems = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.get(
    "/totems/{totem_id}", response_model=Totem, response_model_exclude_unset=True
)
async def read_totem2(totem_id: str):
    return totems[totem_id]


@router.get("/totems/", response_model=list[Totem])
async def read_totems():  # -> list[Totem]:
    return [
        Totem(name="Portal Gun", price=42.0),
        Totem(name="Plumbus", price=32.0),
    ]
    # return {"success": True, "data": "Portal Gun"}  # raise exception ResponseValidationError


@router.post("/totems/", response_model=Totem)
async def create_totem(totem: Totem):  # -> Totem:
    return totem
    # return {"success": True, "data": totem}  # raise exception ResponseValidationError
