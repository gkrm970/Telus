from typing import Any

from fastapi.routing import APIRouter
from fastapi.param_functions import Depends

from app import schemas
from app.api import deps


router = APIRouter()



@router.post("/", response_model=schemas.Msg, status_code=201)
def default_endpoint(
    msg: schemas.Msg,
) -> Any:
    return {"msg": "It works!"}
