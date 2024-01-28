from enum import Enum
from fastapi import APIRouter


router = APIRouter(prefix="/models", tags=["models"])


class ModelName(Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@router.get("/{model_name}")
async def get_model(model_name: ModelName):

    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
