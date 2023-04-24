from app.schemas.subscription_post_status_schema import ReceivedMessages
from app.schemas.subscription_put_status_schema import Subscription
from app.schemas.get_list_status_schema import SubscriptionList
from app.schemas.get_status_schema import Subscriptions
from app.schemas.subscription_put_status_schema import MyResponse
from app.schemas.publish_message_schema import PublishMessageResponse


def get_response(sub_model_obj):
    res = {
        "name": sub_model_obj.name,
        "topic": sub_model_obj.topic,
        "subscriptionType": sub_model_obj.subscriptionType,
        "filter": sub_model_obj.filter,
        "liveDataSubscriptionSettings": {},
        "historicalDataSubscriptionSettings": {"queryStartDateTime": sub_model_obj.queryStartDateTime,
                                               "queryEndDateTime": sub_model_obj.queryEndDateTime},
        "scheduleSettings": {"startDateTime": sub_model_obj.startDateTime,
                             "endDateTime": sub_model_obj.endDateTime, "timeZone": sub_model_obj.timeZone},
        "aggregationSettings": {"timeAggregation": sub_model_obj.timeAggregation,
                                "spaceAggregation": sub_model_obj.spaceAggregation},
        "deliverySettings": {"method": sub_model_obj.method,
                             "format": sub_model_obj.format, "url": sub_model_obj.url},
        "dataTranformationSettings": {"fieldNameChanges": sub_model_obj.fieldNameChanges,
                                      "fieldsReorder": sub_model_obj.fieldsReorder,
                                      "fieldsToRemove": sub_model_obj.fieldsToRemove},
        "pushConfig": {"pushEndpoint": sub_model_obj.pushEndpoint, "attributes":
            {"key": sub_model_obj.key, "value": sub_model_obj.value}},

        "oidcToken": {"serviceAccountEmail": sub_model_obj.serviceAccountEmail,
                      "audience": sub_model_obj.audience},
        "ackDeadlineSeconds": sub_model_obj.ackDeadlineSeconds,
        "retainAckedMessages": sub_model_obj.retainAckedMessages,
        "messageRetentionDuration": sub_model_obj.messageRetentionDuration,
        "labels": {},
        "enableMessageOrdering": sub_model_obj.enableMessageOrdering,
        "expirationPolicy": {"ttl": sub_model_obj.ttl},
        "deadLetterPolicy": {"deadLetterTopic": sub_model_obj.deadLetterTopic,
                             "maxDeliveryAttempts": sub_model_obj.maxDeliveryAttempts},
        "retryPolicy": {"minimumBackoff": sub_model_obj.minimumBackoff,
                        "maximumBackoff": sub_model_obj.maximumBackoff},
        "detached": sub_model_obj.detached,
        "enableExactlyOnceDelivery": sub_model_obj.enableExactlyOnceDelivery,
        "topicMessageRetentionDuration": sub_model_obj.topicMessageRetentionDuration,
        "state": sub_model_obj.state
    }
    return res


def get_all_response(list_data):
    list_of_data = []
    for sub_list in list_data:
        res = {"name": sub_list.name,
               "topic": sub_list.topic,
               "subscriptionType": sub_list.subscriptionType,
               "filter": sub_list.filter,
               "liveDataSubscriptionSettings": {},
               "historicalDataSubscriptionSettings": {
                   "queryStartDateTime": sub_list.queryStartDateTime,
                   "queryEndDateTime": sub_list.queryEndDateTime},
               "scheduleSettings": {"startDateTime": sub_list.startDateTime,
                                    "endDateTime": sub_list.endDateTime,
                                    "timeZone": sub_list.timeZone},
               "aggregationSettings": {"timeAggregation": sub_list.timeAggregation,
                                       "spaceAggregation": sub_list.spaceAggregation},
               "deliverySettings": {"method": sub_list.method,
                                    "format": sub_list.format, "url": sub_list.url},
               "dataTranformationSettings": {"fieldNameChanges": sub_list.fieldNameChanges,
                                             "fieldsReorder": sub_list.fieldsReorder,
                                             "fieldsToRemove": sub_list.fieldsToRemove},
               "pushConfig": {"pushEndpoint": sub_list.pushEndpoint, "attributes":
                   {"key": sub_list.key, "value": sub_list.value}},

               "oidcToken": {"serviceAccountEmail": sub_list.serviceAccountEmail,
                             "audience": sub_list.audience},
               "ackDeadlineSeconds": sub_list.ackDeadlineSeconds,
               "retainAckedMessages": sub_list.retainAckedMessages,
               "messageRetentionDuration": sub_list.messageRetentionDuration,
               "labels": {},
               "enableMessageOrdering": sub_list.enableMessageOrdering,
               "expirationPolicy": {"ttl": sub_list.ttl},
               "deadLetterPolicy": {"deadLetterTopic": sub_list.deadLetterTopic,
                                    "maxDeliveryAttempts": sub_list.maxDeliveryAttempts},
               "retryPolicy": {"minimumBackoff": sub_list.minimumBackoff,
                               "maximumBackoff": sub_list.maximumBackoff},
               "detached": sub_list.detached,
               "enableExactlyOnceDelivery": sub_list.enableExactlyOnceDelivery,
               "topicMessageRetentionDuration": sub_list.topicMessageRetentionDuration,
               "state": sub_list.state
               }
        list_of_data.append(res)
    return {"topics": list_of_data}


def create_response(subscribe_model):
    response = {
        "name": subscribe_model.name,
        "topic": subscribe_model.topic,
        "subscriptionType": subscribe_model.subscriptionType,
        "filter": subscribe_model.filter,
        "liveDataSubscriptionSettings": {},
        "historicalDataSubscriptionSettings": {"queryStartDateTime": subscribe_model.queryStartDateTime,
                                               "queryEndDateTime": subscribe_model.queryEndDateTime},
        "scheduleSettings": {"startDateTime": subscribe_model.startDateTime,
                             "endDateTime": subscribe_model.endDateTime, "timeZone": subscribe_model.timeZone},
        "aggregationSettings": {"timeAggregation": subscribe_model.timeAggregation,
                                "spaceAggregation": subscribe_model.spaceAggregation},
        "deliverySettings": {"method": subscribe_model.method,
                             "format": subscribe_model.format, "url": subscribe_model.url},
        "dataTranformationSettings": {"fieldNameChanges": subscribe_model.fieldNameChanges,
                                      "fieldsReorder": subscribe_model.fieldsReorder,
                                      "fieldsToRemove": subscribe_model.fieldsToRemove},
        "pushConfig": {"pushEndpoint": subscribe_model.pushEndpoint, "attributes":
            {"key": subscribe_model.key, "value": subscribe_model.value}},

        "oidcToken": {"serviceAccountEmail": subscribe_model.serviceAccountEmail,
                      "audience": subscribe_model.audience},
        "ackDeadlineSeconds": subscribe_model.ackDeadlineSeconds,
        "retainAckedMessages": subscribe_model.retainAckedMessages,
        "messageRetentionDuration": subscribe_model.messageRetentionDuration,
        "labels": {},
        "enableMessageOrdering": subscribe_model.enableMessageOrdering,
        "expirationPolicy": {"ttl": subscribe_model.ttl},
        "deadLetterPolicy": {"deadLetterTopic": subscribe_model.deadLetterTopic,
                             "maxDeliveryAttempts": subscribe_model.maxDeliveryAttempts},
        "retryPolicy": {"minimumBackoff": subscribe_model.minimumBackoff,
                        "maximumBackoff": subscribe_model.maximumBackoff},
        "detached": subscribe_model.detached,
        "enableExactlyOnceDelivery": subscribe_model.enableExactlyOnceDelivery,
        "topicMessageRetentionDuration": subscribe_model.topicMessageRetentionDuration,
        "state": subscribe_model.state
    }
    return response


def update_response(sub_obj_model):
    res = {
        "name": sub_obj_model.name,
        "topic": sub_obj_model.topic,
        "subscriptionType": sub_obj_model.subscriptionType,
        "filter": sub_obj_model.filter,
        "liveDataSubscriptionSettings": {},
        "historicalDataSubscriptionSettings": {"queryStartDateTime": sub_obj_model.queryStartDateTime,
                                               "queryEndDateTime": sub_obj_model.queryEndDateTime},
        "scheduleSettings": {"startDateTime": sub_obj_model.startDateTime,
                             "endDateTime": sub_obj_model.endDateTime, "timeZone": sub_obj_model.timeZone},
        "aggregationSettings": {"timeAggregation": sub_obj_model.timeAggregation,
                                "spaceAggregation": sub_obj_model.spaceAggregation},
        "deliverySettings": {"method": sub_obj_model.method,
                             "format": sub_obj_model.format, "url": sub_obj_model.url},
        "dataTranformationSettings": {"fieldNameChanges": sub_obj_model.fieldNameChanges,
                                      "fieldsReorder": sub_obj_model.fieldsReorder,
                                      "fieldsToRemove": sub_obj_model.fieldsToRemove},
        "pushConfig": {"pushEndpoint": sub_obj_model.pushEndpoint, "attributes":
            {"key": sub_obj_model.key, "value": sub_obj_model.value}},

        "oidcToken": {"serviceAccountEmail": sub_obj_model.serviceAccountEmail,
                      "audience": sub_obj_model.audience},
        "ackDeadlineSeconds": sub_obj_model.ackDeadlineSeconds,
        "retainAckedMessages": sub_obj_model.retainAckedMessages,
        "messageRetentionDuration": sub_obj_model.messageRetentionDuration,
        "labels": {},
        "enableMessageOrdering": sub_obj_model.enableMessageOrdering,
        "expirationPolicy": {"ttl": sub_obj_model.ttl},
        "deadLetterPolicy": {"deadLetterTopic": sub_obj_model.deadLetterTopic,
                             "maxDeliveryAttempts": sub_obj_model.maxDeliveryAttempts},
        "retryPolicy": {"minimumBackoff": sub_obj_model.minimumBackoff,
                        "maximumBackoff": sub_obj_model.maximumBackoff},
        "detached": sub_obj_model.detached,
        "enableExactlyOnceDelivery": sub_obj_model.enableExactlyOnceDelivery,
        "topicMessageRetentionDuration": sub_obj_model.topicMessageRetentionDuration,
        "state": sub_obj_model.state
    }
    return res


# return schema responses start

Subscription_Response = {
    200: {
        "description": "If successful, the response body contains data with the following format",
        "model": Subscription
    }
}
Subscription_Post_Response = {
    200: {
        "description": "Response body has the created subscription based on the following format",
        "model": ReceivedMessages
    }
}

Successful_Response = {
    200: {
        "description": "If successful, the response body contains data with the following format",
        "model": SubscriptionList
    }
}
Return_Successful_Response = {
    200: {
        "description": "The subscription corresponding to the provided subscription_name",
        "model": Subscriptions
    }
}
bad_request_responses = {
    400: {
        "description": "bad request",
        "model": MyResponse}
}
unauthorized_responses = {
    401: {
        "description": "unauthorized",
        "model": MyResponse}
}

no_subscription_found = {
    404: {
        "description": "No subscription found for the provided SubscriptionName",
        "model": MyResponse}
}
delete_no_subscription_found = {
    404: {
        "description": "No topic found for the provided TopicName",
        "model": MyResponse}
}

Resource_conflict_responses = {
    409: {
        "description": "Resource conflict",
        "model": MyResponse}
}
Unexpected_error_responses = {
    500: {
        "description": "Unexpected error",
        "model": MyResponse}
}
delete_Response = {
    200: {
        "description": "If successful, the response body is empty",
    }
}

publish_success_Response = {
    200: {
        "description": "Response body has the created subscription based on the following format",
        "model": PublishMessageResponse
    }
}
