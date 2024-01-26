from typing import Annotated
from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    # name: str = Field(..., min_length=3, max_length=50)
    name: Annotated[str, MinLen(3), MaxLen(50)]
    email: EmailStr

    