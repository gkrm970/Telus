from app.schemas.subscription_put_status_schema import MyResponse
from app.schemas.topic_schema import KafkaTopicResponseSchema, TopicList
from app.schemas.schema_info_schema import SchemaInfoResponse, SchemaList


def topic_put_create_response(kafka_topics_model):
    topic_response = {
        "id": kafka_topics_model.id,
        "labels": {
            "key": kafka_topics_model.label_key,
            "value": kafka_topics_model.label_value
        },
        "schemaSettings": {
            "schema": kafka_topics_model.schema,
            "encoding": kafka_topics_model.encoding,
            "firstRevisionId": kafka_topics_model.firstRevisionId,
            "lastRevisionId": kafka_topics_model.lastRevisionId
        },
        "messageRetentionDuration": kafka_topics_model.messageRetentionDuration,
        "retentionSettings": {
            "liveDateRetentionDuration": kafka_topics_model.liveDateRetentionDuration,
            "historicalDataRetentionDuration": kafka_topics_model.historicalDataRetentionDuration
        },
        "supportedSubscriptionTypes": kafka_topics_model.supportedSubscriptionTypes
    }
    return topic_response


def get_all_topic_response(kafka_topics_models_list):
    all_topics = []
    for kafka_topics_model in kafka_topics_models_list:
        topic_response = {
            "id": kafka_topics_model.id,
            "labels": {
                "key": kafka_topics_model.label_key,
                "value": kafka_topics_model.label_value
            },
            "schemaSettings": {
                "schema": kafka_topics_model.schema,
                "encoding": kafka_topics_model.encoding,
                "firstRevisionId": kafka_topics_model.firstRevisionId,
                "lastRevisionId": kafka_topics_model.lastRevisionId
            },
            "messageRetentionDuration": kafka_topics_model.messageRetentionDuration,
            "retentionSettings": {
                "liveDateRetentionDuration": kafka_topics_model.liveDateRetentionDuration,
                "historicalDataRetentionDuration": kafka_topics_model.historicalDataRetentionDuration
            },
            "supportedSubscriptionTypes": kafka_topics_model.supportedSubscriptionTypes
        }
        all_topics.append(topic_response)
    return {"topics": all_topics}


def schema_post_create_response(schema_model):
    schema_response = {
        "id": schema_model.id,
        "name": schema_model.schema_name,
        "type": schema_model.schema_type,
        "definition": schema_model.definition,
        "revisionId": schema_model.revisionId,
        "revisionCreateTime": schema_model.revisionCreateTime
    }
    return schema_response


def get_all_schema_response(schema_models_list):
    all_schemas = []
    for schema_model in schema_models_list:
        schema_response = {
            "id": schema_model.id,
            "name": schema_model.schema_name,
            "type": schema_model.schema_type,
            "definition": schema_model.definition,
            "revisionId": schema_model.revisionId,
            "revisionCreateTime": schema_model.revisionCreateTime
        }
        all_schemas.append(schema_response)
    return {"schemas": all_schemas}


# return schema responses start

Topic_Put_Successful_Response = {
    200: {
        "description": "Response body has the created resource topic based on the following format",
        "model": KafkaTopicResponseSchema
    }
}

Schema_Post_Successful_Response = {
    200: {
        "description": "Response body has the schema corresponding to the provided SchemaName based on the "
                       "following format",
        "model": SchemaInfoResponse
    }
}
no_schema_found = {
    404: {
        "description": "No schema found for the provided SchemaName",
        "model": MyResponse}
}

delete_Response = {
    200: {
        "description": "If successful, the response body is empty",
    }
}

Get_all_topic_Successful_Response = {
    200: {
        "description": "If successful, the response body contains data with the following format",
        "model": TopicList
    }
}

Get_all_schema_Successful_Response = {
    200: {
        "description": "If successful, the response body contains data with the following format",
        "model": SchemaList
    }
}
