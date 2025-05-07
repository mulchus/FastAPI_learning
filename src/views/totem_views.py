from enum import Enum
from typing import Any, Union  # Annotated,

from database import PlaneTotemDB, Session
from fastapi import APIRouter, HTTPException, status  # Query, Path, Body, Header, Cookie,
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel  # , Field, HttpUrl
from sqlalchemy import desc, update
from tools import async_time_calc

from views.sotem_views import router as sotem_router


router = APIRouter()
router.include_router(sotem_router, prefix='/sotem')


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


@router.post(
    "/totems/",
    # response_model=Totem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a totem, yeah",
    response_description="The created totem",
    # description="Create a totem with all the information,"
    #             " name, description, price, tax and a set of unique tags",
)
@async_time_calc
async def create_totem(totem: Totem) -> dict[str, str | Any]:
    """Create a totem with all the information.

    Params:
    - **name**: each totem must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this totem
    """
    with Session(autoflush=True) as session:
        new_plane_totem = PlaneTotemDB(
            **totem.model_dump(exclude={'tags'}),
        )
        session.add(new_plane_totem)
        # эксперименты с настройкой autoflush и измерением времени передачи одного или всех значений
        # спойлер: время выполнения ручки практически одинаково в обоих случаяъ
        # getting_new_plane_totem = session.query(PlaneTotemDB).order_by(desc(PlaneTotemDB.id)).first()
        getting_new_plane_totem = session.query(PlaneTotemDB).all()[-1]
        print(f'getting_new_plane_totem {getting_new_plane_totem.__dict__}')
        session.commit()
        # getting2_new_plane_totem = session.query(PlaneTotemDB).order_by(desc(PlaneTotemDB.id)).first()
        getting2_new_plane_totem = session.query(PlaneTotemDB).all()[-1]
        print(f'getting2_new_plane_totem {getting2_new_plane_totem.__dict__}')

        return {
            "message": "plane_totem created",
            "totem": totem.model_dump(),
        }


@router.get(
    "/totems/{totem_name}",
    response_model=Totem,
    response_model_include={"name", "price", "description", "tags"},
    response_model_exclude_unset=True,
)
async def get_totem(totem_name: str) -> Totem:
    with Session() as session:
        totem = session.query(PlaneTotemDB).filter(PlaneTotemDB.name == totem_name).\
            order_by(desc(PlaneTotemDB.id)).first()
        if not totem:
            raise HTTPException(status_code=404, detail={"message": "Totem not found"})
        return totem


@router.put(
    "/totems/{totem_id}",
    # response_model=Totem,
)
async def update_totem(totem_id: str, totem: Totem) -> dict[str, str | Any]:
    with Session() as session:
        # totem_from_db = session.query(PlaneTotemDB).filter(PlaneTotemDB.id == totem_id).first()
        # if not totem_from_db:
        #     raise HTTPException(status_code=404, detail={"message": f"Totem with id {totem_id} not found"})

        # проверка наличия объекта через запрос на обновление
        stmt = update(PlaneTotemDB).filter(PlaneTotemDB.id == totem_id).values(totem.model_dump(exclude={'tags'}))
        result = session.execute(stmt)
        if not result.rowcount:  # если нет ни одной обновленной строки, значит объектов не существует
            raise HTTPException(status_code=404, detail={"message": f"Totem with id {totem_id} not found"})
        session.commit()
        return {
            "message": "plane_totem updated",
            "totem": totem,
        }


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
async def get_totems(param1: str) -> list[str]:
    # query param1 is required
    return ["Portal gun", "Plumbus"]


@router.get("/users/", tags=[Tags.users], deprecated=True)
async def read_users() -> list[str]:
    return ["Rick", "Morty"]


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
