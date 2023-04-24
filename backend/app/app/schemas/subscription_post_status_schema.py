from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Message(BaseModel):
    data: Optional[str] = Field(example='eyJjb2xvciI6ICJyZWQiLCAidmFsdWUiOiAiI2YwMCJ9', description='The message data '
                                                                                                    'field. A '
                                                                                                    'base64-encoded '
                                                                                                    'string. The '
                                                                                                    'example '
                                                                                                    'base64-encoded '
                                                                                                    'string is for '
                                                                                                    'the message "{'
                                                                                                    '"id": "1", '
                                                                                                    '"price": '
                                                                                                    '"$1.99", '
                                                                                                    '"product": '
                                                                                                    '"shirt"}" which '
                                                                                                    'is based on the '
                                                                                                    'schema in the '
                                                                                                    'example '
                                                                                                    'avro-record ('
                                                                                                    'refer to POST '
                                                                                                    '/pubsub/v1/schemas)')
    messageId: Optional[str] = Field(description='readOnly: true', example='2014-10-02T15:01:23Z')
    publishTime: Optional[datetime] = Field(example='readOnly: true')
    orderingKey: Optional[str]


class ReceivedMessage(BaseModel):
    ackId: Optional[str]
    message: Optional[Message]
    deliveryAttempt: Optional[int]


class ReceivedMessages(BaseModel):
    receivedMessages: Optional[List[ReceivedMessage]]
