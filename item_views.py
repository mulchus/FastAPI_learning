from datetime import datetime, time, timedelta
from fastapi import APIRouter, Query, Path, Body
from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated
from uuid import UUID

import re


router = APIRouter()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=15,
        examples=["Its a good item"],
    )
    price: float = Field(
        gt=0, description="The price must be greater than zero", examples=[35.4]
    )
    tax: float | None = Field(default=None, examples=[3.2])
    tags: set[str] = set()
    image: list[Image] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


@router.put("/dates/{item_id}")
async def read_items(
    item_id: UUID,  # например 6ffefd8e-a018-e811-bbf9-60f67727d806
    start_datetime: Annotated[datetime | None, Body()] = None,
    end_datetime: Annotated[datetime | None, Body()] = None,
    repeat_at: Annotated[time | None, Body()] = None,
    process_after: Annotated[timedelta | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@router.post("/offers/")
async def create_offer(offer: Offer):
    offer.price = sum(item.price for item in offer.items)
    return offer


@router.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


@router.post("/index-weights/")
async def create_index_weights(
    weights: dict[int, float]  # dict have "int" keys and float values
):
    return weights


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
        str | None,
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
            max_length=15,
            min_length=3,
            # regex="^fixedquery$",
            deprecated=True,  # отметка, что параметр устарел
        ),
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


@router.put("/update2/{item_id}/")
async def update_item_2(
    item_id: int,
    item: Annotated[
        Item,
        Body(
            embed=True,  # в json добавлен главный уровень item
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 135.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
            # examples=[
            #     {
            #         "name": "Foo",
            #         "description": "A very nice Item",
            #         "price": 55.5,
            #         "tax": 3.2,
            #     },
            #     {
            #         "name": "Bar",
            #         "price": "35.4",
            #     },
            #     {
            #         "name": "Baz",
            #         "price": "thirty five point four",
            #     },
            # ],
        ),
    ],
    q: str | None = None,
):
    item.name = item.name.strip().title()
    item.description = ((item.description + ", ") * 5).rstrip(", ")
    if item.tax:
        item.price += item.tax
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q[::-1]})
    return result


@router.put("/put/{item_id}")
async def update_item(
    item_id: int, item: Annotated[Item, Body(embed=True)]
):  # в json добавлен главный уровень item
    results = {"item_id": item_id, "item": item}
    return results


@router.get("/")
def list_items(
    q: Annotated[list[str], Query(alias="<item-query> instead <q>")] = (
        "default",
        "query",
    )
):
    return [x for x in q] + ["string1", "string^"]


@router.get("/latest/")
def read_last_item(
    q: Annotated[
        list[str],
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
        ),
    ] = ("foo", "bar")
):
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
