from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Labels(BaseModel):
    description: Optional[str] = Field(description='Reserved for future use')
    key: Optional[str]
    value: Optional[str]


class Encoding(str, Enum):
    JSON : str = "JSON"
    BINARY: str = "BINARY"
    EMPTY: None = ''


class SchemaName(BaseModel):
    #__root__: str = Field(..., description='Name of the schema', example='test')
    schema_name: str = Field(..., description='Name of the schema', example='test')


class SchemaSettings(BaseModel):
    #schema_: Optional[SchemaName] = Field(alias='schema')
    schema_: Optional[str] = Field(..., description='Name of the schema', example='test', alias='schema')
    encoding: Optional[Encoding] = Field(example='JSON')
    firstRevisionId: Optional[str] = Field(description='Reserved for future use')
    lastRevisionId: Optional[str] = Field(description='Reserved for future use')

    class Config:  
        use_enum_values = True  # <--


class RetentionSettings(BaseModel):
    liveDateRetentionDuration: Optional[str] = Field(description='Reserved for future use')
    historicalDataRetentionDuration: Optional[str] = Field(description='Reserved for future use')


class SupportedSubscriptionTypes(str, Enum):
    LIVE: str = "LIVE"
    HISTORICAL: str = "HISTORICAL"
    EMPTY: None = ''


class KafkaTopicSchema(BaseModel):
    labels: Optional[Labels]
    schemaSettings: SchemaSettings
    kafka_bus_name: str
    messageRetentionDuration: Optional[str] = Field(example='10.5s')
    retentionSettings: Optional[RetentionSettings]
    supportedSubscriptionTypes: Optional[SupportedSubscriptionTypes] = Field(description='Reserved for future use')

    class Config:  
        use_enum_values = True  # <--


class KafkaTopicResponseSchema(BaseModel):
    labels: Optional[Labels]
    schemaSettings: SchemaSettings
    messageRetentionDuration: Optional[str] = Field(example='10.5s')
    retentionSettings: Optional[RetentionSettings]
    supportedSubscriptionTypes: Optional[SupportedSubscriptionTypes] = Field(description='Reserved for future use')


class TopicList(BaseModel):
    topics: Optional[List[KafkaTopicResponseSchema]]
