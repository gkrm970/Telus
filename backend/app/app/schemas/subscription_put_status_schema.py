from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SubscriptionType(str, Enum):
    LIVE = 'LIVE'
    HISTORICAL = 'HISTORICAL'


class StateEnum(str, Enum):
    ACTIVE = "ACTIVE"
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    RESOURCE_ERROR = "RESOURCE_ERROR"


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
    pushEndpoint: Optional[str] = Field(description='A URL locating the endpoint to which messages '
                                                    'should be pushed. For example, a \
                                                    Webhook endpoint might use https://example.com/push.')
    attributes: Optional[Attributes]
    oidcToken: Optional[OidcToken]


class Lable(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    key: Optional[str]
    value: Optional[str]


class ExpirationPolicy(BaseModel):
    description: Optional[str] = Field(
        description='A policy that specifies the conditions for this subscription s expiration. A subscription is '
                    'considered active as long as any connected subscriber is successfully consuming messages from '
                    'the subscription or is issuing operations on the subscription. If expirationPolicy is not set, '
                    'a default policy with ttl of 31 days will be used. The minimum allowed value for '
                    'expirationPolicy.ttl is 1 day & maximum is 31days. If expirationPolicy is set, '
                    'but expirationPolicy.ttl is not set, a default policy with ttl of 31 days will be used.')
    ttl: Optional[str] = Field(example='2678400s')


class DeadLetterPolicy(BaseModel):
    description: Optional[str] = Field(
        description='A policy that specifies the conditions for dead lettering messages in this subscription. If '
                    'deadLetterPolicy is not set, dead lettering is disabled.')
    deadLetterTopic: Optional[str]
    maxDeliveryAttempts: Optional[int]


class RetryPolicy(BaseModel):
    description: Optional[str] = Field(description='The minimum delay between consecutive deliveries of a given '
                                                   'message. Value should be between 0 and 600 seconds. Defaults to '
                                                   '10 seconds.')
    minimumBackoff: Optional[str]
    maximumBackoff: Optional[str]
    maximumBackoff: Optional[str]


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

    messageRetentionDuration: Optional[str] = Field(example='700.5s', description='example: 700.5s How long to retain unacknowledged messages in \
                                                the subscription s backlog, from the moment a message is published. \
                                                If retainAckedMessages is true, then this also configures the retention of acknowledged messages.\
                                                A duration in seconds with up to nine fractional digits, terminated by s')

    labels: Optional[Lable]
    enableMessageOrdering: Optional[bool] = Field(description='If true, messages published with the same orderingKey in PubsubMessage \
                                            will be delivered to the subscribers in the order in which they are \
                                            received by the Pub/Sub system. Otherwise, they may be delivered in any order.')

    expirationPolicy: Optional[ExpirationPolicy]
    deadLetterPolicy: Optional[DeadLetterPolicy]
    retryPolicy: Optional[RetryPolicy]
    detached: Optional[bool]
    enableExactlyOnceDelivery: Optional[bool]
    topicMessageRetentionDuration: Optional[str] = Field(
        description='Output only. Indicates the minimum duration for '
                    'which a message is retained after it is '
                    'published to the subscriptions topic. If this '
                    'field is set, messages published to the '
                    'subscriptions topic in the last '
                    'topicMessageRetentionDuration are always '
                    'available to subscribers. See the '
                    'messageRetentionDuration field in Topic. This '
                    'field is set only in responses from the server; '
                    'it is ignored if it is set in any requests.')
    state: Optional[StateEnum] = Field(description='Reserved for future use')


# Error Codes Schemas #

class ErrorDetails(BaseModel):
    reason: str
    type: str


class ErrorResponse(BaseModel):
    code: int
    message: str
    status: str
    details: ErrorDetails


class MyResponse(BaseModel):
    error: ErrorResponse
