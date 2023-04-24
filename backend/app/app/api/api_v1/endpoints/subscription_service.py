from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from app.models.models import SubscriptionModel
from app.schemas.post_schema import SubscriptionPull
from app.schemas.subscription_patch_schema import Subscription as Patch_Subscription
from app.schemas.subscription_schema import Subscription, validate_subscription_name, env_names, team_names, SubscriptionType
from app.responses.return_api_responses import create_response, update_response, get_response, get_all_response, \
    Successful_Response, unauthorized_responses, Unexpected_error_responses, Subscription_Response, \
    bad_request_responses, Resource_conflict_responses, Return_Successful_Response, no_subscription_found, \
    delete_Response, delete_no_subscription_found, Subscription_Post_Response

from sqlalchemy.orm import Session
from sqlalchemy import exc
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger

API_NAME = "Subscription API"
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


@api_router.get("/subscriptions",
                responses={**Successful_Response, **unauthorized_responses, **Unexpected_error_responses})
def Lists_all_the_subscriptions(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    subscription_list = db.query(SubscriptionModel).all()
    try:
        if subscription_list:
            res = get_all_response(subscription_list)

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


@api_router.put("/subscriptions/{SubscriptionName}",
                responses={**Subscription_Response, **bad_request_responses, **unauthorized_responses,
                           **Resource_conflict_responses,
                           **Unexpected_error_responses})
def Creates_a_subscription(input_data: Subscription, SubscriptionName: str = Path(..., description="Name of the "
                                                                                                        "topic. "
                                                                                                        "Follow the "
                                                                                                        "naming "
                                                                                                        "convention "
                                                                                                        "<app-team-name"
                                                                                                        ">-<environment"
                                                                                                        "-name>-<event"
                                                                                                        "-name>. "
                                                                                                        "Allowed "
                                                                                                        "environment "
                                                                                                        "names "
                                                                                                        "are develop, "
                                                                                                        "preprod, "
                                                                                                        "qa & prod. "
                                                                                                        "App "
                                                                                                        "team name "
                                                                                                        "examples -> "
                                                                                                        "bsaf, "
                                                                                                        "naaf & pltf. "
                                                                                                        "The "
                                                                                                        "three "
                                                                                                        "examples "
                                                                                                        "are for "
                                                                                                        "application teams "
                                                                                                        "TINAA Business "
                                                                                                        "Services "
                                                                                                        "Automation "
                                                                                                        "Framework, "
                                                                                                        "TINAA Network "
                                                                                                        "Applications "
                                                                                                        "Automation "
                                                                                                        "Framework & TINAA "
                                                                                                        "Platform team. If "
                                                                                                        "you do no belong "
                                                                                                        "to any of the "
                                                                                                        "three within "
                                                                                                        "TINAA, "
                                                                                                        "Please contact "
                                                                                                        "dlSDNPlatformSupportDistributionList@telus.com."),

                           db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    res = validate_subscription_name(SubscriptionName)
    dict_data = input_data.__dict__

    sub_obj = db.query(SubscriptionModel).filter(SubscriptionModel.name == SubscriptionName).first()
    logger.info(f'Checking SubscriptionName Object Existed in DB {sub_obj}')
    try:
        if res:
            logger.info(f'Valid SubscriptionName follow the naming convention: {res}')
            if sub_obj:
                logger.info(f'Valid SubscriptionName Object {sub_obj} is not None')
                error = {
                    "error": {
                        "code": 404,
                        "message": f"SubscriptionName: {SubscriptionName} Already Existed In DB",
                        "status": "Can you Give Another SubscriptionName",
                        "details": {
                            "reason": "SubscriptionName Already Existed In DB",
                            "type": "invalid_parameter"
                        }
                    }
                }
                logger.info(f'SubscriptionName: {SubscriptionName} Already Existed In DB')
                return JSONResponse(content=error, status_code=404)

            else:
                logger.info(f'Sub_obj Is None So Checking Topic Name Association Already Existed Same Values in DB')
                sub_obj = db.query(SubscriptionModel).filter(SubscriptionModel.topic == dict_data.get('topic')).first()

                logger.info(f'sub_obj_topic: {sub_obj}')
                if sub_obj:
                    logger.info(f'Checked sub_obj is not None:{sub_obj}')
                    logger.info(f'Start the Checking sub_obj values and Input_data Values Same or Not ')
                    if sub_obj.topic == dict_data.get('topic') and sub_obj.pushEndpoint == dict_data.get(
                            'pushConfig').pushEndpoint and \
                            sub_obj.ttl == dict_data.get(
                        'expirationPolicy').ttl and sub_obj.minimumBackoff == dict_data.get(
                        'retryPolicy').minimumBackoff and \
                            sub_obj.maximumBackoff == dict_data.get('retryPolicy').maximumBackoff and \
                            sub_obj.messageRetentionDuration == dict_data.get('messageRetentionDuration'):
                        logger.info(f'Both are Same value Raising Error Values Already Existed In DB')
                        error = {
                            "error": {
                                "code": 404,
                                "message": f"This {sub_obj.topic} Topic Name Association Already Existed Same Values "
                                           f"in DB",
                                "status": "Can you Give Another Values",
                                "details": {
                                    "reason": "Values Already Existed In DB",
                                    "type": "invalid_parameter"
                                }
                            }
                        }
                        logger.info(f'sub_obj_topic: {sub_obj}')
                        return JSONResponse(content=error, status_code=404)
                    else:
                        logger.info(f'Values Are Not Same DB Operations Start')
                        subscribe_model = SubscriptionModel()
                        subscribe_model.name = SubscriptionName
                        subscribe_model.topic = dict_data['topic']
                        if dict_data.get('pushConfig'):
                            if dict_data.get('pushConfig').pushEndpoint:
                                logger.info(dict_data.get('pushConfig').pushEndpoint)
                                subscribe_model.subscription_type = SubscriptionType.PUSH
                                subscribe_model.pushEndpoint = dict_data.get('pushConfig').pushEndpoint
                            else:
                                subscribe_model.subscription_type = SubscriptionType.PULL
                        else:
                            subscribe_model.subscription_type = SubscriptionType.PULL
                        subscribe_model.ttl = dict_data['expirationPolicy'].ttl
                        subscribe_model.minimumBackoff = dict_data['retryPolicy'].minimumBackoff
                        subscribe_model.maximumBackoff = dict_data['retryPolicy'].maximumBackoff
                        subscribe_model.messageRetentionDuration = dict_data['messageRetentionDuration']
                        db.add(subscribe_model)
                        db.commit()
                        logger.info("Data-Stored-In-DataBase-Successfully")
                        response = create_response(subscribe_model)
                else:
                    logger.info(f'sub_obj {sub_obj} is None So DB Operations Start')
                    subscribe_model = SubscriptionModel()
                    subscribe_model.name = SubscriptionName
                    subscribe_model.topic = dict_data['topic']
                    if dict_data.get('pushConfig'):
                        if dict_data.get('pushConfig').pushEndpoint:
                            subscribe_model.subscription_type = SubscriptionType.PUSH
                            subscribe_model.pushEndpoint = dict_data.get('pushConfig').pushEndpoint
                        else:
                            subscribe_model.subscription_type = SubscriptionType.PULL
                    else:
                        subscribe_model.subscription_type = SubscriptionType.PULL
                    subscribe_model.ttl = dict_data['expirationPolicy'].ttl
                    subscribe_model.minimumBackoff = dict_data['retryPolicy'].minimumBackoff
                    subscribe_model.maximumBackoff = dict_data['retryPolicy'].maximumBackoff
                    subscribe_model.messageRetentionDuration = dict_data['messageRetentionDuration']
                    db.add(subscribe_model)
                    db.commit()
                    logger.info("Data-Stored-In-DataBase-Successfully")
                    response = create_response(subscribe_model)
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
        return response
    except Exception as e:
        error = {
            {
                "error": {
                    "code": 500,
                    "message": f"Error Occurred in {str(e)}",
                    "status": "string",
                    "details": {
                        "reason": "Error",
                        "type": "Unexpected error"
                    }
                }
            }
        }
        return JSONResponse(content=error, status_code=500)


# start the post method
@api_router.post("/subscriptions/{SubscriptionName}:pull",
                 responses={**Subscription_Post_Response, **bad_request_responses, **unauthorized_responses,
                            **Unexpected_error_responses})
def Pulls_message_for_the_subscription(input_data: SubscriptionPull,
                                       SubscriptionName: str = Path(..., description='Name of the topic'), db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    pass


# End the post method

@api_router.patch('/subscriptions/{SubscriptionName}',
                  responses={**Subscription_Response, **bad_request_responses, **unauthorized_responses,
                             **Unexpected_error_responses})
def Updates_a_subscription(input_data: Patch_Subscription, SubscriptionName: str = Path(..., description='Name of the '
                                                                                                         'subscription. Follow the naming convention <app-team-name>-<environment-name>-<subscription-name>. '
                                                                                                         'Allowed '
                                                                                                         'environment '
                                                                                                         'names are '
                                                                                                         'develop, '
                                                                                                         'preprod, '
                                                                                                         'qa & prod. '
                                                                                                         'App team '
                                                                                                         'name '
                                                                                                         'examples -> '
                                                                                                         'bsaf, '
                                                                                                         'naaf & '
                                                                                                         'pltf. The '
                                                                                                         'three '
                                                                                                         'examples '
                                                                                                         'are for '
                                                                                                         'application '
                                                                                                         'teams TINAA '
                                                                                                         'Business '
                                                                                                         'Services '
                                                                                                         'Automation '
                                                                                                         'Framework, '
                                                                                                         'TINAA '
                                                                                                         'Network '
                                                                                                         'Applications Automation Framework & TINAA Platform team.'
                                                                                                         ' If you do no belong to any of the three within TINAA, '
                                                                                                         'Please contact dlSDNPlatformSupportDistributionList@telus.com.'),
                           db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    sub_obj_model = db.query(SubscriptionModel).filter(SubscriptionModel.name == SubscriptionName).first()
    try:
        res = validate_subscription_name(SubscriptionName)
        if res:
            if sub_obj_model:
                dict_data = input_data.__dict__
                logger.info("Inside if Condition")
                data = dict_data.get('pushConfig').__dict__
                d = data.get('oidcToken').__dict__
                a = dict_data.get('labels').__dict__
                key = a.get('key')
                value = a.get('value')
                service_email = d.get('serviceAccountEmail')
                audience = d.get('audience')
                sub_obj_model.name = SubscriptionName
                sub_obj_model.topic = dict_data['topic']
                sub_obj_model.subscriptionType = dict_data['subscriptionType']
                sub_obj_model.filter = dict_data['filter']
                sub_obj_model.timeAggregation = dict_data['aggregationSettings'].timeAggregation
                sub_obj_model.spaceAggregation = dict_data['aggregationSettings'].spaceAggregation
                sub_obj_model.method = dict_data['deliverySettings'].method
                sub_obj_model.format = dict_data['deliverySettings'].format
                sub_obj_model.url = dict_data['deliverySettings'].url
                sub_obj_model.fieldNameChanges = dict_data['dataTranformationSettings'].fieldNameChanges
                sub_obj_model.fieldsReorder = dict_data['dataTranformationSettings'].fieldsReorder
                sub_obj_model.fieldsToRemove = dict_data['dataTranformationSettings'].fieldsToRemove
                # sub_obj_model.pushEndpoint = dict_data['pushConfig'].pushEndpoint
                if dict_data.get('pushConfig'):
                    if dict_data.get('pushConfig').pushEndpoint:
                        logger.info(dict_data.get('pushConfig').pushEndpoint)
                        sub_obj_model.subscription_type = SubscriptionType.PUSH
                        sub_obj_model.pushEndpoint = dict_data.get('pushConfig').pushEndpoint
                    else:
                        sub_obj_model.subscription_type = SubscriptionType.PULL
                else:
                    sub_obj_model.subscription_type = SubscriptionType.PULL
                sub_obj_model.serviceAccountEmail = service_email
                sub_obj_model.audience = audience
                sub_obj_model.ackDeadlineSeconds = dict_data['ackDeadlineSeconds']
                sub_obj_model.retainAckedMessages = dict_data['retainAckedMessages']
                sub_obj_model.messageRetentionDuration = dict_data['messageRetentionDuration']
                sub_obj_model.key = key
                sub_obj_model.value = value
                sub_obj_model.enableMessageOrdering = dict_data['enableMessageOrdering']
                sub_obj_model.ttl = dict_data['expirationPolicy'].ttl
                sub_obj_model.deadLetterTopic = dict_data['deadLetterPolicy'].deadLetterTopic
                sub_obj_model.maxDeliveryAttempts = dict_data['deadLetterPolicy'].maxDeliveryAttempts
                sub_obj_model.minimumBackoff = dict_data['retryPolicy'].minimumBackoff
                sub_obj_model.maximumBackoff = dict_data['retryPolicy'].maximumBackoff
                sub_obj_model.detached = dict_data['detached']
                sub_obj_model.enableExactlyOnceDelivery = dict_data['enableExactlyOnceDelivery']
                db.add(sub_obj_model)
                db.commit()
                res = update_response(sub_obj_model)

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


@api_router.get('/subscriptions/{SubscriptionName}',
                responses={**Return_Successful_Response, **unauthorized_responses, **no_subscription_found,
                           **Unexpected_error_responses})
def Returns_a_subscription(SubscriptionName: str = Path(..., description='Name of the subscription. Follow the naming '
                                                                         'convention '
                                                                         '<app-team-name>-<environment-name'
                                                                         '>-<subscription-name>. Allowed environment '
                                                                         'names are develop, preprod, qa & prod. App '
                                                                         'team name examples -> bsaf, naaf & pltf. '
                                                                         'The three examples are for application '
                                                                         'teams TINAA Business Services Automation '
                                                                         'Framework, TINAA Network Applications '
                                                                         'Automation Framework & TINAA Platform team. '
                                                                         'If you do no belong to any of the three '
                                                                         'within TINAA, Please contact '
                                                                         'dlSDNPlatformSupportDistributionList@telus'
                                                                         '.com.'), db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    sub_model_obj = db.query(SubscriptionModel).filter(SubscriptionModel.name == SubscriptionName).first()
    res = validate_subscription_name(SubscriptionName)

    try:
        if res:
            if sub_model_obj:
                logger.info('Checking The DB object Existed or Not')
                res = get_response(sub_model_obj)
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
                logger.info('No Object Existed in DB')
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
        return res
    except exc.SQLAlchemyError as e:
        logger.info("Data Base Connection Error")
        logger.debug(e)
        raise Exception("DataBase Connection Error", e)
    except Exception as e:
        error = {
            {
                "error": {
                    "code": 500,
                    "message": f"Error Occurred in {str(e)}",
                    "status": "string",
                    "details": {
                        "reason": "Error",
                        "type": "Unexpected error"
                    }
                }
            }
        }
        return JSONResponse(content=error, status_code=500)


@api_router.delete('/subscriptions/{SubscriptionName}',
                   responses={**delete_Response, **delete_no_subscription_found, **unauthorized_responses,
                              **Unexpected_error_responses})
def Deregisters_a_subscription(SubscriptionName: str = Path(..., description='Name of the subscription. Follow the '
                                                                           'naming convention '
                                                                           '<app-team-name>-<environment-name'
                                                                           '>-<subscription-name>. Allowed '
                                                                           'environment names are develop, preprod, '
                                                                           'qa & prod. App team name examples -> '
                                                                           'bsaf, naaf & pltf. The three examples are '
                                                                           'for application teams TINAA Business '
                                                                           'Services Automation Framework, '
                                                                           'TINAA Network Applications Automation '
                                                                           'Framework & TINAA Platform team. If you '
                                                                           'do no belong to any of the three within '
                                                                           'TINAA, Please contact '
                                                                           'dlSDNPlatformSupportDistributionList'
                                                                           '@telus.com.'),
                             db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    sub_model_obj = db.query(SubscriptionModel).filter(SubscriptionModel.name == SubscriptionName).first()
    res = validate_subscription_name(SubscriptionName)
    try:
        if res:
            if sub_model_obj:
                logger.info('Checking The DB object Existed or Not')
                db.delete(sub_model_obj)
                db.commit()
                logger.info('Deleted Record Successfully')
                res = {f"Record Deleted Successfully SubscriptionName : {SubscriptionName}"}
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

