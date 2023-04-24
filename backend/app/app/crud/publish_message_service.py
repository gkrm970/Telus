import base64, binascii
import functools
import time
import uuid
import json
import socket
import fastavro
import requests
from avro import schema
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from fastavro._schema_common import SchemaParseException
from starlette.responses import JSONResponse
from urllib3 import HTTPSConnectionPool
import paramiko
from app.api.utils.exception_handler import TopicNotFoundException
from app.api.utils.utils import infer_avro_schema, get_current_utc_ascii_timestamp
from app.schemas.publish_message_schema import Messages
from app.models.models import FedKafkaBuses
from app.models.models import AuthType, GSSAPIAuthenticationInfo, KeycloakAuthenticationInfo, LDAPAuthenticationInfo, OAuthBearerAuthenticationInfo, PlainTextAuthenticationInfo, SASLAuthenticationInfo, SSLAuthenticationInfo, ScramAuthenticationInfo, KerberosAuthenticationInfo, FedKafkaBuses
from app.api.utils.enums import AuthTypeEnum
from sqlalchemy.orm import Session

from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger

API_NAME = "Publish Service"
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


def acked(err, msg):
    if err is not None:
        logger.error("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        logger.info("Message produced: %s" % (str(msg)))


def _get_token(args, config_str):
    """Note here value of config comes from sasl.oauthbearer.config below.
        It is not used in this example but you can put arbitrary values to
        configure how you can get the token (e.g. which token URL to use)
    """
    resp = requests.post(args[1], data=args[0], verify=False)
    token = resp.json()
    logger.info(f'token------------------ {token["access_token"]}')
    return token['access_token'], time.time() + float(token['expires_in'])


def write_payload_to_kafka(topic_name, json_data):
    logger.debug("Writing to kafka")
    try:
        producer = Producer(
            bootstrap_servers=["localhost:9092"],
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )
        producer.send(topic_name, json_data)

        logger.debug("Message sent to Kafka topic:", topic_name)
        logger.debug('Writing to kafka Completed')

    except NoBrokersAvailable as e:
        logger.error(f'Error in getting data from Kafka: {str(e)}')
        logger.error('Writing to kafka FAILED')


def timestamp(uuid_16, msg):
    out_dict = {}
    time_str = get_current_utc_ascii_timestamp()
    out_dict['Timestamp'] = time_str
    out_dict['messageId'] = uuid_16
    out_dict['data'] = msg
    return out_dict


class PublishMessage:
    def create(TopicName: str, info_schema: Messages, db: Session, schema_definition: str, bus_name: str):
#        global input_topic_name
        try:
            logger.info('Validating all messages are encoded in base64')
            data_values = [message.data for message in info_schema.messages]
            for msg in data_values:
                try:
                    is_valid = base64.b64decode(msg, validate=True)
                except binascii.Error as e:
                     error = {
                        "error": {
                             "code": 400,
                             "message": f"Message data not encrypted",
                             "status": "error",
                             "details": {
                                 "reason": f"Detail description: Message should be base64 encoded format",
                                 "type": "Data not encoded"}
                         }
                     }
                     return JSONResponse(content=error, status_code=400)

            if schema_definition:
                logger.info(f'Schema for topic - {TopicName} is - {schema_definition}, '
                            f'proceeding message validation with schema')
                for msg in data_values:
                    logger.info(f'Verifying each message with schema associated')
                    logger.info(f"converting encoded data into decoded bytes")
                    decoded_bytes = base64.b64decode(msg)
                    decoded_string = decoded_bytes.decode('utf-8')
                    logger.info(f"decoded string: {decoded_string}")
                    json_data = json.loads(decoded_string)
                    #json_data_list.append(json_data)
                    logger.info(f"converted decoded string into json data: {json_data}")
                    avro_schema = infer_avro_schema(json_data, TopicName)

                    logger.info(f'Compare schema generated from message with schema definition')
                    if fastavro.parse_schema(schema_definition) and fastavro.parse_schema(avro_schema):
                        logger.info("Both schemas are valid")
                        avro_schema_definition = schema.parse(json.dumps(avro_schema))
                        if schema_definition == avro_schema_definition.to_json():
                            logger.info(f'Schema definition and generated schema for message - {msg} are same')
                        else :
                            logger.error(f'Messsage - {msg} is not alligned with associated schema definition')
                            raise SchemaParseException

            logger.info(f'Proceeding to publish messages to topic - {TopicName}')
            logger.info(f'Fetching bus details associated to topic - {TopicName}')
            bus_info = db.query(FedKafkaBuses).filter(FedKafkaBuses.kafka_host==bus_name).first()
            if bus_info:
                kafka_host = bus_info.kafka_host
                kafka_port = bus_info.kafka_port
                auth_type = bus_info.kafka_auth_type
                bootstrap_servers = kafka_host + ":" + str(kafka_port)
                logger.info(f'Fetching Authentication details for bus - {bus_name}')
                if auth_type == AuthTypeEnum.OAUTHBEARER.value:
                    auth_info_obj = db.query(AuthType).filter(AuthType.auth_type == auth_type).filter(AuthType.fed_kafka_bus_name == bus_name).first()
                    if auth_info_obj:
                        logger.info(f'Bus - {bus_name} is registered with {auth_type} authentication')
                        OAuth_id = auth_info_obj.OAuth_auth_info_id
                        OAUth_obj = db.query(OAuthBearerAuthenticationInfo).filter(OAuthBearerAuthenticationInfo.id == OAuth_id).first()
                        oauth_client_secret = OAUth_obj.oauth_client_secret
                        oauth_URL = OAUth_obj.oauth_URL
                        oauth_security_protocol = OAUth_obj.oauth_security_protocol
                        oauth_security_mechanism = OAUth_obj.oauth_security_mechanism
                        oauth_issuer = OAUth_obj.oauth_issuer
                        oauth_client_id = OAUth_obj.oauth_client_id

                        payload = {
                            'grant_type': 'client_credentials',
                            'client_id': oauth_client_id,
                            'client_secret': oauth_client_secret
                        }
                        token_payload_url_list = [payload, oauth_URL]
                        logger.info(f'token_payload_url_list is : {token_payload_url_list}')

                        conf = {
                            'bootstrap.servers': bootstrap_servers,
                            'security.protocol': oauth_security_protocol,
                            'debug': 'broker,admin,protocol',
                            # 'security.protocol': 'SASL_PLAINTEXT',
                            'sasl.mechanisms': auth_type,
                            'ssl.certificate.location': oauth_issuer,
                            'ssl.ca.location': oauth_issuer,
                            'client.id': socket.gethostname(),
                            'compression.type':'none',
                            'enable.ssl.certificate.verification': False,
                            'group.id': oauth_client_id,
                            'oauth_cb': functools.partial(_get_token, token_payload_url_list)
                        }
                    else:
                        logger.error(f'Error while fetching authentication info for bus- {bus_name}')
                        raise BaseException
                else:
                    logger.info(f'No authentication set for the bus - {bus_name}')
                    conf = {'bootstrap.servers': bootstrap_servers, 'session.timeout.ms': 6000,
                            'client.id': socket.gethostname()}

            producer = Producer(conf)
            serializer = StringSerializer('utf_8')
            list_ids = []
            input_topic_name = TopicName
            logger.info(f"User_input: {input_topic_name}")
            logger.debug(f'Data values are : {data_values}')
            for msg in data_values:
                uuid_16 = str(uuid.uuid4().int)[:16]
                logger.info('Writing message using confluent kafka producer')
                logger.info(f'Message to publish is - {msg}')

                try:
                    record_key = uuid_16
                    record_value = msg
                    logger.info("Producing record: {}\t{}".format(record_key, record_value))
                    producer.produce(input_topic_name,
                                 key=record_key,
                                 value=record_value, on_delivery=acked)
                    producer.poll(0)
                    list_ids.append(uuid_16)
                except Exception as e:
                    logger.error('Issue while producing messages to topic - {topic_name}')
                    raise BaseException
                    return {"status": "Failed to produce messages to Kafka"}
            if producer.flush(timeout=10) == 0:
                logger.info("All messages sent successfully")
                return {"messageIds": list_ids}
            else:
                logger.error("Failed to send messages to Kafka")
                raise Exception 
        except SchemaParseException as e:
            error = {
                "error": {
                    "code": 400,
                    "message": f"schema validation failed, can't publish message",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Invalid Message format"}
                }
            }
            return JSONResponse(content=error, status_code=400)
        except TopicNotFoundException as e:
            error = {
                "error": {
                    "code": 400,
                    "message": f"Topic '{TopicName}' not found in the Kafka topic table list.",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Topic Not Found"}
                }
            }
            return JSONResponse(content=error, status_code=400)
        except HTTPSConnectionPool as e:
            error = {
                "error": {
                    "code": 400,
                    "message": f"HTTPSConnectionPool(host='3.110.130.218', port=9090)",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Topic Not Found"}
                }
            }
            return JSONResponse(content=error, status_code=400)
        except paramiko.AuthenticationException as e:
            error = {
                "error": {
                    "code": 401,
                    "message": f"Authentication failed",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Unauthorized"}
                }
            }
            return JSONResponse(content=error, status_code=401)
        except BaseException as e:
            error = {
                "error": {
                    "code": 500,
                    "message": f"Unexpected Error",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Unexpected Error"}
                }
            }
            return JSONResponse(content=error, status_code=500)
        except Exception as e:
            error = {
               "error": {
                    "code": 500,
                    "message": f"Unable to publish messages to kafka",
                    "status": "error",
                    "details": {
                        "reason": f"Detail description: {e}",
                        "type": "Kafka Error"}
                }
            }
            return JSONResponse(content=error, status_code=500)
