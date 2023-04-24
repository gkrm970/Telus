from typing import Optional, List
from pydantic import BaseModel


class PullSubscriptionInput(BaseModel):
    maxMessages: int


class AckIdsRecordSchema(BaseModel):
    subscription: str
    ackId: str
    object: str


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


class Message(BaseModel):
    data: str
    messageId: str
    publishTime: str
    orderingKey: str


class ReceivedMessage(BaseModel):
    ackId: str
    message: Message
    deliveryAttempt: int


class ReceivedMessages(BaseModel):
    receivedMessages: List[ReceivedMessage]
