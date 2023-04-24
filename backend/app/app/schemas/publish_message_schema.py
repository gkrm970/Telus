from __future__ import annotations
from typing import List, Optional
from enum import Enum
from fastapi import Path
from pydantic import BaseModel, Field

# configure_num = 20

class Data(BaseModel):
    data: str = Field(..., description="The message data field. A base64-encoded string.")
    orderingKey: str


class Messages(BaseModel):
    messages: List[Data]


class enum_data(str, Enum):
    JSON = "JSON"
    BINARY = "BINARY"


class enum_definition(str, Enum):
    LIVE = "LIVE"
    HISTORICAL = "HISTORICAL"


class Definition(BaseModel):
    key: str = Field(example="")
    value: str = Field(example="")



class SchemaSettings(BaseModel):
    Schema: str = Field(alias="schema", description="Reserved for future use", example="test")
    encoding: enum_data
    firstRevisionId: str = Field(description="Reserved for future use")
    lastRevisionId: str = Field(description="Reserved for future use")


class RetentionSettings(BaseModel):
    liveDateRetentionDuration: str = Field(description="Reserved for future use")
    historicalDataRetentionDuration: str = Field(description="Reserved for future use")


class Topic(BaseModel):
    labels: Definition = Path(description="Reserved for future use")
    schemaSettings: SchemaSettings
    messageRetentionDuration: str = Field(example="10.5s")
    retentionSettings: RetentionSettings
    supportedSubscriptionTypes: enum_definition = Path(description="Reserved for future use")


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


class PublishMessageResponse(BaseModel):
    messageIds: List[str] 
    class Config:
         schema_extra = { "example": { "messageIds": ["6886725847298471"] } }
