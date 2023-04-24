import logging
import os
#from app.database.session import engine,Base
#Base.metadata.create_all(bind=engine)
from fastapi import APIRouter, Depends, HTTPException, Path
from app.models.models import FedKafkaBuses,SchemasInfo
from app.models.models import TopicSchemaAssociation as SchemaTopicAssociation
from app.models.models import FedKafkaTopics as KafkaTopics
from sqlalchemy.orm import Session
from sqlalchemy import exc
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
from app.schemas.topic_schema import KafkaTopicSchema
from app.schemas.entity import DiscoveryModuleInternalTopicSchemaAssociation as TopicSchemaAssociationPydantic

from app.responses.return_api_responses import unauthorized_responses, Unexpected_error_responses,bad_request_responses, publish_success_Response, Resource_conflict_responses
from app.responses.schema_topic_return_response import Topic_Put_Successful_Response, topic_put_create_response, get_all_topic_response, Get_all_topic_Successful_Response
from app.schemas.publish_message_schema import Messages, MyResponse
from app.schemas.subscription_schema import team_names, env_names, validate_name
from app.crud.publish_message_service import PublishMessage
from starlette.responses import JSONResponse
from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger

API_NAME = "Topic Service"
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

api_router = APIRouter()
MAX_MESSAGES_TO_PUBLISH = os.getenv('MAX_MESSAGES_TO_PUBLISH')


# Kafka Topics CRUD Starts
@api_router.put("/topics/{TopicName}",
                responses={**Topic_Put_Successful_Response, **bad_request_responses, **unauthorized_responses,
                           **Resource_conflict_responses,
                           **Unexpected_error_responses})
async def Registers_a_topic_under_TINAA_pubsub(kafka_topic_object: KafkaTopicSchema, TopicName: str = Path(...,
                                                                                                           description="Name of the topic. Follow the naming convention <app-team-name>-<environment-name>-<event-name>. Allowed environment names are develop, preprod, qa & prod. App team name examples -> bsaf, naaf & pltf. The three examples are for application teams TINAA Business Services Automation Framework, TINAA Network Applications Automation Framework & TINAA Platform team. If you do no belong to any of the three within TINAA, Please contact dlSDNPlatformSupportDistributionList@telus.com."),
                                               db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    #res = validate_name(TopicName)
    res = True
    kafka_bus_model = db.query(FedKafkaBuses).filter(
    FedKafkaBuses.kafka_host == kafka_topic_object.kafka_bus_name).first()
    try:
        if res:
            if kafka_bus_model:
                kafka_topics_model = KafkaTopics()
                dict_data = kafka_topic_object.__dict__
                logger.info(f'Dict data from topic creation is - {dict_data}')
                logger.info(f'type of schema is - {type(dict_data.get("schemaSettings").schema)}')
                logger.info(f'schema is - {dict_data.get("schemaSettings").schema()}')
                kafka_topics_model.label_key = dict_data.get("labels").key
                kafka_topics_model.label_value = dict_data.get("labels").value
                kafka_topics_model.schema = dict_data.get("schemaSettings").schema_
                kafka_topics_model.encoding = dict_data.get('schemaSettings').encoding
                kafka_topics_model.firstRevisionId = dict_data.get("schemaSettings").firstRevisionId
                kafka_topics_model.lastRevisionId = dict_data.get("schemaSettings").lastRevisionId
                kafka_topics_model.kafka_bus_name = kafka_bus_model.kafka_host
                kafka_topics_model.messageRetentionDuration = dict_data.get("messageRetentionDuration")
                kafka_topics_model.liveDateRetentionDuration = dict_data.get(
                    "retentionSettings").liveDateRetentionDuration
                kafka_topics_model.historicalDataRetentionDuration = dict_data.get(
                    "retentionSettings").historicalDataRetentionDuration
                kafka_topics_model.supportedSubscriptionTypes = dict_data.get("supportedSubscriptionTypes")
                # kafka_topics_model.kafka_bus_id = kafka_bus_model.id
                kafka_topics_model.kafka_topic_name = TopicName

                db.add(kafka_topics_model)
                db.commit()
                logger.info('Created Record Successfully')

                response = topic_put_create_response(kafka_topics_model)
                return response

            else:
                error = {
                    "error": {
                        "code": 404,
                        "message": "Given Kafka Bus Name does not exist in database.",
                        "status": "error",
                        "details": {
                            "reason": "Given Kafka Bus Name does not exist in database.",
                            "type": "invalid_parameter"
                        }
                    }
                }
                logger.info('No Record Found In DB')
                return JSONResponse(content=error, status_code=404)
        else:
            error = {
                "error": {
                    "code": 422,
                    "message": "Subscription name must follow the naming convention: "
                               "<app-team-name>-<environment-name>-<subscription-name>",
                    "example": 'naaf-develop-MEM-NOKIA-Telemetry',
                    "status": "error",
                    "details": {
                        "reason": "Name of the topic. Follow the naming convention "
                                  "<app-team-name>-<environment-name>-<event-name>. Allowed "
                                  f'App-Team-Names Ex: {team_names}, Environment-Names Ex: {env_names}',
                        "type": "invalid_parameter"
                    }
                }
            }
            return JSONResponse(content=error, status_code=422)
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


@api_router.get("/topics/{TopicName}", status_code=200,
                responses={**Topic_Put_Successful_Response, **unauthorized_responses, **Unexpected_error_responses})
async def Returns_a_topic(TopicName: str = Path(...,
                                                description="Name of the topic. Follow the naming convention "
                                                            "<app-team-name>-<environment-name>-<event-name>. Allowed "
                                                            "environment names are develop, preprod, qa & prod. App "
                                                            "team name examples -> bsaf, naaf & pltf. The three "
                                                            "examples are for application teams TINAA Business "
                                                            "Services Automation Framework, TINAA Network "
                                                            "Applications Automation Framework & TINAA Platform team. "
                                                            "If you do no belong to any of the three within TINAA, "
                                                            "Please contact "
                                                            "dlSDNPlatformSupportDistributionList@telus.com."),
                          db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    kafka_topics_model = db.query(KafkaTopics).filter(KafkaTopics.kafka_topic_name == TopicName).first()
    #res = validate_name(TopicName)
    res = True
    try:
        if res:
            if kafka_topics_model:
                response = topic_put_create_response(kafka_topics_model)
                return response
            else:
                error = {
                    "error": {
                        "code": 404,
                        "message": "Given Kafka Bus Name does not exist in database.",
                        "status": "error",
                        "details": {
                            "reason": "Given Kafka Bus Name does not exist in database.",
                            "type": "invalid_parameter"
                        }
                    }
                }
                logger.info('No Record Found In DB')
                return JSONResponse(content=error, status_code=404)
        else:
            error = {
                "error": {
                    "code": 422,
                    "message": "Topic name must follow the naming convention: "
                               "<app-team-name>-<environment-name>-<subscription-name>",
                    "example": 'naaf-develop-MEM-NOKIA-Telemetry',
                    "status": "error",
                    "details": {
                        "reason": "Name of the topic. Follow the naming convention "
                                  "<app-team-name>-<environment-name>-<event-name>. Allowed "
                                  f'App-Team-Names Ex: {team_names}, Environment-Names Ex: {env_names}',
                        "type": "invalid_parameter"
                    }
                }
            }
            return JSONResponse(content=error, status_code=422)
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


@api_router.get("/topics/get_record_by_bus_and_topic_name/{kafka_topic_name}/{kafka_bus_name}",
                responses={**unauthorized_responses, **Unexpected_error_responses}, include_in_schema=False)
async def get_topic_with_bus_name(kafka_topic_name: str, kafka_bus_name: str, db: Session = Depends(get_db)):
    try:
        kafkatopic_model = db.query(KafkaTopics).filter(
            KafkaTopics.kafka_topic_name == kafka_topic_name,
            KafkaTopics.kafka_bus_name == kafka_bus_name,
        ).first()

        if kafkatopic_model is not None:
            kafka_topic_id = kafkatopic_model.id
        else:
            kafka_topic_id = ''
        return kafka_topic_id
    except Exception as e:
        logger.error(f'Error occurred - {str(e)}')


@api_router.get("/topics",
                responses={**Get_all_topic_Successful_Response, **unauthorized_responses, **Unexpected_error_responses})
async def Lists_all_the_topics_available_for_subscription_via_TINAA_pubsub(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        kafka_topics_models_list = db.query(KafkaTopics).all()
        if kafka_topics_models_list:
            response = get_all_topic_response(kafka_topics_models_list)
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


@api_router.patch("/topics/{TopicName}",
                  responses={**Topic_Put_Successful_Response, **bad_request_responses, **unauthorized_responses,
                             **Unexpected_error_responses})
async def Registers_a_topic_under_TINAA_pubsub(kafka_topic_object: KafkaTopicSchema, TopicName: str = Path(...,
                                                                                                           description="Name of the topic. Follow the naming convention <app-team-name>-<environment-name>-<event-name>. Allowed environment names are develop, preprod, qa & prod. App team name examples -> bsaf, naaf & pltf. The three examples are for application teams TINAA Business Services Automation Framework, TINAA Network Applications Automation Framework & TINAA Platform team. If you do no belong to any of the three within TINAA, Please contact dlSDNPlatformSupportDistributionList@telus.com."),
                                               db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    kafka_topics_model = db.query(KafkaTopics).filter(KafkaTopics.kafka_topic_name == TopicName).first()
    #res = validate_name(TopicName)
    res = True
    try:
        if res:
            if kafka_topics_model:
                dict_data = kafka_topic_object.__dict__
                kafka_topics_model.label_key = dict_data.get("labels").key
                kafka_topics_model.label_value = dict_data.get("labels").value
                kafka_topics_model.schema = dict_data.get("schemaSettings").schema_
                kafka_topics_model.encoding = dict_data.get('schemaSettings').encoding
                kafka_topics_model.firstRevisionId = dict_data.get("schemaSettings").firstRevisionId
                kafka_topics_model.lastRevisionId = dict_data.get("schemaSettings").lastRevisionId
                kafka_topics_model.kafka_bus_name = dict_data.get("kafka_bus_name")
                kafka_topics_model.messageRetentionDuration = dict_data.get("messageRetentionDuration")
                kafka_topics_model.liveDateRetentionDuration = dict_data.get(
                    "retentionSettings").liveDateRetentionDuration
                kafka_topics_model.historicalDataRetentionDuration = dict_data.get(
                    "retentionSettings").historicalDataRetentionDuration
                kafka_topics_model.supportedSubscriptionTypes = dict_data.get("supportedSubscriptionTypes")
                # kafka_topics_model.kafka_bus_id = kafka_bus_model.id
                kafka_topics_model.kafka_topic_name = TopicName

                db.add(kafka_topics_model)
                db.commit()
                logger.info('Created Record Successfully')

                response = topic_put_create_response(kafka_topics_model)
                return response

            else:
                error = {
                    "error": {
                        "code": 404,
                        "message": "Given Kafka Bus Name does not exist in database.",
                        "status": "error",
                        "details": {
                            "reason": "Given Kafka Bus Name does not exist in database.",
                            "type": "invalid_parameter"
                        }
                    }
                }
                logger.info('No Record Found In DB')
                return JSONResponse(content=error, status_code=404)
        else:
            error = {
                "error": {
                    "code": 422,
                    "message": "Subscription name must follow the naming convention: "
                               "<app-team-name>-<environment-name>-<subscription-name>",
                    "example": 'naaf-develop-MEM-NOKIA-Telemetry',
                    "status": "error",
                    "details": {
                        "reason": "Name of the topic. Follow the naming convention "
                                  "<app-team-name>-<environment-name>-<event-name>. Allowed "
                                  f'App-Team-Names Ex: {team_names}, Environment-Names Ex: {env_names}',
                        "type": "invalid_parameter"
                    }
                }
            }
            return JSONResponse(content=error, status_code=422)
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


@api_router.delete("/topics/{TopicName}",
                   responses={**bad_request_responses, **unauthorized_responses, **Unexpected_error_responses})
async def Deregisters_a_topic_under_TINAA_pubsub(TopicName: str, db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        kafkatopic_model = db.query(KafkaTopics).filter(KafkaTopics.kafka_topic_name == TopicName).all()
        if len(kafkatopic_model) > 0:
            for record in kafkatopic_model:
                schema_topic_association_objects = db.query(SchemaTopicAssociation).filter(
                    SchemaTopicAssociation.kafka_topics_id == record.id).all()
                for each_record in schema_topic_association_objects:
                    schema_model_records = db.query(SchemasInfo).filter(
                        SchemasInfo.id == each_record.schemas_info_id).all()
                    for each_topic in schema_model_records:
                        db.delete(each_topic)
                        db.commit()
                    db.delete(each_record)
                    db.commit()
                db.delete(record)
                db.commit()

            logger.info('Deleted Record Successfully')
            res = {f"Record Deleted Successfully TopicName : {TopicName}"}
            return res
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


# Kafka Topics CRUD Ends

def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")


@api_router.get("/topics/get_schema_topic_association_details/{relation_id}", include_in_schema=False,
                responses={**unauthorized_responses, **Unexpected_error_responses})
async def get_schema_topic_association_details(relation_id: int, db: Session = Depends(get_db)):
    try:
        each_schema_topic = db.query(SchemaTopicAssociation).filter(SchemaTopicAssociation.id == relation_id).first()
        schema_model = db.query(SchemasInfo).filter(SchemasInfo.id == each_schema_topic.schemas_info_id).first()
        topics_model = db.query(KafkaTopics).filter(KafkaTopics.id == each_schema_topic.kafka_topics_id).first()
        schema_topic_dict = {}
        schema_topic_dict['topic_name'] = topics_model.kafka_topic_name
        schema_topic_dict['messageRetentionDuration'] = topics_model.messageRetentionDuration
        schema_topic_dict['bus_name'] = topics_model.kafka_bus_name
        schema_topic_dict['topic_status'] = topics_model.topic_status
        schema_topic_dict['schema_name'] = schema_model.schema_name
        schema_topic_dict['schema_type'] = schema_model.schema_type
        schema_topic_dict['schema_definition'] = schema_model.definition
        schema_topic_dict['schema_revision_id'] = schema_model.revisionId
        return schema_topic_dict
    except Exception as e:
        logger.error(f'Error occurred - {str(e)}')


@api_router.put(
    "/topics/update_latest_schema_in_topic_schema_association/{old_schemas_info_id}/{latest_schemas_info_id}",
    include_in_schema=False)
async def update_schema_topic_association_to_latest_schema_version(old_schemas_info_id: int,
                                                                   latest_schemas_info_id: int,
                                                                   db: Session = Depends(get_db)):
    try:
        schema_topic_model = db.query(SchemaTopicAssociation).filter(
            SchemaTopicAssociation.schemas_info_id == old_schemas_info_id,
        )
        updated_ids = []
        if schema_topic_model is None:
            schema_topic_model = {}
        else:
            for each_association in schema_topic_model:
                each_association.schemas_info_id = latest_schemas_info_id
                db.add(each_association)
                db.commit()
                updated_ids.append(each_association)

        return updated_ids
    except Exception as e:
        logger.error(f'Error occurred - {str(e)}')


@api_router.get("/topics/topic_schema_associations", responses={**unauthorized_responses, **Unexpected_error_responses})
async def Lists_all_topic_schema_associations(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        logger.info('Fetching all topic-schema associations')
        schema_topic_objects = db.query(SchemaTopicAssociation).all()
        logger.info(f'schema_topic_obj is - {schema_topic_objects}')
        all_schema_topic_object = []
        if schema_topic_objects is not None:
            for each_schema_topic in schema_topic_objects:
                schema_model = db.query(SchemasInfo).filter(SchemasInfo.id == each_schema_topic.schemas_info_id).first()
                topics_model = db.query(KafkaTopics).filter(KafkaTopics.id == each_schema_topic.kafka_topics_id).first()
                schema_topic_dict = {}
                schema_topic_dict['topic_name'] = topics_model.kafka_topic_name
                schema_topic_dict['messageRetentionDuration'] = topics_model.messageRetentionDuration
                schema_topic_dict['bus_name'] = topics_model.kafka_bus_name
                schema_topic_dict['topic_status'] = topics_model.topic_status
                schema_topic_dict['schema_name'] = schema_model.schema_name
                schema_topic_dict['schema_type'] = schema_model.schema_type
                schema_topic_dict['schema_definition'] = schema_model.definition
                schema_topic_dict['schema_revision_id'] = schema_model.revisionId
                all_schema_topic_object.append(schema_topic_dict)
        return all_schema_topic_object
    except Exception as e:
        logger.error(f'Error occurred - {str(e)}')


@api_router.post("/topics/create/topic_schema_association", include_in_schema=False)
async def create_schema_topic_association_post_call_method(schema_topic_object: TopicSchemaAssociationPydantic, db: Session = Depends(get_db)):
    try:
        logger.info(f'schema_topic_object is - {schema_topic_object}')
        schema_topic_db_object = SchemaTopicAssociation()
        schema_topic_db_object.schemas_info_id = schema_topic_object.schemas_info_id
        schema_topic_db_object.kafka_topics_id = schema_topic_object.kafka_topics_id
        db.add(schema_topic_db_object)
        db.commit()
        return successful_response(201), schema_topic_db_object.id
    except Exception as e:
        logger.error(f'error occured - {str(e)}')


@api_router.post("/topics/{TopicName}:publish", response_model=None, responses={**publish_success_Response,
    **bad_request_responses,
    **unauthorized_responses,
    **Unexpected_error_responses})
def Publishes_a_message(Info: Messages,
                        TopicName: str = Path(..., description="Name of the topic"),
                        db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        TopicName = TopicName.split(':publish')[0]
        logger.info(f'Inside publish message to kafka topic - {TopicName}')
        kafkatopic_model = db.query(KafkaTopics).filter(KafkaTopics.kafka_topic_name == TopicName).first()
        if kafkatopic_model:
            logger.info(f'Topic - {TopicName} exist, proceeding with payload validation')
            kafka_topic_id = kafkatopic_model.id
            bus_name = kafkatopic_model.kafka_bus_name
            publish_messge_length = len(Info.messages)
            logger.debug(f'publish_messge_length - {publish_messge_length}, MAX_MESSAGES_TO_PUBLISH - {MAX_MESSAGES_TO_PUBLISH}')
            logger.debug(f'{type(publish_messge_length)}, {type(MAX_MESSAGES_TO_PUBLISH)}')
            if publish_messge_length > int(MAX_MESSAGES_TO_PUBLISH):
                error = {
                    "error": {
                        "code": 400,
                        "message": f"Message range exceeded",
                        "status": "error",
                        "details": {
                            "reason": f"Detail description: Maximum limit set to publish messages. Range: 1 to {int(MAX_MESSAGES_TO_PUBLISH)} messages",
                            "type": "Payload Limitation"}
                    }
                }
                return JSONResponse(content=error, status_code=400)
            else:
                logger.info('Payload validation successful')
                logger.info(f'Verifying schema association for topic - {TopicName}')
                topic_schema_association = db.query(SchemaTopicAssociation).filter(SchemaTopicAssociation.kafka_topics_id==kafka_topic_id).first()
                if topic_schema_association:
                    logger.info(f'Getting schema associated for topic - {TopicName}')
                    schema_info_id = topic_schema_association.schemas_info_id
                    schema_info = db.query(SchemasInfo).filter(SchemasInfo.id == schema_info_id).first()
                    if schema_info:
                        logger.info(f'schema definition is - {schema_info.definition}')
                        schema_definition = schema_info.definition
                    else:
                        schema_definition = ""
                else:
                    logger.info(f'Topic - {TopicName} does not have associated schema')
                    schema_definition = ""
                create_info = PublishMessage.create(TopicName=TopicName, info_schema=Info,db=db, schema_definition=schema_definition, bus_name=bus_name)
                return create_info
        else:
            error = {
                "error": {
                    "code": 400,
                    "message": f"Topic '{TopicName}' not found in the Kafka topic table",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: Topic '{TopicName}' is not exist to publish messages, Create one to proceed",
                        "type": "Topic Not Found"}
                }
            }
            return JSONResponse(content=error, status_code=400)
    except Exception as e:
        return {f"status_message": str(e)}

