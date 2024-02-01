from datetime import datetime, time, timedelta
from fastapi import APIRouter, Query, Path, Body, Header, Cookie
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated


router = APIRouter()


class Totem(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


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
