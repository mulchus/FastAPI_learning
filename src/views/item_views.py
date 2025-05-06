from datetime import datetime, time, timedelta
from typing import Annotated, Any, Generator
from uuid import UUID

from database import get_aioredis
from fastapi import APIRouter, Body, Cookie, Depends, Header, HTTPException, Path, Query
from pydantic import AfterValidator, BaseModel, Field, HttpUrl
from redis import Redis  # type: ignore[import-untyped]


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


router = APIRouter()


class FirstItem(BaseModel):
    title: str
    size: int = 10


@router.post("/item_class/")
async def view_item_class(item: FirstItem) -> FirstItem:
    item.title = item.title.title()
    item.size += 50
    return item


@router.put("/dates/{item_id}")
async def read_dates_items(
    item_id: UUID,  # например 6ffefd8e-a018-e811-bbf9-60f67727d806
    start_datetime: Annotated[datetime, Query()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
) -> dict[str, Any]:
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


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: str = Field(
        default="",
        title="The description of the item",
        max_length=15,
        examples=["Its a good item"],
    )
    price: float = Field(
        gt=0,
        description="The price must be greater than zero",
        examples=[35.4],
    )
    tax: float = Field(default=0, examples=[3.2])
    tags: set[str] = set()
    image: list[Image] | None = None

    model_config = {"extra": "forbid"}  # запретить иные кроме печечисленных


class ShortOffer(BaseModel):
    name: str
    description: str | None = None
    price: float


class Offer(ShortOffer):
    items: list[Item]


@router.post("/offers/")
async def create_offer(offer: Offer) -> dict[str, Any]:
    offer.price = sum(item.price for item in offer.items)
    rez_offer = offer.model_dump()
    rez_offer["extra"] = "extra_field"  # this field ignore in return
    return rez_offer


@router.post("/short_offers_info/", response_model=ShortOffer)
async def create_short_offer(offer: Offer) -> ShortOffer:
    offer.price = sum(item.price for item in offer.items)
    return ShortOffer(**offer.model_dump())


@router.post("/images/multiple/")
async def create_multiple_images(images: list[Image]) -> list[Image]:
    return images


@router.post("/index-weights/")
async def create_index_weights(
    weights: dict[int, float],
) -> dict[int, float]:
    return weights


@router.post("/create_redis_item/")
async def create_redis_item(item: Item, redis: Redis = Depends(get_aioredis)) -> dict[str, Any]:  # noqa B008
    item.name = item.name.strip().title()
    item.description = ((item.description + ", ") * 3).rstrip(", ")
    await redis.set(item.name, item.price)
    return {
        "status": "ok",
        item.name: item.price,
    }


@router.get("/get_redis_item/{item_key}")
async def get_redis_item(item_key: str, redis: Redis = Depends(get_aioredis)) -> dict[str, Any]:  # noqa B008
    value = await redis.get(item_key)
    if not value:
        raise HTTPException(status_code=404, detail=f"Key {item_key} is absent.")
    return {
        "status": "ok",
        item_key: value,
    }


@router.delete("/delete_redis_item/")
async def pop_redis_item(item_key: str, redis: Redis = Depends(get_aioredis)) -> dict[str, Any]:  # noqa B008
    value = await redis.get(item_key)
    if not value:
        raise HTTPException(status_code=404, detail=f"Key {item_key} is absent.")
    print(f"Value for '{item_key}': {value}")
    await redis.delete(item_key)
    print(f"Key '{item_key}' has been deleted.")
    return {
        "status": "delete",
        item_key: value,
    }


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
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    item.name = item.name.strip().title()
    item.description = ((item.description + ", ") * 5).rstrip(", ")
    if item.tax:
        item.price += item.tax
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q[::-1]})
    return result


@router.put("/put/{item_id}")
async def put_item(
    item_id: int,
    item: Annotated[Item, Body(embed=True)],
) -> dict[str, Any]:  # в json добавлен главный уровень item
    results = {"item_id": item_id, "item": item}
    return results


@router.get("/")
def list_items(
    q: Annotated[
        tuple[str, str], Query(alias="item-query"),
    ] = (  # <item-query> instead <q>
        "default",
        "query",
    ),
) -> list[str]:
    return [x for x in q] + ["string1", "string2"]


@router.get("/cookie/")
async def read_cookie_items(
    ads_id: Annotated[str | None, Cookie()] = None,
) -> dict[str, str | None]:
    return {"ads_id": ads_id}


@router.get("/header/")
async def read_header_items(
    user_agent: Annotated[str | None, Header()] = None,
) -> dict[str, str | None]:
    return {"User-Agent": user_agent}


@router.get("/book/{book_")
async def read_book_items(
    ads_id: Annotated[str | None, Cookie()] = None,
) -> dict[str, str | None]:
    return {"ads_id": ads_id}


@router.get("/latest/")
def read_last_item(
    q: Annotated[
        tuple[str, str],
        Query(
            title="Query string",
            description="Query string for the items to search in the database that have a good match",
        ),
    ] = ("foo", "bar"),
) -> dict[str, Any]:
    return {"item_id": "latest", "q": q}


async def verify_token(x_token: Annotated[str, Header()]) -> None:
    if x_token != "fake_super_secret_token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]) -> str:
    if x_key != "fake_super_secret_key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


# get some items with chek toke and key
@router.get(
    "/items-path-depends/", dependencies=[Depends(verify_token), Depends(verify_key)],
)
async def read_items_path_depends() -> list[dict[str, str]]:
    return [{"item": "Foo"}, {"key": "Bar"}]


def check_valid_id(item_id: str) -> str:
    prefixes = ("isbn-", "imdb-")
    if not item_id.startswith(prefixes):
        raise ValueError(f"Invalid item_id format, it must start with {prefixes}")
    return item_id


@router.get("/{item_id}")  # example: http://127.0.0.1:8000/items-new/1/?q=qwerty
def get_item(
    item_id: Annotated[
        str,
        AfterValidator(check_valid_id),
    ],
    q: Annotated[str | None, Query(pattern="[a-zA-Zйцуке][^0-9]123$")] = None,
) -> dict[str, str]:
    if item_id == "isbn-abc":
        raise HTTPException(status_code=418, detail="Nope! I don't like ABC.")
    return {"item_id": item_id, "q": q} if q else {"item_id": item_id}


@router.get("/var2/{item_id}")  # !! automatically delete '/'
# example http://127.0.0.1:8000/items-new/var2/1?q=%27asdass%27&short=0
async def read_item(
    item_id: str,
    q: Annotated[str | None, Query()] = "fixedquery",
    short: bool = False,
) -> dict[str, str]:
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"},
        )
    return item


# it's for second example
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@router.get("/items-dep/")
# it's for null and first examples
# async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
# async def read_items(commons: CommonsDep):
# it's for second example
async def read_items(
    commons: Annotated[CommonQueryParams, Depends()],
) -> dict[str, Any]:
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})  # type: ignore[dict-item]
    return response


class OwnerError(Exception):
    pass


data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal_gun": {"description": "Gun to create portals", "owner": "Rick"},
}


def get_username() -> Generator[str, Any, None]:
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@router.get("/yield-exc/{item_id}")
def get_item_by_username(
    item_id: str, username: Annotated[str, Depends(get_username)],
) -> dict[str, str]:
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item
