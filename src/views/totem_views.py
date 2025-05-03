# from datetime import datetime, time, timedelta
from enum import Enum
from typing import Union  # Annotated,

from fastapi import APIRouter, HTTPException, status  # Query, Path, Body, Header, Cookie,
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel  # , Field, HttpUrl


router = APIRouter()


class Totem(BaseModel):
    name: str = ""
    description: str = ""
    price: float = 0
    tax: float = 10.5  # default value
    tags: list[str] = []


totems = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.get(
    "/totems/{totem_id}",
    response_model=Totem,
    response_model_include={"name", "price", "description", "tags"},
    response_model_exclude_unset=True,
)
async def read_totem(totem_id: str) -> Totem:
    if totem_id not in totems:
        raise HTTPException(status_code=404, detail={"message": "Totem not found"})
    return Totem(**totems[totem_id])  # type: ignore


@router.put("/totems3/{totem_id}", response_model=Totem)
async def update_totem(totem_id: str, totem: Totem) -> Totem:
    update_totem_encoded = jsonable_encoder(totem)
    totems[totem_id] = update_totem_encoded
    print(update_totem_encoded)
    print(totems)
    # return {"success": True, "data": totems}  # not return a dict because response_model = Totem
    return Totem(**totems[totem_id])  # type: ignore


@router.patch("/totems4/{totem_id}", response_model=Totem)
async def update_totem4(totem_id: str, totem: Totem) -> Totem:
    stored_totem_data = totems[totem_id]
    stored_totem_model = Totem(**stored_totem_data)  # type: ignore[arg-type]
    print(stored_totem_model)
    update_data = totem.dict(exclude_unset=True)
    print(update_data)
    updated_totem = stored_totem_model.model_copy(update=update_data)
    print(updated_totem)
    totems[totem_id] = jsonable_encoder(updated_totem)
    return updated_totem


new_totems = [
    {"name": "Foo", "description": "The bartenders Foo", "price": 50.2},
    {
        "name": "Bar",
        "description": "The bartenders Bar",
        "price": 62,
        "tax": 20.2,
    },
    {
        "name": "Baz",
        "description": "The bartenders Baz",
        "price": 50.2,
        "tax": 10.5,
        "tags": [],
    },
]


@router.get(
    "/new-totems/",
    response_model=list[Totem],
    # response_model_include={"name", "description"},   # don't work
    # response_model_exclude={"tax", "tags", "price"},  # don't work
    response_model_exclude_unset=True,  # work
)
async def read_totems() -> list[dict]:  # -> list[Totem]:
    # return [
    #     Totem(name="Portal Gun", price=42.0),
    #     Totem(name="Plumbus", price=32.0),
    # ]
    # return {"success": True, "data": "Portal Gun"}  # raise exception ResponseValidationError
    return new_totems


class Tags(Enum):
    totems = "totems"
    users = "users"


@router.get("/totems/", tags=[Tags.totems], operation_id="get_totems_easy")
async def get_totems() -> list[str]:
    return ["Portal gun", "Plumbus"]


@router.get("/users/", tags=[Tags.users], deprecated=True)
async def read_users() -> list[str]:
    return ["Rick", "Morty"]


@router.post(
    "/totems/",
    response_model=Totem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a totem, yeah",
    response_description="The created totem",
    # description="Create a totem with all the information,"
    #             " name, description, price, tax and a set of unique tags",
)
async def create_totem(totem: Totem) -> Totem:
    """Create a totem with all the information.

    Params:
    - **name**: each totem must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this totem
    """
    totem.price += totem.tax
    return totem
    # return {"success": True, "data": totem}  # raise exception ResponseValidationError


class BaseTotem(BaseModel):
    description: str
    totem_type: str


class CarTotem(BaseTotem):
    totem_type: str = "car"


class PlaneTotem(BaseTotem):
    totem_type: str = "plane"
    size: int


totems2 = {
    "totem1": {"description": "All my friends drive a low rider", "totem_type": "car"},
    "totem2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "totem_type": "plane",
        "size": 5,
    },
}


@router.get("/totems2/{totem_id}", response_model=Union[PlaneTotem, CarTotem])
async def read_totem2_1(totem_id: str) -> Totem:
    return Totem(**totems2[totem_id])  # type: ignore
