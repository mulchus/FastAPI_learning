from typing import Annotated
from fastapi import APIRouter, Path
from pydantic import BaseModel


router = APIRouter(prefix="/calc")


class Items(BaseModel):
    var1: int
    var2: int


@router.post("/add/")
def add(items: Items):
    return {
        "a": items.var1,
        "b": items.var2,
        "sum": items.var1 + items.var2
    }


@router.post("2/add/")
def add2(a: int, b: int):
    return {
        "a": a,
        "b": b,
        "sum": a + b
    }


@router.get("3/add/{a} {b}")
# def add3(a: int, b: int):
def add3(a: Annotated[int, Path(ge=0, le=1_000)], b: Annotated[int, Path(ge=0, le=10)]):
    return {
        "a": a,
        "b": b,
        "sum": a + b
    }
