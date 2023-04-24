from datetime import datetime
import enum
from enum import Enum
from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, Enum
from app.database.session import Base
from app.schemas.subscription_schema import State, SubscriptionType
from app.schemas.schema_info_schema import SchemaType
from app.schemas.topic_schema import Encoding, SupportedSubscriptionTypes


class StatusEnum(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    trash = 'trash'


class FedKafkaBuses(Base):
    __tablename__ = "fed_kafka_buses"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    schema_registry_id = Column(Integer, ForeignKey("schema_registry.id"))
    instance_type = Column(String(length=250))
    kafka_host = Column(String(length=250))
    kafka_port = Column(Integer)
    kafka_version = Column(String(length=250))
    kafka_auth_type = Column(String(length=250))
    created_by = Column(String(length=250))
    updated_by = Column(String(length=250))
    created_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)


class SchemaRegistry(Base):
    __tablename__ = "schema_registry"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    schema_registry_host = Column(String(length=250))
    schema_registry_port = Column(Integer)
    schema_registry_version = Column(String(length=250))
    #schema_auth_type_id = Column(Integer)
    schema_auth_type = Column(String(length=250))
    created_by = Column(String(length=250))
    updated_by = Column(String(length=250))
    created_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)


class FedKafkaTopics(Base):
    __tablename__ = "fed_kafka_topics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    #kafka_bus_id = Column(Integer)
    kafka_topic_name = Column(String(length=100))
    #topic_status = Column(String(length=100))
    label_key = Column(String(length=100))
    label_value = Column(String(length=100))
    schema = Column(String(length=100))
    encoding = Column(Enum(Encoding), nullable=True)
    firstRevisionId = Column(String(length=100), default=None)
    lastRevisionId = Column(String(length=100), default=None)
    kafka_bus_name = Column(String(length=100))
    messageRetentionDuration = Column(String(length=100))
    liveDateRetentionDuration = Column(String(length=100), default=None)
    historicalDataRetentionDuration = Column(String(length=100), default=None)
    supportedSubscriptionTypes = Column(Enum(SupportedSubscriptionTypes), nullable=True)


class SchemasInfo(Base):
    __tablename__ = "schemas_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    #fed_kafkabus_id = Column(Integer)
    schema_name = Column(String(length=250), nullable=True)
    schema_type = Column(Enum(SchemaType), nullable=True)
    definition = Column(String(length=4096), nullable=True)
    revisionId = Column(String(length=250), nullable=True)
    revisionCreateTime = Column(DateTime, nullable=True, default=datetime.utcnow)
    #schema_status = Column(String(length=250), default='True', nullable=True)


class TopicSchemaAssociation(Base):
    __tablename__ = "topics_schemas_relation"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    schemas_info_id = Column(Integer, ForeignKey("schemas_info.id"))
    kafka_topics_id = Column(Integer, ForeignKey("fed_kafka_topics.id"))


class SchedularModel(Base):
    __tablename__ = "fed_kafka_scheduler"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    fed_kafka_bus_id = Column(String(length=250))
    schedular_status = Column(String(length=300),default=StatusEnum.active, nullable=False)
    frequency = Column(String(length=250))
    created_by = Column(String(length=250))
    updated_by = Column(String(length=250))
    created_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)


class AuthType(Base):
    __tablename__ = "auth_type"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    plaintext_auth_info_id = Column(Integer, ForeignKey("plaintext_authentication_info.id"))
    OAuth_auth_info_id = Column(Integer, ForeignKey("OAuthBearer_authentication_info.id"))
    scram_auth_info_id = Column(Integer, ForeignKey("scram_authentication_info.id"))
    keycloak_auth_info_id = Column(Integer, ForeignKey("keycloak_authentication_info.id"))
    GSSAPI_auth_info_id = Column(Integer, ForeignKey("GSSAPI_authentication_info.id"))
    kerberos_auth_info_id = Column(Integer, ForeignKey("kerberos_authentication_info.id"))
    SASL_auth_info_id = Column(Integer, ForeignKey("SASL_authentication_info.id"))
    SSL_auth_info_id = Column(Integer, ForeignKey("SSL_authentication_info.id"))
    LDAP_auth_info_id = Column(Integer, ForeignKey("LDAP_authentication_info.id"))
    auth_type = Column(String(length=250))
    fed_kafka_bus_name = Column(String(length=250))
    created_by = Column(String(length=250))
    updated_by = Column(String(length=250))
    created_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_datetime = Column(DateTime, nullable=False, default=datetime.utcnow)


class PlainTextAuthenticationInfo(Base):
    __tablename__ = "plaintext_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    plaintext_username = Column(String(length=250))
    plaintext_password = Column(String(length=250))


class OAuthBearerAuthenticationInfo(Base):
    __tablename__ = "OAuthBearer_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    oauth_access_token = Column(String(length=250))
    oauth_token_type = Column(String(length=250))
    oauth_security_protocol = Column(String(length=250))
    oauth_security_mechanism = Column(String(length=250))
    oauth_URL = Column(String(length=250))
    oauth_client_id = Column(String(length=250))
    oauth_client_secret = Column(String(length=250))
    oauth_expires_in = Column(String(length=250))
    oauth_refresh_token = Column(String(length=250))
    oauth_token_id = Column(String(length=250))
    oauth_user_id = Column(String(length=250))
    oauth_authorization = Column(String(length=250))
    oauth_bearer = Column(String(length=250))
    oauth_scope = Column(String(length=250))
    oauth_audience = Column(String(length=250))
    oauth_issuer = Column(String(length=250))
    oauth_expiration = Column(String(length=250))
    oauth_claim = Column(String(length=250))
    oauth_JWT = Column(String(length=250))
    oauth_refresh = Column(String(length=250))


class ScramAuthenticationInfo(Base):
    __tablename__ = "scram_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    scram_salt = Column(String(length=250))
    scram_iteration = Column(String(length=250))
    scram_nonce = Column(String(length=250))
    scram_channel_binding = Column(String(length=250))
    scram_hi = Column(String(length=250))
    scram_hi_calculation = Column(String(length=250))
    scram_client_key = Column(String(length=250))
    scram_server_Key = Column(String(length=250))
    scram_stored_key = Column(String(length=250))
    scram_proof = Column(String(length=250))


class KeycloakAuthenticationInfo(Base):
    __tablename__ = "keycloak_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    keycloak_realm = Column(String(length=250))
    keycloak_client = Column(String(length=250))
    keycloak_user = Column(String(length=250))
    keycloak_role = Column(String(length=250))
    keycloak_group = Column(String(length=250))
    keycloak_identity_provider = Column(String(length=250))
    keycloak_authenticator = Column(String(length=250))
    keycloak_flow = Column(String(length=250))
    keycloak_scope = Column(String(length=250))
    keycloak_session = Column(String(length=250))


class GSSAPIAuthenticationInfo(Base):
    __tablename__ = "GSSAPI_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    GSSAPI_authentication_mechanism = Column(String(length=250))
    GSSAPI_service_principal_name = Column(String(length=250))
    GSSAPI_credentials = Column(String(length=250))
    GSSAPI_context = Column(String(length=250))
    GSSAPI_tokens = Column(String(length=250))
    GSSAPI_quality_of_protection = Column(String(length=250))
    GSSAPI_security_context_establishment = Column(String(length=250))


class KerberosAuthenticationInfo(Base):
    __tablename__ = "kerberos_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    kerberos_authentication = Column(String(length=250))
    kerberos_tickets = Column(String(length=250))
    kerberos_KDC = Column(String(length=250))
    kerberos_principal = Column(String(length=250))
    kerberos_realm = Column(String(length=250))
    kerberos_service = Column(String(length=250))
    kerberos_keytab = Column(String(length=250))
    kerberos_TGT = Column(String(length=250))
    kerberos_SPN = Column(String(length=250))
    kerberos_GSSAPI = Column(String(length=250))


class SASLAuthenticationInfo(Base):
    __tablename__ = "SASL_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    sasl_authentication = Column(String(length=250))
    sasl_protocol = Column(String(length=250))
    sasl_mechanism = Column(String(length=250))
    sasl_credential = Column(String(length=250))
    sasl_service = Column(String(length=250))
    sasl_authorization = Column(String(length=250))
    sasl_channel_bindings = Column(String(length=250))
    sasl_security = Column(String(length=250))
    sasl_identity = Column(String(length=250))
    sasl_QOP = Column(String(length=250))


class SSLAuthenticationInfo(Base):
    __tablename__ = "SSL_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    ssl_truststore_location = Column(String(length=250))
    ssl_truststore_password = Column(String(length=250))
    ssl_keystore_location = Column(String(length=250))
    ssl_keystore_password = Column(String(length=250))
    ssl_key_password = Column(String(length=250))

    ssl_certificate_location = Column(String(length=250))
    ssl_key_location = Column(String(length=250))

    ssl_endpoint_identification_algorithm = Column(String(length=250))


class LDAPAuthenticationInfo(Base):
    __tablename__ = "LDAP_authentication_info"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    ldap_sasl_jaas_config = Column(String(length=250))
    ldap_sasl_mechanism = Column(String(length=250))
    ldap_ssl_truststore_location = Column(String(length=250))
    ldap_ssl_truststore_password = Column(String(length=250))
    ldap_security_protocol = Column(String(length=250))
    ldap_url = Column(String(length=250))
    ldap_user = Column(String(length=250))
    ldap_password = Column(String(length=250))

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    name = Column(String(length=250), nullable=True)
    # SubscriptionName = Column(String(length=250), nullable=True)
    topic = Column(String(length=250), nullable=False)
    subscriptionType = Column(String(length=250), nullable=True, default='string')
    filter = Column(String(length=250), nullable=True, default='string')
    liveDataSubscriptionSettings = Column((JSON), nullable=True, default={})
    queryStartDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    queryEndDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    startDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    endDateTime = Column(DateTime, nullable=False, default=datetime.utcnow)
    timeZone = Column(DateTime, nullable=False, default=datetime.utcnow)
    timeAggregation = Column((JSON), nullable=True, default={})
    spaceAggregation = Column((JSON), nullable=True, default={})
    method = Column(String(length=250), nullable=True, default='EMAIL')
    format = Column(String(length=250), nullable=True, default='CSV')
    url = Column(String(length=250), nullable=True, default='string')
    fieldNameChanges = Column(String(length=250), nullable=True, default='string')
    fieldsReorder = Column(String(length=250), nullable=True, default='string')
    fieldsToRemove = Column(String(length=250), nullable=True, default='string')
    pushEndpoint = Column(String(length=250), nullable=True, default=None)
    attributes = Column((JSON), nullable=True, default={})
    serviceAccountEmail = Column(String(length=250), nullable=True, default='string')
    audience = Column(String(length=250), nullable=True, default='string')
    ackDeadlineSeconds = Column((Integer),nullable=True,  default=10)
    retainAckedMessages = Column(String(length=250), nullable=True, default='true')
    messageRetentionDuration = Column(String(length=250), nullable=True, default='604800s')
    key = Column(String(length=250), nullable=True, default='string')
    value = Column(String(length=250), nullable=True, default='string')
    enableMessageOrdering = Column(String(length=250), nullable=True, default='true')
    ttl = Column(String(length=250),nullable=True, default='2678400s')
    deadLetterTopic = Column(String(length=250), nullable=True, default='string')
    maxDeliveryAttempts = Column((Integer), nullable=True, default=0)
    minimumBackoff = Column(String(length=250), nullable=True, default='10s')
    maximumBackoff = Column(String(length=250), nullable=True, default='600s')
    detached = Column(String(length=250), nullable=True, default='true')
    enableExactlyOnceDelivery = Column(String(length=250), nullable=True, default='true')
    topicMessageRetentionDuration = Column(String(length=250), nullable=True, default='string')
    state = Column(Enum(State), default=State.ACTIVE, nullable=False)
    subscription_type = Column(Enum(SubscriptionType), nullable=False)

# ************************************************************************************************************** #
# Pull Api related models
from sqlalchemy import Float

class AckIdsRecord(Base):
    __tablename__ = "ackIds"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    ackId = Column(String(length = 250), unique = False)
    subscription = Column(String(length=250), unique = False)
    topic = Column(String(length=250), unique = False)
    partition = Column(Integer)
    offset = Column(Integer)
    time = Column(DateTime)
    ack_deadline = Column(Float)
    min_backoff = Column(Float)
    max_backoff = Column(Float)
    status = Column(String(length=250), unique = False)


class SubscriptionReTry(Base):
    __tablename__ = "retry"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, default=None)
    subscription = Column(String(length=250), unique = False)
    first_pull_time = Column(DateTime)
    most_recent_pull_time = Column(DateTime)
    hit_backoff = Column(Integer)
# ################################################################################################################# #
