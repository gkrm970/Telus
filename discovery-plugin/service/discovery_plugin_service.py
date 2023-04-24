import json
import base64, binascii
import sys, os
import re
import ast
import requests
import functools
from confluent_kafka import Consumer
from confluent_kafka.admin import AdminClient, ConfigResource
from confluent_kafka.cimpl import KafkaException, KafkaError
import concurrent.futures
from utils.avro_utils import infer_avro_schema
import time

import logging

logging.getLogger('apscheduler.scheduler').propagate = False
logging.getLogger('apscheduler.executors').propagate = False
logger = logging.getLogger('bg-scheduler-instance')


def on_assign (c, ps):
    for p in ps:
        p.offset=-2
        c.assign(ps)


def _get_token(args, config_str):
    """Note here value of config comes from sasl.oauthbearer.config below.
        It is not used in this example but you can put arbitrary values to
        configure how you can get the token (e.g. which token URL to use)
        """
    resp = requests.post(args[1], data=args[0], verify=False)
    token = resp.json()
    logger.info(f'token------------------ {token["access_token"]}')
    return token['access_token'], time.time() + float(token['expires_in'])


def discovery_service(service_url, job_ids, access_token):
    logger.info(
        '****************************** Discovery Plugin service ******************************')
    service_url = f'{service_url}'
    fetch_fed_kafka_bus_by_id_url = service_url + 'fed_kafka_bus/get_by_id/'
    create_fed_kafka_topics_url = service_url + 'topics'
    get_schema_registry_info_url = service_url + 'schemaregistry/'
    get_latest_schema_info_db_url = service_url + 'schemas'
    create_new_inactive_old_schema_url = service_url + 'schemas/update_new_schema'
    update_schema_topic_association_to_latest_schema_version_url = \
        '{0}topics/update_latest_schema_in_topic_schema_association'.format(service_url)
    create_schema_topic_url = '{0}topics/create/topic_schema_association'.format(service_url)
    create_schema_info_url = service_url + 'schemas'
    get_auth_record_url = service_url + 'auth_type/get_record_by/'
    headers = {'accept': 'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}

    ids_list = job_ids
    logger.info(
        f'All the job ids for this frequency interval are: {ids_list}')
    for job_id in ids_list:
        logger.info(f'Fetching details of kafka bus id - {job_id}')
        fed_kafka_info_id_url = fetch_fed_kafka_bus_by_id_url + str(job_id)
        logger.debug(
            f'url to fetch info for bus id is: {fed_kafka_info_id_url}')
        fed_kafka_buses_resp = requests.get(fed_kafka_info_id_url, headers=headers)
        logger.debug(
            f'Response from fed_kafka_buses table is: {fed_kafka_buses_resp.json()} ')

        if fed_kafka_buses_resp.status_code == 200:
            logger.info('fed_kafka_buses entries are exist')
            response = fed_kafka_buses_resp.json()
            fed_kafka_bus_id = response['fed_kafka_id']
            fed_kafka_bus_name = response['kafka_host']
            schema_registry_id = response['schema_registry_id']
            kafka_host = response['kafka_host']
            kafka_port = response['kafka_port']
            kafka_auth_type = response.get('kafka_auth_type')
            created_by = 'Discovery-Plugin-Service'
            updated_by = 'Discovery-Plugin-Service'

            logger.info(
                'Fetching each row host, port and auth_type of bus from table - fed_kafka_buses')
            bootstrap_servers = kafka_host + ":" + str(kafka_port)
            logger.info('kafka onsumer call')
            if kafka_auth_type is None:
                conf = {'bootstrap.servers': bootstrap_servers, 'session.timeout.ms': 6000, 'group.id': 'pltf-develop-pubsub-discoverer', 'auto.offset.reset': 'earliest', 'session.timeout.ms': 6000}
            elif kafka_auth_type == "OAUTHBEARER":
                logger.info(f'Get OAUTHBEARER details from auth_info table')
                get_auth_record_url_with_params = "{0}{1}/{2}".format(get_auth_record_url, str(kafka_auth_type),
                                                                      str(fed_kafka_bus_name))
                logger.info(f'URL is: {get_auth_record_url_with_params}')
                auth_info_response = requests.get(get_auth_record_url_with_params, headers=headers)
                auth_info_response_json = auth_info_response.json()
                logger.info(f'Authentication info response is : {auth_info_response_json}')

                payload = {
                    'grant_type': 'client_credentials',
                    'client_id': auth_info_response_json.get('oauth_client_id'),
                    'client_secret': auth_info_response_json.get('oauth_client_secret')
                }
                token_payload_url_list = [payload, auth_info_response_json.get('oauth_URL')]
                logger.info(f'token_payload_url_list is : {token_payload_url_list}')

                conf = {
                    'bootstrap.servers': bootstrap_servers,
                    #'debug': 'broker,admin,protocol',
                    'security.protocol': auth_info_response_json.get('oauth_security_protocol'),
                    # 'security.protocol': 'SASL_PLAINTEXT',
                    'session.timeout.ms': 6000,
                    'auto.offset.reset': 'earliest',
                    'sasl.mechanisms': auth_info_response_json.get('auth_type'),
                    # 'ssl.certificate.location': auth_info_response_json.get('oauth_issuer'),

                    'ssl.certificate.location': auth_info_response_json.get('certificate_issuer'),
                    'ssl.key.location': auth_info_response_json.get('key_issuer'),

                    'ssl.key.password': auth_info_response_json.get('oauth_issuer'),
                    'ssl.ca.location': auth_info_response_json.get('oauth_issuer'),
                    'enable.ssl.certificate.verification': False,
                    'group.id': auth_info_response_json.get('oauth_client_id'),
                    'oauth_cb': functools.partial(_get_token, token_payload_url_list)
                }
            consumer = Consumer(conf)
            admin_client = AdminClient(conf)
            consumer.poll(timeout=10)
            list_of_topics = consumer.list_topics().topics
            logger.info(
                f'Fetching list  of topics from consumer call: {list_of_topics}')

            logger.info('topics appending to list')
            topic_names = []
            for topic_name in list_of_topics:
                topic_names.append(topic_name)
            logger.info(
                f'list of topic name from consumer call: {topic_names}')

            if schema_registry_id is not None:
                logger.info(
                    f'Schema Registry id - {schema_registry_id} exist for order id: {fed_kafka_bus_id}')
                try:
                    logger.info(
                        f'Fetching the Schema Registry details for Schema Registry id - {schema_registry_id} '
                        f'from schema_registry table')
                    schema_registry_resp = requests.get(
                        get_schema_registry_info_url + f'{schema_registry_id}', headers=headers)
                    logger.debug(
                        f'Response from schema_registry table is - {schema_registry_resp}')
                    schema_registry_db_data = schema_registry_resp.json()
                    schema_registry_host = schema_registry_db_data["schema_registry_host"]
                    schema_registry_port = schema_registry_db_data["schema_registry_port"]
                    schema_info_from_schema_registery_url = "http://" + schema_registry_host + ":" + \
                                                            str(schema_registry_port) + "/schemas"
                    logger.debug(
                        f'schema_registry_url is - {schema_info_from_schema_registery_url}')
                    schema_info_resp = requests.get(
                        schema_info_from_schema_registery_url, headers=headers)
                    all_schema_defintions_from_cloud = schema_info_resp.json()
                    logger.debug(
                        f'Response from schema_registry url: {all_schema_defintions_from_cloud}')
                    for each_cloud_schema_dict in all_schema_defintions_from_cloud:
                        subject_from_cloud = each_cloud_schema_dict['subject']
                        if "-key" in subject_from_cloud:
                            continue
                        topic_name_from_cloud = (
                                                    subject_from_cloud.split('-value'))[:-1][0]
                        schema_name_from_cloud = json.loads(
                            each_cloud_schema_dict['schema'])['name']
                        schema_type_from_cloud = json.loads(
                            each_cloud_schema_dict['schema'])['type']
                        latest_schema_definition_from_cloud = json.loads(
                            each_cloud_schema_dict['schema'])

                        logger.debug(
                            f"Values are extracting schema are: {subject_from_cloud}, {topic_name_from_cloud}, "
                            f"{schema_name_from_cloud},{schema_type_from_cloud},{latest_schema_definition_from_cloud}")

                        get_latest_schema_info_url = '{0}/{1}'.format(get_latest_schema_info_db_url,
                                                                      str(schema_name_from_cloud))
                        logger.debug(
                            f'get_latest_schema_info_url - {get_latest_schema_info_url}')
                        schema_info_object = requests.get(
                            get_latest_schema_info_url, headers=headers)
                        schema_info_resp = schema_info_object.json()
                        logger.debug(
                            f'response from schema_info table - {schema_info_resp}')

                        if schema_info_object.status_code == 200:
                            schema_id = schema_info_resp['id']
                            old_schema_definition_in_db = schema_info_resp['definition']
                            logger.debug(
                                f'type of old schema - {type(ast.literal_eval(old_schema_definition_in_db))}')
                            logger.debug(
                                f'type od new schema - {type(latest_schema_definition_from_cloud)}')
                            old_schema, new_schema = ast.literal_eval(
                                old_schema_definition_in_db), latest_schema_definition_from_cloud
                            logger.info(
                                'comparing old_schema with latest_schema')
                            logger.info(f'{old_schema}, {new_schema}')
                            if old_schema != new_schema:
                                logger.info(
                                    f'both schemas are not same, inserting new version as db record '
                                    f'and making old one inactive using put call')

                                logger.info(
                                    f'create_new_inactive_old_schema_url: {create_new_inactive_old_schema_url}')
                                new_version_schema_info_payload_dict = {
                                    "definition": json.dumps(latest_schema_definition_from_cloud),
                                }
                                create_new_inactive_old_schema_with_schema_id_url = "{0}/{1}".format(
                                    create_new_inactive_old_schema_url, str(schema_id))
                                schema_info_object = requests.put(
                                    create_new_inactive_old_schema_with_schema_id_url,
                                    json=new_version_schema_info_payload_dict, headers=headers)
                                schema_info_json_resp = schema_info_object.json()
                                logger.info(
                                    f'response after inserting latest version - {schema_info_json_resp}')
                                # latest_version_schema_id = schema_info_json_resp['id']
                                # logger.info(
                                #     f'updating schema topics associations')
                                # update_schema_topic_association_to_latest_schema_version_with_ids_url = \
                                #     update_schema_topic_association_to_latest_schema_version_url + "/" + schema_id + \
                                #     "/" + latest_version_schema_id
                                # schema_topic_relation_object_resp = requests.put(
                                #     update_schema_topic_association_to_latest_schema_version_with_ids_url,
                                #     headers=headers)
                                # schema_topic_relation_object_resp = schema_topic_relation_object_resp.json()
                                logger.info(
                                    f'topic-schema association updated successfully')
                            else:
                                logger.info(
                                    f'no differences found the the old and latest schema definitions. Old schema: '
                                    f'{old_schema} , New schema: {new_schema}')
                        elif schema_info_object.status_code != 200:
                            logger.debug(
                                f'saving schema info table because no record existed')
                            schema_info_payload = {
                                "name": schema_name_from_cloud,
                                "type": schema_type_from_cloud,
                                "definition": str(latest_schema_definition_from_cloud)
                            }
                            logger.debug(
                                f'schema_info_payload is - {schema_info_payload}')
                            logger.debug(f'{create_schema_info_url}')
                            schema_info_object = requests.post(
                                create_schema_info_url, json=schema_info_payload, headers=headers)
                            schema_info_json_resp = schema_info_object.json()
                            logger.debug(
                                f'Response after inserting into schema info table - {schema_info_json_resp}')
                            schema_info_object_id = schema_info_json_resp["id"]

                            logger.info(
                                f'After saving into Schema info DB {schema_info_json_resp} and '
                                f'id is {schema_info_object_id}')

                            logger.info(
                                f'Schema:: fetching message retention period for topic - {topic_name_from_cloud}')
                            admin_client.poll(timeout=10)
                            topic_configResource = admin_client.describe_configs(
                                [ConfigResource(restype=2, name=topic_name_from_cloud)], request_timeout=10)
                            for j in concurrent.futures.as_completed(iter(topic_configResource.values())):
                                config_response = j.result(timeout=1)
                                logger.info(f'schema:: config response is : {config_response}')
                                msg_retention_time_obj = config_response.get('retention.ms')
                            msg_retention_time_ms = (str(msg_retention_time_obj).split('=')[-1]).replace('"', "")
                            msg_retention_time_sec = (int(msg_retention_time_ms) / 1000)
                            logger.info(f'schema:: message retention time for topic is : {msg_retention_time_sec}')

                            topic_payload_dict = {
                                "labels": {
                                    "key": "",
                                    "value": ""
                                },
                                "schemaSettings": {
                                    "schema": schema_name_from_cloud,
                                    "encoding": "JSON",
                                    "firstRevisionId": "",
                                    "lastRevisionId": ""
                                },
                                "kafka_bus_name": fed_kafka_bus_name,
                                "messageRetentionDuration": f'{msg_retention_time_sec}s',
                                "retentionSettings": {
                                    "liveDateRetentionDuration": "",
                                    "historicalDataRetentionDuration": ""
                                },
                                "supportedSubscriptionTypes": ""
                            }
                            logger.debug(
                                f'Inserting kafka topic details - {topic_payload_dict} in fed_kafka_topics table')
                            create_fed_kafka_topics_with_topic_name_url = "{0}/{1}".format(
                                create_fed_kafka_topics_url, str(topic_name_from_cloud))
                            fed_kafka_topics_object = requests.put(
                                create_fed_kafka_topics_with_topic_name_url, json=topic_payload_dict, headers=headers)
                            fed_kafka_topics_object = fed_kafka_topics_object.json()
                            logger.info(
                                f'fed_kafka_topics_object - {fed_kafka_topics_object}')
                            fed_kafka_topics_object_id = fed_kafka_topics_object["id"]
                            logger.info(
                                f'after saving fed_kafka_topics_object - {fed_kafka_topics_object} '
                                f'and id is {fed_kafka_topics_object_id}')

                            logger.info(
                                f'saving schema topics association table')
                            schema_topic_payload_dict = {
                                "schemas_info_id": schema_info_object_id,
                                "kafka_topics_id": fed_kafka_topics_object_id,
                            }
                            schema_topic_relation_object = requests.post(
                                create_schema_topic_url, json=schema_topic_payload_dict, headers=headers)
                            schema_topic_relation_object = schema_topic_relation_object.json()
                            logger.info(
                                f'schema topics relation response {schema_topic_relation_object}')

                except Exception as e:
                    logger.error(
                        f'Error while dealing with schema registry ID - {schema_registry_id}')
                    logger.error(f'Exception : {e}')

            else:
                logger.info(
                    f'if schema_registry not exits with the admin payload,reading data from all topics')
                if len(topic_names) > 0:
                    for topic_name in topic_names:
                        try:
                            if topic_name == "_schemas" or topic_name == "__consumer_offsets":
                                continue
                            logger.info(
                                f'getting all messages from single topic - {topic_name}')
                            logger.info(
                                f'getting first message in topic - {topic_name}')
                            first_message_in_topic = None

                            try: 
                                logger.info(f'getting subscribed to the topic - {topic_name}')
                                #consumer.subscribe([topic_name] , on_assign=on_assign)
                                consumer.subscribe([topic_name])
                                logger.info('Subscribed to the topic successfully')
                                logger.info('Polling to fetch the record using offset')
                                msg = consumer.poll(5.0)
                                logger.info(f'{type(msg)}')

                                if msg is None:
                                    logger.info(f'message is None')
                                    first_message_in_topic = "NO_MSG_TO_DISCOVER_SCHEMA"
                                    logger.info(f'message is set to - {first_message_in_topic}')
                                elif msg.error():
                                    if msg.error().code() == KafkaError._PARTITION_EOF:
                                        logger.info(f'reached end at offset - {msg.topic(), msg.partition(), msg.offset()}')
                                    elif msg.error():
                                        logger.info(f'Consumer error: {msg.error()}')
                                        #raise KafkaException(msg.error())
                                        logger.error(KafkaException(msg.error()))
                                    first_message_in_topic = "UNABLE_TO_DISCOVER_SCHEMA"
                                else:
                                    all_messages = msg.value()
                                    logger.info(f'message type is - {type(all_messages)}')
                                    if isinstance(all_messages, (bytes, bytearray)):
                                        try:
                                            all_message_in_topic = all_messages.decode('utf-8').replace("'", '"')
                                            logger.info(f'all messages in topics are - {all_message_in_topic}')
                                            string_to_json_list = re.split(r'(?<=})\B(?={)', all_message_in_topic)
                                            logger.info(f'byte stream to json objects are : {string_to_json_list}')
                                            list_after_split = re.split('\n', string_to_json_list[0])
                                            for json_msg in list_after_split:
                                                first_message_in_topic = json_msg
                                        except Exception as err:
                                            logger.info(f'Messages are in encoded format, decode format not known')
                                            logger.error(f'Exception while decoding - {str(err)}')
                                            first_message_in_topic = "UNABLE_TO_DISCOVER_SCHEMA"
                                    else:
                                        first_message_in_topic = all_messages.decode('utf-8')
                                        logger.info(f'message received is : {first_message_in_topic}')
                            finally:
                                logger.info('Finally block')
                                #consumer.close()

                            logger.info(f'Fetching message retention period for topic - {topic_name}')
                            admin_client.poll(timeout=10)
                            topic_configResource = admin_client.describe_configs(
                                [ConfigResource(restype=2, name=topic_name)], request_timeout=10)
                            for j in concurrent.futures.as_completed(iter(topic_configResource.values())):
                                config_response = j.result(timeout=1)
                                logger.info(f'config response is : {config_response}')
                                msg_retention_time_obj = config_response.get('retention.ms')
                            msg_retention_time_ms = (str(msg_retention_time_obj).split('=')[-1]).replace('"', "")
                            msg_retention_time_sec = (int(msg_retention_time_ms) / 1000)
                            logger.info(f'message retention time for topic is : {msg_retention_time_sec}')

                            logger.info(
                                f'assigning schema name with topic name: {topic_name}')
                            schema_name = topic_name

                            get_latest_schema_info_url = get_latest_schema_info_db_url + '/' + str(
                                schema_name)
                            logger.debug(
                                f'get_latest_schema_info_url - {get_latest_schema_info_url}')
                            schema_info_object = requests.get(
                                get_latest_schema_info_url, headers=headers)
                            schema_info_resp = schema_info_object.json()
                            logger.debug(
                                f'response from schema_info table - {schema_info_resp}')

                            if first_message_in_topic != "NO_MSG_TO_DISCOVER_SCHEMA" and \
                                    first_message_in_topic != "UNABLE_TO_DISCOVER_SCHEMA":
                                logger.info(
                                    f'Message existed in topic {first_message_in_topic}')
                                logger.info(f'type of message is : {type(first_message_in_topic)}')

                                if isinstance(first_message_in_topic, str):
                                    logger.info('Decoding message if in base64 format')
                                    try:
                                        is_valid = base64.b64decode(first_message_in_topic, validate=True)
                                        if is_valid is not None:
                                            logger.info(f"converting encoded data into decoded bytes")
                                            decoded_string = is_valid.decode('utf-8')
                                            logger.info(f"decoded string: {decoded_string}")
                                            str_to_dict_data = json.loads(decoded_string)
                                        else: 
                                            logger.info('Message after decode is empty')
                                    except binascii.Error as e:
                                        str_to_dict_data = json.loads(first_message_in_topic)
                                    generated_schema_from_topic = infer_avro_schema(str_to_dict_data, topic_name)
                                else:
                                    generated_schema_from_topic = infer_avro_schema(first_message_in_topic, topic_name)
                                logger.info(f'generated schema from topic is - {generated_schema_from_topic}')
                                logger.info(f'{type(generated_schema_from_topic)}')

                                if schema_info_object.status_code == 200:
                                    schema_id = schema_info_resp['id']
                                    schema_definition_from_db = json.loads(schema_info_resp.get('definition'))
                                    logger.info(
                                        f'getting schema from db - {schema_definition_from_db}')
                                    logger.info(f'generated schema from message - {generated_schema_from_topic}')

                                    if schema_definition_from_db != generated_schema_from_topic:
                                        logger.info(f'Current generated schema and stored schema are different, '
                                                    f'Hence setting schema to UNDISCOVERED')

                                        new_version_schema_info_payload_dict = {
                                            "name": schema_name,
                                            "type": "",
                                            "definition": "",
                                        }
                                        create_new_inactive_old_schema_with_schema_id_url = \
                                            create_new_inactive_old_schema_url + \
                                            "/" + str(schema_id)
                                        schema_info_object = requests.put(
                                            create_new_inactive_old_schema_with_schema_id_url,
                                            json=new_version_schema_info_payload_dict, headers=headers)
                                        schema_info_json_resp = schema_info_object.json()
                                        logger.info(
                                            f'response after inserting latest version - {schema_info_json_resp}')
                                        # latest_version_schema_id = schema_info_json_resp['id']
                                        # logger.info(
                                        #     f'updating schema topics associations')
                                        # update_schema_topic_association_to_latest_schema_version_with_ids_url = \
                                        #     update_schema_topic_association_to_latest_schema_version_url + \
                                        #     "/" + str(schema_id) + "/" + \
                                        #     str(latest_version_schema_id)
                                        # schema_topic_relation_object_resp = requests.put(
                                        #     update_schema_topic_association_to_latest_schema_version_with_ids_url,
                                        #     headers=headers)
                                        # schema_topic_relation_object_resp = schema_topic_relation_object_resp.json()
                                        # logger.info(
                                        #     f'Updated topic schema association...')
                                    else:
                                        logger.info(
                                            f'No differences found in old db schema - {schema_definition_from_db}, '
                                            f'and new generated schema - {generated_schema_from_topic}')
                                elif schema_info_object.status_code != 200:
                                    logger.debug(
                                        f'saving into schema info table')
                                    schema_info_payload = {
                                        "name": schema_name,
                                        "type": "AVRO",
                                        "definition": json.dumps(generated_schema_from_topic)
                                    }
                                    logger.debug(
                                        f'schema_info_payload is - {schema_info_payload}')
                                    logger.debug(
                                        f'{create_schema_info_url}')
                                    schema_info_object = requests.post(
                                        create_schema_info_url, json=schema_info_payload, headers=headers)
                                    schema_info_json_resp = schema_info_object.json()
                                    schema_info_object_id = schema_info_json_resp["id"]

                                    logger.info(
                                        f'After saving into Schema info DB {schema_info_json_resp} and '
                                        f'id is {schema_info_object_id}')

                                    topic_payload_dict = {
                                        "labels": {
                                            "key": "",
                                            "value": ""
                                        },
                                        "schemaSettings": {
                                            "schema": schema_name,
                                            "encoding": "JSON",
                                            "firstRevisionId": "",
                                            "lastRevisionId": ""
                                        },
                                        "kafka_bus_name": fed_kafka_bus_name,
                                        "messageRetentionDuration": f'{msg_retention_time_sec}s',
                                        "retentionSettings": {
                                            "liveDateRetentionDuration": "",
                                            "historicalDataRetentionDuration": ""
                                        },
                                        "supportedSubscriptionTypes": ""
                                    }
                                    logger.debug(
                                        f'Inserting kafka topic details-{topic_payload_dict} in fed_kafka_topics table')
                                    create_fed_kafka_topics_with_topic_name_url = "{0}/{1}".format(
                                        create_fed_kafka_topics_url, str(topic_name))
                                    fed_kafka_topics_object = requests.put(
                                        create_fed_kafka_topics_with_topic_name_url, json=topic_payload_dict, headers=headers)
                                    fed_kafka_topics_object = fed_kafka_topics_object.json()
                                    logger.info(
                                        f'fed_kafka_topics_object - {fed_kafka_topics_object}')
                                    fed_kafka_topics_object_id = fed_kafka_topics_object["id"]
                                    logger.info(
                                        f'after saving fed_kafka_topics_object-{fed_kafka_topics_object} and '
                                        f'id is {fed_kafka_topics_object_id}')

                                    logger.info(
                                        f'saving schema topics association table')
                                    schema_topic_payload_dict = {
                                        "schemas_info_id": schema_info_object_id,
                                        "kafka_topics_id": fed_kafka_topics_object_id,
                                    }
                                    schema_topic_relation_object = requests.post(
                                        create_schema_topic_url, json=schema_topic_payload_dict, headers=headers)
                                    schema_topic_relation_object = schema_topic_relation_object.json()
                                    logger.info(
                                        f'schema topics relation response {schema_topic_relation_object}')
                            else:
                                if (first_message_in_topic == "NO_MSG_TO_DISCOVER_SCHEMA" or
                                    first_message_in_topic == "UNABLE_TO_DISCOVER_SCHEMA") \
                                        and schema_info_object.status_code != 200:
                                    logger.info(
                                        f'no messages existed for this topic - {topic_name}')
                                    schema_info_payload = {
                                        "name": schema_name,
                                        "type": "",
                                        "definition": ""
                                    }
                                    logger.debug(
                                        f'schema_info_payload is - {schema_info_payload}')
                                    logger.debug(
                                        f'{create_schema_info_url}')
                                    schema_info_object = requests.post(
                                        create_schema_info_url, json=schema_info_payload, headers=headers)
                                    schema_info_json_resp = schema_info_object.json()
                                    schema_info_object_id = schema_info_json_resp["id"]

                                    logger.info(
                                        f'After saving into Schema info DB '
                                        f'{schema_info_json_resp} and id is {schema_info_object_id}')

                                    topic_payload_dict = {
                                        "labels": {
                                            "key": "",
                                            "value": ""
                                        },
                                        "schemaSettings": {
                                            "schema": schema_name,
                                            "encoding": "JSON",
                                            "firstRevisionId": "",
                                            "lastRevisionId": ""
                                        },
                                        "kafka_bus_name": fed_kafka_bus_name,
                                        "messageRetentionDuration": f'{msg_retention_time_sec}s',
                                        "retentionSettings": {
                                            "liveDateRetentionDuration": "",
                                            "historicalDataRetentionDuration": ""
                                        },
                                        "supportedSubscriptionTypes": ""
                                    }
                                    logger.debug(
                                        f'Inserting kafka topic details - '
                                        f'{topic_payload_dict} in fed_kafka_topics table')
                                    create_fed_kafka_topics_with_topic_name_url = "{0}/{1}".format(
                                        create_fed_kafka_topics_url, str(topic_name))
                                    fed_kafka_topics_object = requests.put(
                                        create_fed_kafka_topics_with_topic_name_url, json=topic_payload_dict, headers=headers)
                                    fed_kafka_topics_object = fed_kafka_topics_object.json()
                                    logger.info(
                                        f'fed_kafka_topics_object - {fed_kafka_topics_object}')
                                    fed_kafka_topics_object_id = fed_kafka_topics_object["id"]
                                    logger.info(
                                        f'after saving fed_kafka_topics_object - {fed_kafka_topics_object} '
                                        f'and id is {fed_kafka_topics_object_id}')

                                    logger.info(
                                        f'saving schema topics association table')
                                    schema_topic_payload_dict = {
                                        "schemas_info_id": schema_info_object_id,
                                        "kafka_topics_id": fed_kafka_topics_object_id,
                                    }
                                    schema_topic_relation_object = requests.post(
                                        create_schema_topic_url, json=schema_topic_payload_dict, headers=headers)
                                    schema_topic_relation_object = schema_topic_relation_object.json()
                                    logger.info(
                                        f'schema topics relation response {schema_topic_relation_object}')
                                else:
                                    logger.info('Entry already exist for this topic-schema relation')
                        except Exception as e:
                            logger.exception(f'Exception while dealing topic name - {topic_name}')
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            logger.error(f'{exc_type, fname, exc_tb.tb_lineno}')
                            continue
        else:
            logger.error(
                f'Issue while fetching the kafka bus id - {job_id}')
