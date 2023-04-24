import datetime
import logging
import json
from json import JSONDecodeError
from fastapi import Depends, HTTPException, APIRouter, Path
from app.models.models import FedKafkaBuses,SchemaRegistry,SchemasInfo,StatusEnum
from app.models.models import TopicSchemaAssociation as SchemaTopicAssociation
from app.models.models import FedKafkaTopics as KafkaTopics
from sqlalchemy.orm import Session
from sqlalchemy import exc
from app.schemas.schema_info_schema import SchemaInfo as SchemaInfoSchema
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
import fastavro
from app.api.utils.utils import infer_avro_schema
#from fastapi_pagination import Page, Params, paginate
from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger
from fastapi.responses import JSONResponse
from app.responses.return_api_responses import unauthorized_responses, Unexpected_error_responses,bad_request_responses,Resource_conflict_responses
from app.responses.schema_topic_return_response import schema_post_create_response, get_all_schema_response, Get_all_schema_Successful_Response, Schema_Post_Successful_Response, no_schema_found
from app.api.utils.utils import gen_random_string

API_NAME = "Schema API"
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

from app.responses.schema_topic_return_response import schema_post_create_response, get_all_schema_response, Get_all_schema_Successful_Response
api_router = APIRouter()

#Schema Info CRUD Starts
@api_router.post("/schemas", responses={**Schema_Post_Successful_Response, **bad_request_responses, **unauthorized_responses,
                           **Resource_conflict_responses,
                           **Unexpected_error_responses})
async def Creates_a_schema(schema_info: SchemaInfoSchema, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        # schemas_fields = json.dumps(schema_info.schemas_fields)
        schema_definition = schema_info.definition
        logger.info(f'schema definition is : {schema_definition}')
        if schema_definition:
            logger.info(f'Validating schema definition is valid or not')
            str_to_dict_schema = json.loads(schema_definition.replace("'", '"'))
            logger.info(f'schema type after converstion - {type(str_to_dict_schema)}')
            try:
                if fastavro.parse_schema(str_to_dict_schema):
                    logger.info("Valid Schema, proceeding...")
            except Exception as e:
                logger.error(f'Not a valid schema - {str(e)}')
                return {"status_code": 422, "status_message": "Invalid schema in schema definition"}
        else:
            logger.info('schema definition is empty')
        schema_model = SchemasInfo()
        schema_model.schema_name = schema_info.name
        schema_model.schema_type = schema_info.type
        schema_model.definition = schema_info.definition
        schema_model.revisionId = gen_random_string(8)
        schema_model.revisionCreateTime = datetime.datetime.now()

        db.add(schema_model)
        db.commit()

        response = schema_post_create_response(schema_model)
        return response
    except exc.SQLAlchemyError as e:
        logger.info("Data Base Connection Error")
        logger.debug(e)
        raise Exception("DataBase Connection Error", e)
    except Exception as er:
        error = {
            {
                "error": {
                    "code": 500,
                    "message": f"Error Occurred in {str(er)}",
                    "status": "string",
                    "details": {
                        "reason": "Error",
                        "type": "Unexpected error"
                    }
                }
            }
        }
        return JSONResponse(content=error, status_code=500)


@api_router.get("/schemas/{SchemaName}", responses={**Schema_Post_Successful_Response, **unauthorized_responses, **no_schema_found,  **Unexpected_error_responses})
async def Read_a_schema(SchemaName: str=Path(..., description="Name of the schema"), db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    schema_info_model = db.query(SchemasInfo).filter(
        SchemasInfo.schema_name == SchemaName).first()
    try:
        if schema_info_model:
            response = schema_post_create_response(schema_info_model)
            return response
        else:
            error = {
                "error": {
                    "code": 404,
                    "message": "Schema object does not exist in database with given SchemaName.",
                    "status": "error",
                    "details": {
                        "reason": "Schema object does not exist in database with given SchemaName.",
                        "type": "invalid_parameter"
                    }
                }
            }
            logger.info('No Record Found In DB')
            return JSONResponse(content=error, status_code=404)
    except exc.SQLAlchemyError as e:
        logger.info("Data Base Connection Error")
        logger.debug(e)
        raise Exception("DataBase Connection Error", e)
    except Exception as er:
        error = {
            {
                "error": {
                    "code": 500,
                    "message": f"Error Occurred in {str(er)}",
                    "status": "string",
                    "details": {
                        "reason": "Error",
                        "type": "Unexpected error"
                    }
                }
            }
        }
        return JSONResponse(content=error, status_code=500)


@api_router.get("/schemas", responses={**Get_all_schema_Successful_Response, **unauthorized_responses,  **Unexpected_error_responses})
async def Lists_all_the_Schemas(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        SchemaInfo_model_list = db.query(SchemasInfo).all()

        if SchemaInfo_model_list:
            response = get_all_schema_response(SchemaInfo_model_list)
        else:
            error = {
                "error": {
                    "code": 404,
                    "message": "Item not found",
                    "status": "error",
                    "details": {
                        "reason": "Item not found",
                        "type": "invalid_parameter"
                    }
                }
            }
            return JSONResponse(content=error, status_code=404)
        return response
    except Exception as e:
        logger.error(f'Error occurred - {str(e)}')


@api_router.put("/schemas/update_new_schema/{schema_id}", include_in_schema=False, responses={**Schema_Post_Successful_Response, **bad_request_responses, **unauthorized_responses,
                           **Resource_conflict_responses,
                           **Unexpected_error_responses})
async def make_old_schemas_info_active_create_new_schema_with_definition(schema_id: int, schema_info_obj: SchemaInfoSchema, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        schema_info = db.query(SchemasInfo).filter(SchemasInfo.id == schema_id).first()

        schema_updated_info = schema_info
        schema_updated_info.definition = schema_info_obj.definition
        db.add(schema_updated_info)
        db.commit()
        response = schema_post_create_response(schema_updated_info)
        return response
    except Exception as e:
        print("Error occurred ", str(e))


@api_router.delete("/schemas/{SchemaName}", responses={**bad_request_responses, **unauthorized_responses, **Unexpected_error_responses})
async def Deletes_a_schema(SchemaName: str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        schema_model = db.query(SchemasInfo).filter(SchemasInfo.schema_name == SchemaName).all()

        if len(schema_model) > 0:
            for record in schema_model:
                schema_topic_association_objects = db.query(SchemaTopicAssociation).filter(SchemaTopicAssociation.schemas_info_id == record.id).all()
                for each_record in schema_topic_association_objects:
                    topics_model_records = db.query(KafkaTopics).filter(KafkaTopics.id == each_record.kafka_topics_id).all()
                    for each_topic in topics_model_records:
                        db.delete(each_topic)
                        db.commit()
                    db.delete(each_record)
                    db.commit()
                db.delete(record)
                db.commit()
            logger.info('Deleted Record Successfully')
            res = {f"Record Deleted Successfully SchemaName : {SchemaName}"}
        else:
            error = {
                "error": {
                    "code": 404,
                    "message": "Item not found",
                    "status": "error",
                    "details": {
                        "reason": "Item not found",
                        "type": "invalid_parameter"
                    }
                }
            }
            logger.info('No Record Found In DB')
            return JSONResponse(content=error, status_code=404)
        return res

    except exc.SQLAlchemyError as e:
        logger.info("Data Base Connection Error")
        logger.debug(e)
        raise Exception("DataBase Connection Error", e)
    except Exception as er:
        error = {
            {
                "error": {
                    "code": 500,
                    "message": f"Error Occurred in {str(er)}",
                    "status": "string",
                    "details": {
                        "reason": "Error",
                        "type": "Unexpected error"
                    }
                }
            }
        }
        return JSONResponse(content=error, status_code=500)


@api_router.get("/schemas/validate/{schema}", responses={**unauthorized_responses,  **Unexpected_error_responses})
async def validate_schema(schema: str, current_user: TokenPayload = Depends(get_current_user)):
    try:
        str_to_dict_schema = json.loads(schema.replace("'", '"'))
        if fastavro.parse_schema(str_to_dict_schema):
            return {"status_message": "Valid Schema", "status_code": 200}
        else:
            return {"status_message": "Not Vaild Schema", "status_code": 200}
    except JSONDecodeError:
        return {"status_message": "schema must be a key-value pair", "status_code": 422}
    except Exception as e:
        return {"status_message": "schema should contain require fields - name, type, fields", "status_code": 422}



@api_router.get("/schemas/generate/{SchemaName}/{message}", responses={**unauthorized_responses,  **Unexpected_error_responses})
async def generate_schema(SchemaName: str, message: str, current_user: TokenPayload = Depends(get_current_user)):
     try:
         data = json.loads(message.replace("'", '"'))
         if data:
             avro_schema = infer_avro_schema(data, SchemaName)
             return {"status_code": 200, "type": "AVRO", "definition": avro_schema}
         else:
             return {"status_message": "Message is empty"}
     except JSONDecodeError:
         return {"status_message": "schema must be a key-value pair", "status_code": 422}
     except Exception as e:
         return {"status_message": "Error while generating schema", "status_code": 500}

