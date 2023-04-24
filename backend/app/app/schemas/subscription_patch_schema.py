import re
from enum import Enum
from typing import Optional

import requests
from pydantic import BaseModel, Field, validator


class SubscriptionType(str, Enum):
    LIVE = 'LIVE'
    HISTORICAL = 'HISTORICAL'


class LiveDataSubscriptionSettings(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')


class HistoricalDataSubscriptionSettings(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    queryStartDateTime: Optional[str]
    queryEndDateTime: Optional[str]


class ScheduleSettings(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    startDateTime: Optional[str]
    endDateTime: Optional[str]
    timeZone: Optional[str]


class TimeAggregation(BaseModel):
    pass


class SpaceAggregation(BaseModel):
    pass


class AggregationSettings(BaseModel):
    description: str = None
    timeAggregation: TimeAggregation = None
    spaceAggregation: SpaceAggregation = None


class DeliveryMethodEnum(str, Enum):
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"
    TCP = "TCP"
    UDP = "UDP"


class TypeEnum(str, Enum):
    CSV = "CSV"
    JSON = "JSON"
    YAML = "YAML"


class DeliverySettings(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    method: Optional[DeliveryMethodEnum] = Field(description='Reserved for future use')
    format: Optional[TypeEnum] = Field(description='Reserved for future use')
    url: Optional[str] = None


class DataTransformationSettings(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    fieldNameChanges: Optional[str]
    fieldsReorder: Optional[str]
    fieldsToRemove: Optional[str]


class Attributes(BaseModel):
    key: Optional[str]
    value: Optional[str]


class OidcToken(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    serviceAccountEmail: Optional[str]
    audience: Optional[str]


class PushConfig(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    # pushEndpoint: str = Field(example='https://my-webhook.osc.tac.net',
    #                           description='A URL locating the endpoint to which messages '
    #                                       'should be pushed. For example, a \
    #                                                 Webhook endpoint might use https://example.com/push.')
    pushEndpoint: Optional[str] = Field(example='https://webhook.site/67c64204-c49f-46dd-8042-0d338fbcec72', description='A URL '
                                                                                                               'locating the endpoint to which messages should be pushed. For example, a Webhook endpoint might use https://example.com/push.')
    attributes: Optional[Attributes]
    oidcToken: Optional[OidcToken]

    @validator('pushEndpoint')
    def validate_push_endpoint(cls, value):
        response = requests.get(value)
        if response.status_code != 200:
            raise ValueError("Push endpoint must return a 200 status code")
        return value


class Lable(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    key: Optional[str]
    value: Optional[str]


def convert_time_to_days(time_str):
    """
    Converts a time string in the format of either '2678400s'
    into a number of days. Assumes that there are 30.44 days in a month and 365 days
    in a year.
    """
    time_dict = {
        's': 1 / 86400,
        # 'h': 1 / 24,
        # 'm': 1 / 1440,
        # 'd': 1
    }
    time_num = int(time_str[:-1])
    time_unit = time_str[-1]
    days = time_num * time_dict[time_unit]

    return days


class ExpirationPolicy(BaseModel):
    description: Optional[str] = Field(
        description='A policy that specifies the conditions for this subscription s expiration. A subscription is '
                    'considered active as long as any connected subscriber is successfully consuming messages from '
                    'the subscription or is issuing operations on the subscription. If expirationPolicy is not set, '
                    'a default policy with ttl of 31 days will be used. The minimum allowed value for '
                    'expirationPolicy.ttl is 1 day & maximum is 31days. If expirationPolicy is set, '
                    'but expirationPolicy.ttl is not set, a default policy with ttl of 31 days will be used.')
    ttl: str = Field(example='2678400s')

    @validator('ttl')
    def validate_ttl(cls, v):
        # ttl_re = re.compile(r'^\d+[s|m|h|d]$')
        ttl_re = re.compile(r'^\d+[s|]$')

        if not ttl_re.match(v):
            raise ValueError('TTL must be in seconds (s)')
        else:
            days = convert_time_to_days(v)
            if 1 > days or 31 < days:
                raise ValueError('expirationPolicy.ttl allowable range 1day – 31 days')
        return v


class DeadLetterPolicy(BaseModel):
    description: Optional[str] = Field(
        description='A policy that specifies the conditions for dead lettering messages in this subscription. If '
                    'deadLetterPolicy is not set, dead lettering is disabled.')
    deadLetterTopic: Optional[str]
    maxDeliveryAttempts: Optional[int]


class RetryPolicy(BaseModel):
    description: Optional[str] = Field(description='The minimum delay between consecutive deliveries of a given '
                                                   'message. Value should be between 0 and 600 seconds. Defaults to '
                                                   '10 seconds.',
                                       example='The minimum delay between consecutive deliveries of a given '
                                               'message. Value should be between 0 and 600 seconds. Defaults to '
                                               '10 seconds.')
    minimumBackoff: str = Field(example='3.5s')
    maximumBackoff: str = Field(example='600s')

    @validator('minimumBackoff', 'maximumBackoff')
    def validate_backoff(cls, v):
        backoff_re = re.compile(r'^\d+(\.\d+)?[s]$')
        if not backoff_re.match(v):
            raise ValueError('Backoff time must be in seconds with optional decimals minimumBackoff (e.g. 3.5s), '
                             'maximumBackoff (e.g: 600s)')
        return v


class StateEnum(str, Enum):
    ACTIVE = "ACTIVE"
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    RESOURCE_ERROR = "RESOURCE_ERROR"


class Subscription(BaseModel):
    name: str = Field(description='Name of the subscription', title='SubscriptionName')
    topic: str = Field(description='Name of the topic', title='TopicName')
    subscriptionType: Optional[SubscriptionType] = Field(description='Reserved for future use')
    filter: Optional[str] = Field(description='Reserved for future use')
    liveDataSubscriptionSettings: Optional[LiveDataSubscriptionSettings]
    historicalDataSubscriptionSettings: Optional[HistoricalDataSubscriptionSettings]
    scheduleSettings: Optional[ScheduleSettings]
    aggregationSettings: Optional[AggregationSettings]
    deliverySettings: Optional[DeliverySettings]
    dataTranformationSettings: Optional[DataTransformationSettings]
    pushConfig: Optional[PushConfig]
    ackDeadlineSeconds: Optional[int] = Field(example=10, description='The approximate amount of time (on a best-effort basis) Pub/Sub waits for the \
                                                        subscriber to acknowledge receipt before resending the message. \
                                                        In the interval after the message is delivered and before it is acknowledged,'
                                                                      ' it is considered to be outstanding. \
                                                        During that time period, the message will not be redelivered (on a best-effort basis).'
                                                                      ' For pull subscriptions, \
                                                        this value is used as the initial value for the ack deadline. \
                                                        To override this value for a given message, call \
                                                        subscriptions.modifyAckDeadline with the corresponding ackId if using pull')

    retainAckedMessages: Optional[bool] = Field(description='Indicates whether to retain acknowledged messages. If true, \
                                            then messages are not expunged from the subscription s backlog, \
                                            even if they are acknowledged, until they fall out of the messageRetentionDuration window. \
                                            This must be true if you would like to subscriptions.seek to a timestamp \
                                            in the past to replay previously-acknowledged messages.')

    messageRetentionDuration: Optional[str] = Field(example='700s', description='example: 700.5s How long to retain unacknowledged messages in \
                                                the subscription s backlog, from the moment a message is published. \
                                                If retainAckedMessages is true, then this also configures the retention of acknowledged messages.\
                                                A duration in seconds with up to nine fractional digits, terminated by s')

    labels: Optional[Lable]
    enableMessageOrdering: Optional[bool] = Field(description='If true, messages published with the same orderingKey in PubsubMessage \
                                            will be delivered to the subscribers in the order in which they are \
                                            received by the Pub/Sub system. Otherwise, they may be delivered in any order.')

    expirationPolicy: ExpirationPolicy
    deadLetterPolicy: Optional[DeadLetterPolicy]
    retryPolicy: RetryPolicy
    detached: Optional[bool]
    enableExactlyOnceDelivery: Optional[bool]

    @validator('messageRetentionDuration')
    def validate_retention(cls, v):
        retention_re = re.compile(r'^\d+[s]$')
        sec = v[:-1]
        if not retention_re.match(v):
            raise ValueError('Retention duration must be in seconds (s)')
        if int(sec) > 604800:
            raise ValueError('Message retention duration more than 7 days and duration in seconds its not allowed')
        return v
