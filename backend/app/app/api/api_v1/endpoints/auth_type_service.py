from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
from app.schemas.entity import AuthSettings as AuthTypeSchema
from app.crud.crud_auth_type import CrudAuthType

from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger


API_NAME = "Auth Type Service"

logger_conf = [
    {
        "handler_name": settings.LOGGER_HANDLER_NAME,
        "log_level": settings.TINAA_LOG_LEVEL,
        "log_format": settings.LOGGER_FORMAT,
        "date_format": settings.LOGGER_DATE_FORMAT,
        "app_code": settings.LOGGER_APP_CODE,
        "app_name": API_NAME,
    }
]
logger = get_app_logger(log_conf=logger_conf, logger_name=API_NAME)
router = APIRouter()


@router.post("/auth_type/insert", status_code=201, response_model=None)
def insert_auth_type(auth_type_info: AuthTypeSchema, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        logger.info('Inside auth_type insert ')
        create_auth_type_info = CrudAuthType.create(db=db, auth_type_schema=auth_type_info)
        response = create_auth_type_info
        logger.info(response)
        return response
    except Exception as e:
        return str(e)


@router.put("/auth_type/update/{auth_type_info_id}", status_code=201, response_model=None)
def update_auth_type(auth_type_info_id: int, auth_type_info: AuthTypeSchema, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):

    create_kafka_info = CrudAuthType.update_auth_type_info(db=db, auth_type_info_id=auth_type_info_id,
                                                     auth_type_info=auth_type_info)

    response = {"status": "Record Updated Successfully", "status_code": 201}
    logger.info(response)
    return response
  
@router.get("/auth_type/list_of_auth_type_info_records", status_code=200)
async def get_all_auth_type_records(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    get_all_auth_type_data = CrudAuthType.get_all_auth_type_info(db=db)
    return get_all_auth_type_data


@router.get("/auth_type/get_record_by/{auth_type_name}/{kafka_bus_name}", status_code=200)
def get_data_with_id(auth_type_name: str,kafka_bus_name:str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    get_auth_type_data_with_id = CrudAuthType.get_data_by_id(db=db, auth_type_info_name=auth_type_name,fed_kafka_bus_name_info=kafka_bus_name)
    return get_auth_type_data_with_id


@router.delete("/auth_type/delete/{auth_type_id}")
async def delete_auth_type_info(auth_type_id: int, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    delete_auth_type_info_data_with_id = CrudAuthType.delete_auth_type_data_by_id(db=db, auth_type_id=auth_type_id)
    return {"response": "Record Deleted Successfully", "status_code": 200}

