from fastapi import APIRouter,Depends,HTTPException
from app.models.models import SchemaRegistry
from sqlalchemy.orm import Session
from app.schemas.entity import SchemaRegistry as SchemaRegisterySchema
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger

API_NAME = "Schema Registry Api"
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

@router.post("/schemaregistry/create", status_code=201, response_model=None)
async def Creates_a_schemaregistery(schema_info: SchemaRegisterySchema, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):

    """
          {
          "schema_registry_host": "string",
          "schema_registry_port": int,
          "schema_name": "string",

        }
    """
    try:
        # schemas_fields = json.dumps(schema_info.schemas_fields)
        schema_registery_model = SchemaRegistry()

        schema_registery_model.schema_registry_host = schema_info.schema_registry_host
        schema_registery_model.schema_registry_port = schema_info.schema_registry_port
        schema_registery_model.schema_auth_type_id = schema_info.schema_auth_type_id

        db.add(schema_registery_model)
        db.commit()
        schemaregistery_dict = {
            # "schema_info_id":schema_model.id,
            "schema_registry_host": schema_info.schema_registry_host,
            "schema_registry_port": schema_info.schema_registry_port,
            "schema_auth_type_id": schema_info.schema_auth_type_id,
            "created_by": "Prodapt",
            "updated_by": "Prodapt",


        }
        logger.info(f'schemaregistery_dict: {schemaregistery_dict}')
        return schemaregistery_dict,successful_response(201)
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


@router.get("/schemaregistry/{register_id}", status_code=200)
async def Read_a_schemaregistery(register_id: str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        SchemaRegistry_model = db.query(SchemaRegistry).filter(SchemaRegistry.id == int(register_id)).first()
        logger.info(f'SchemaRegistry_model_obj: {SchemaRegistry_model}')
        schema_info_dict = {
                        "id":SchemaRegistry_model.id,
                        "schema_registry_host": SchemaRegistry_model.schema_registry_host,
                        "schema_registry_port": SchemaRegistry_model.schema_registry_port,
                        "schema_auth_type_id": SchemaRegistry_model.schema_auth_type_id,
                        "created_by":SchemaRegistry_model.created_by,
                        "updated_by":SchemaRegistry_model.updated_by,
                        "created_datetime":SchemaRegistry_model.created_datetime,
                        "updated_datetime":SchemaRegistry_model.updated_datetime
                           }

        logger.info(f"schema_info_dict: {schema_info_dict}")
        return schema_info_dict
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


@router.get("/schemaregistry/all_records", status_code=200)
async def Lists_all_the_Schemasregistery( db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        SchemaRegistry_model_list = db.query(SchemaRegistry).all()
        logger.info(f"SchemaRegistry_model_list: {SchemaRegistry_model_list}")
        schema_list = []
        for values in SchemaRegistry_model_list:
            schema_registery_dict = {
                            "id":values.id,
                            "schema_registry_host": values.schema_registry_host,
                            "schema_registry_port": values.schema_registry_port,
                            "schema_auth_type_id": values.schema_auth_type_id,
                            "created_by":values.created_by,
                            "updated_by":values.updated_by,
                            "created_datetime":values.created_datetime,
                            "updated_datetime":values.updated_datetime
            }
            schema_list.append(schema_registery_dict)
        schema_dict={"schemas":schema_list}
        logger.info(f'schema_list: {schema_list}')
        return schema_dict
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


@router.put("/schemaregistry/{SchemaName}")
async def updates_a_schemaregistery(SchemaName: str,schema_info: SchemaRegisterySchema,db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        schema_model = db.query(SchemaRegistry).filter(SchemaRegistry.schema_name == SchemaName).first()

        if schema_model is None:
            raise http_exception()

        schema_dict = {
            "schema_registry_host": schema_info.schema_registry_host,
            "schema_registry_port": schema_info.schema_registry_port,
            "schema_name": schema_info.schema_name,
        }
        logger.info(schema_dict)

        schema_model.schema_registry_host = schema_info.schema_registry_host
        schema_model.schema_registry_port = schema_info.schema_registry_port
        schema_model.schema_name = schema_info.schema_name
        db.add(schema_model)
        db.commit()
        return schema_dict,successful_response(200)
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


@router.delete("/schemaregistry/{SchemaName}")
async def Deletes_a_schemaregistery(SchemaName: str,db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        schema_model = db.query(SchemaRegistry).filter(SchemaRegistry.schema_name == SchemaName).delete()
        if schema_model is None:
            raise http_exception()

        db.commit()

        return successful_response(204)
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")
