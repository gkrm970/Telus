from app.schemas.entity import AuthSettings as AuthTypeSchema
from app.models.models import AuthType, GSSAPIAuthenticationInfo, KeycloakAuthenticationInfo, LDAPAuthenticationInfo, OAuthBearerAuthenticationInfo, PlainTextAuthenticationInfo, SASLAuthenticationInfo, SSLAuthenticationInfo, ScramAuthenticationInfo, KerberosAuthenticationInfo, FedKafkaBuses
from app.api.utils.enums import AuthTypeEnum
from sqlalchemy import exc
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger


API_NAME = "Crud Auth Type"
logger_conf = [
    {
        "handler_name": settings.LOGGER_HANDLER_NAME,
        "log_level": settings.TINAA_LOG_LEVEL,
        "log_format": settings.LOGGER_FORMAT,
        "date_format": settings.LOGGER_DATE_FORMAT,
        "app_code": settings.LOGGER_APP_CODE,
        "app_name": API_NAME,
    }
]
logger = get_app_logger(log_conf=logger_conf, logger_name=API_NAME)


class CrudAuthType:
    def create(db: Session, auth_type_schema: AuthTypeSchema):
        logger.info("Inside crudAuthType")
        dict_data = auth_type_schema.__dict__
        auth_type = dict_data["auth_type"]
        fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
        logger.info(f'auth type - {auth_type} and bus name - {fed_kafka_bus_name}')
        try:
            logger.info(f'Checking if Data already exists with this auth_type: {auth_type} and fed_kafka_bus_name: {fed_kafka_bus_name}')
            #existing_auth_data = (db.query(AuthType).filter(AuthType.auth_type == auth_type and AuthType.fed_kafka_bus_name == fed_kafka_bus_name).first())
            existing_auth_data = (db.query(AuthType).filter(AuthType.auth_type == auth_type, AuthType.fed_kafka_bus_name == fed_kafka_bus_name).first())
            logger.info(f'existing auth type - {existing_auth_data}')
            if existing_auth_data:
                res = {"status_message": "Data already exists for the given information", "status_code": 200}
                return res
            
            if auth_type == AuthTypeEnum.OAUTHBEARER.value:
                logger.info("Inserting values for OAUTHBEARER auth_type")
                auth_info = OAuthBearerAuthenticationInfo()
                auth_info.oauth_access_token=dict_data["oauth_access_token"]
                auth_info.oauth_token_type=dict_data["oauth_token_type"]
                auth_info.oauth_security_protocol=dict_data["oauth_security_protocol"]
                auth_info.oauth_security_mechanism=dict_data["oauth_security_mechanism"]
                auth_info.oauth_URL=dict_data["oauth_URL"]
                auth_info.oauth_client_secret=dict_data["oauth_client_secret"]
                auth_info.oauth_client_id=dict_data["oauth_client_id"]
                auth_info.oauth_expires_in=dict_data["oauth_expires_in"]
                auth_info.oauth_refresh_token=dict_data["oauth_refresh_token"]
                auth_info.oauth_token_id=dict_data["oauth_token_id"]
                auth_info.oauth_user_id=dict_data["oauth_user_id"]
                auth_info.oauth_authorization=dict_data["oauth_authorization"]
                auth_info.oauth_bearer=dict_data["oauth_bearer"]
                auth_info.oauth_scope=dict_data["oauth_scope"]
                auth_info.oauth_audience=dict_data["oauth_audience"]
                auth_info.oauth_issuer=dict_data["oauth_issuer"]
                auth_info.oauth_expiration=dict_data["oauth_expiration"]
                auth_info.oauth_claim=dict_data["oauth_claim"]
                auth_info.oauth_JWT=dict_data["oauth_JWT"]
                auth_info.oauth_refresh=dict_data["oauth_refresh"]
                logger.info("Storing OAUTHBEARER configuration values in database")
                db.add(auth_info)
                db.commit()
                db.refresh(auth_info)
                

                auth_data = AuthType(
                    OAuth_auth_info_id=auth_info.id,
                    auth_type=dict_data["auth_type"],
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
            elif auth_type == AuthTypeEnum.PLAINTEXT.value:
                logger.info("Inserting values for PLAINTEXT auth_type")
                auth_info_data = PlainTextAuthenticationInfo(
                    plaintext_username=dict_data["plaintext_username"],
                    plaintext_password=dict_data["plaintext_password"]
                )
                logger.info("Storing PLAINTEXT configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    plaintext_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)  
                
                
            elif auth_type == AuthTypeEnum.SCRAM.value:
                logger.info("Inserting values for SCRAM auth_type")
                auth_info_data = ScramAuthenticationInfo(
                    scram_salt=dict_data["scram_salt"],
                    scram_iteration=dict_data["scram_iteration"],
                    scram_nonce=dict_data["scram_nonce"],
                    scram_channel_binding=dict_data["scram_channel_binding"],
                    scram_hi=dict_data["scram_hi"],
                    scram_hi_calculation=dict_data["scram_hi_calculation"],
                    scram_client_key=dict_data["scram_client_key"],
                    scram_server_Key=dict_data["scram_server_Key"],
                    scram_stored_key=dict_data["scram_stored_key"],
                    scram_proof=dict_data["scram_proof"]
                )
                logger.info("Storing SCRAM configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    scram_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
            
            elif auth_type == AuthTypeEnum.KEYCLOAK.value:
                logger.info("Inserting values for KEYCLOAK auth_type")
                auth_info_data = KeycloakAuthenticationInfo(
                    keycloak_realm=dict_data["keycloak_realm"],
                    keycloak_client=dict_data["keycloak_client"],
                    keycloak_user=dict_data["keycloak_user"],
                    keycloak_role=dict_data["keycloak_role"],
                    keycloak_group=dict_data["keycloak_group"],
                    keycloak_identity_provider=dict_data["keycloak_identity_provider"],
                    keycloak_authenticator=dict_data["keycloak_authenticator"],
                    keycloak_flow=dict_data["keycloak_flow"],
                    keycloak_scope=dict_data["keycloak_scope"],
                    keycloak_session=dict_data["keycloak_session"]
                )
                logger.info("Storing KEYCLOAK configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    keycloak_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
                
            elif auth_type == AuthTypeEnum.GSSAPI.value:
                logger.info("Inserting values for GSSAPI auth_type")
                auth_info_data = GSSAPIAuthenticationInfo(
                    GSSAPI_authentication_mechanism=dict_data["GSSAPI_authentication_mechanism"],
                    GSSAPI_service_principal_name=dict_data["GSSAPI_service_principal_name"],
                    GSSAPI_credentials=dict_data["GSSAPI_credentials"],
                    GSSAPI_context=dict_data["GSSAPI_context"],
                    GSSAPI_tokens=dict_data["GSSAPI_tokens"],
                    GSSAPI_quality_of_protection=dict_data["GSSAPI_quality_of_protection"],
                    GSSAPI_security_context_establishment=dict_data["GSSAPI_security_context_establishment"]
                )
                logger.info("Storing GSSAPI configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    GSSAPI_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
            
            elif auth_type == AuthTypeEnum.KERBEROS.value:
                logger.info("Inserting values for KERBEROS auth_type")
                auth_info_data = kerberosAuthenticationInfo(
                    kerberos_authentication=dict_data["kerberos_authentication"],
                    kerberos_tickets=dict_data["kerberos_tickets"],
                    kerberos_KDC=dict_data["kerberos_KDC"],
                    kerberos_principal=dict_data["kerberos_principal"],
                    kerberos_realm=dict_data["kerberos_realm"],
                    kerberos_service=dict_data["kerberos_service"],
                    kerberos_keytab=dict_data["kerberos_keytab"],
                    kerberos_TGT=dict_data["kerberos_TGT"],
                    kerberos_SPN=dict_data["kerberos_SPN"],
                    kerberos_GSSAPI=dict_data["kerberos_GSSAPI"]
                )
                logger.info("Storing KERBEROS configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    kerberos_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
                
            elif auth_type == AuthTypeEnum.SASL.value:
                logger.info("Inserting values for SASL auth_type")
                logger.info("inside function...........")
                auth_info_data = SASLAuthenticationInfo(
                    sasl_authentication=dict_data["sasl_authentication"],
                    sasl_protocol=dict_data["sasl_protocol"],
                    sasl_mechanism=dict_data["sasl_mechanism"],
                    sasl_credential=dict_data["sasl_credential"],
                    sasl_service=dict_data["sasl_service"],
                    sasl_authorization=dict_data["sasl_authorization"],
                    sasl_channel_bindings=dict_data["sasl_channel_bindings"],
                    sasl_security=dict_data["sasl_security"],
                    sasl_identity=dict_data["sasl_identity"],
                    sasl_QOP=dict_data["sasl_QOP"]
                )
                logger.info("Storing SASL configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    SASL_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
                
            elif auth_type == AuthTypeEnum.SSL.value:
                logger.info("Inserting values for SSL auth_type")
                auth_info_data = SSLAuthenticationInfo(
                    ssl_truststore_location=dict_data["ssl_truststore_location"],
                    ssl_truststore_password=dict_data["ssl_truststore_password"],
                    ssl_keystore_location=dict_data["ssl_keystore_location"],
                    ssl_keystore_password=dict_data["ssl_keystore_password"],

                    ssl_certificate_location=dict_data["ssl_certificate_location"],
                    ssl_key_location=dict_data["ssl_key_location"],

                    ssl_key_password=dict_data["ssl_key_password"],
                    ssl_endpoint_identification_algorithm=dict_data["ssl_endpoint_identification_algorithm"]
                )
                logger.info("Storing SSL configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    SSL_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
                
            elif auth_type == AuthTypeEnum.LDAP.value:
                logger.info("Inserting values for LDAP auth_type")
                auth_info_data = LDAPAuthenticationInfo(
                    ldap_sasl_jaas_config=dict_data["ldap_sasl_jaas_config"],
                    ldap_sasl_mechanism=dict_data["ldap_sasl_mechanism"],
                    ldap_ssl_truststore_location=dict_data["ldap_ssl_truststore_location"],
                    ldap_ssl_truststore_password=dict_data["ldap_ssl_truststore_password"],
                    ldap_security_protocol = dict_data["ldap_security_protocol"],
                    ldap_url= dict_data["ldap_url"],
                    ldap_user=dict_data["ldap_user"],
                    ldap_password=dict_data["ldap_password"]
                )
                logger.info("Storing LDAP configuration values in database")
                db.add(auth_info_data)
                db.commit()
                db.refresh(auth_info_data)

                auth_data = AuthType(
                    LDAP_auth_info_id=auth_info_data.id,
                    fed_kafka_bus_name=dict_data["fed_kafka_bus_name"],
                    auth_type=dict_data["auth_type"],
                    created_by=dict_data["created_by"],
                    updated_by=dict_data["updated_by"]
                )
                db.add(auth_data)
                db.commit()
                db.refresh(auth_data)
                
            else:
                raise ValueError(f"Invalid auth_type: {auth_type}, value must be in {AuthTypeEnum.list()}")

            res =  {"status": "Record Inserted Successfully", "status_code": 200}   
            return res 
                     
        except Exception as e:
            db.rollback()
            raise e
        
        

    def update_auth_type_info(db: Session, auth_type_info_id: int, auth_type_info: str):
        dict_data = auth_type_info.__dict__
        auth_info_model = db.query(AuthType).filter(AuthType.id == auth_type_info_id).first()
        logger.info("Querying the Auth_type table and get the details from the database")
        if auth_info_model is None:
            raise HTTPException(status_code=404, detail="Record not Found")
        try:
            if auth_info_model.auth_type == AuthTypeEnum.OAUTHBEARER.value:
                logger.info("updating values for OAUTHBEARER auth_type table")
                auth_model = db.query(OAuthBearerAuthenticationInfo).filter(OAuthBearerAuthenticationInfo.id == auth_info_model.OAuth_auth_info_id).first()
                auth_model.oauth_access_token = dict_data["oauth_access_token"]
                auth_model.oauth_token_type = dict_data["oauth_token_type"]
                auth_model.oauth_security_protocol = dict_data["oauth_security_protocol"]
                auth_model.oauth_security_mechanism = dict_data["oauth_security_mechanism"]
                auth_model.oauth_URL = dict_data["oauth_URL"]
                auth_model.oauth_client_secret = dict_data["oauth_client_secret"]
                auth_model.oauth_client_id = dict_data["oauth_client_id"]
                auth_model.oauth_expires_in = dict_data["oauth_expires_in"]
                auth_model.oauth_refresh_token = dict_data["oauth_refresh_token"]
                auth_model.oauth_token_id = dict_data["oauth_token_id"]
                auth_model.oauth_user_id = dict_data["oauth_user_id"]
                auth_model.oauth_authorization = dict_data["oauth_authorization"]
                auth_model.oauth_bearer = dict_data["oauth_bearer"]
                auth_model.oauth_scope = dict_data["oauth_scope"]
                auth_model.oauth_audience = dict_data["oauth_audience"]
                auth_model.oauth_issuer = dict_data["oauth_issuer"]
                auth_model.oauth_expiration = dict_data["oauth_expiration"]
                auth_model.oauth_claim = dict_data["oauth_claim"]
                auth_model.oauth_JWT = dict_data["oauth_JWT"]
                auth_model.oauth_refresh = dict_data["oauth_refresh"]
                
                db.add(auth_model)
                db.flush()
                db.commit()

                auth_info_model.OAuth_auth_info_id = auth_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()

            elif auth_info_model.auth_type == AuthTypeEnum.PLAINTEXT.value:
                logger.info("updating values for PLAINTEXT auth_type table")
                authinfo_model = db.query(PlainTextAuthenticationInfo).filter(PlainTextAuthenticationInfo.id == auth_info_model.plaintext_auth_info_id).first()
                logger.info(f'auth_info_model_id : {auth_info_model.id}')
                
                authinfo_model.plaintext_username = dict_data["plaintext_username"]
                authinfo_model.plaintext_password = dict_data["plaintext_password"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.plaintext_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
                
            elif auth_info_model.auth_type == AuthTypeEnum.SCRAM.value:
                logger.info("updating values for SCRAM auth_type table")
                authinfo_model = db.query(ScramAuthenticationInfo).filter(ScramAuthenticationInfo.id == auth_info_model.scram_auth_info_id).first()
                
                authinfo_model.scram_salt=dict_data["scram_salt"]
                authinfo_model.scram_iteration=dict_data["scram_iteration"]
                authinfo_model.scram_nonce=dict_data["scram_nonce"]
                authinfo_model.scram_channel_binding=dict_data["scram_channel_binding"]
                authinfo_model.scram_hi=dict_data["scram_hi"]
                authinfo_model.scram_hi_calculation=dict_data["scram_hi_calculation"]
                authinfo_model.scram_client_key=dict_data["scram_client_key"]
                authinfo_model.scram_server_Key=dict_data["scram_server_Key"]
                authinfo_model.scram_stored_key=dict_data["scram_stored_key"]
                authinfo_model.scram_proof=dict_data["scram_proof"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.scram_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
                
            elif auth_info_model.auth_type == AuthTypeEnum.KEYCLOAK.value:
                logger.info("updating values for KEYCLOAK auth_type table")
                authinfo_model = db.query(KeycloakAuthenticationInfo).filter(KeycloakAuthenticationInfo.id == auth_info_model.keycloak_auth_info_id).first()
                authinfo_model.keycloak_realm=dict_data["keycloak_realm"]
                authinfo_model.keycloak_client=dict_data["keycloak_client"]
                authinfo_model.keycloak_user=dict_data["keycloak_user"]
                authinfo_model.keycloak_role=dict_data["keycloak_role"]
                authinfo_model.keycloak_group=dict_data["keycloak_group"]
                authinfo_model.keycloak_identity_provider=dict_data["keycloak_identity_provider"]
                authinfo_model.keycloak_authenticator=dict_data["keycloak_authenticator"]
                authinfo_model.keycloak_flow=dict_data["keycloak_flow"]
                authinfo_model.keycloak_scope=dict_data["keycloak_scope"]
                authinfo_model.keycloak_session=dict_data["keycloak_session"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.keycloak_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
                
            elif auth_info_model.auth_type == AuthTypeEnum.GSSAPI.value:
                logger.info("updating values for GSSAPI auth_type table")
                authinfo_model = db.query(GSSAPIAuthenticationInfo).filter(GSSAPIAuthenticationInfo.id == auth_info_model.GSSAPI_auth_info_id).first()
                authinfo_model.GSSAPI_authentication_mechanism=dict_data["GSSAPI_authentication_mechanism"]
                authinfo_model.GSSAPI_service_principal_name=dict_data["GSSAPI_service_principal_name"]
                authinfo_model.GSSAPI_credentials=dict_data["GSSAPI_credentials"]
                authinfo_model.GSSAPI_context=dict_data["GSSAPI_context"]
                authinfo_model.GSSAPI_tokens=dict_data["GSSAPI_tokens"]
                authinfo_model.GSSAPI_quality_of_protection=dict_data["GSSAPI_quality_of_protection"]
                authinfo_model.GSSAPI_security_context_establishment=dict_data["GSSAPI_security_context_establishment"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.GSSAPI_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
                
            elif auth_info_model.auth_type == AuthTypeEnum.KERBEROS.value:
                logger.info("updating values for KERBEROS auth_type table")
                authinfo_model = db.query(kerberosAuthenticationInfo).filter(kerberosAuthenticationInfo.id == auth_info_model.kerberos_auth_info_id).first()
                authinfo_model.kerberos_authentication=dict_data["kerberos_authentication"]
                authinfo_model.kerberos_tickets=dict_data["kerberos_tickets"]
                authinfo_model.kerberos_KDC=dict_data["kerberos_KDC"]
                authinfo_model.kerberos_principal=dict_data["kerberos_principal"]
                authinfo_model.kerberos_realm=dict_data["kerberos_realm"]
                authinfo_model.kerberos_service=dict_data["kerberos_service"]
                authinfo_model.kerberos_keytab=dict_data["kerberos_keytab"]
                authinfo_model.kerberos_TGT=dict_data["kerberos_TGT"]
                authinfo_model.kerberos_SPN=dict_data["kerberos_SPN"]
                authinfo_model.kerberos_GSSAPI=dict_data["kerberos_GSSAPI"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.kerberos_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
                
            elif auth_info_model.auth_type == AuthTypeEnum.SASL.value:
                logger.info("updating values for SASL auth_type table")
                authinfo_model = db.query(SASLAuthenticationInfo).filter(SASLAuthenticationInfo.id == auth_info_model.SASL_auth_info_id).first()
                authinfo_model.sasl_authentication=dict_data["sasl_authentication"]
                authinfo_model.sasl_protocol=dict_data["sasl_protocol"]
                authinfo_model.sasl_mechanism=dict_data["sasl_mechanism"]
                authinfo_model.sasl_credential=dict_data["sasl_credential"]
                authinfo_model.sasl_service=dict_data["sasl_service"]
                authinfo_model.sasl_authorization=dict_data["sasl_authorization"]
                authinfo_model.sasl_channel_bindings=dict_data["sasl_channel_bindings"]
                authinfo_model.sasl_security=dict_data["sasl_security"]
                authinfo_model.sasl_identity=dict_data["sasl_identity"]
                authinfo_model.sasl_QOP=dict_data["sasl_QOP"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.SASL_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                
            elif auth_info_model.auth_type == AuthTypeEnum.SSL.value:
                logger.info("updating values for SSL auth_type table")
                authinfo_model = db.query(SSLAuthenticationInfo).filter(SSLAuthenticationInfo.id == auth_info_model.SSL_auth_info_id).first()
                authinfo_model.ssl_truststore_location=dict_data["ssl_truststore_location"]
                authinfo_model.ssl_truststore_password=dict_data["ssl_truststore_password"]
                authinfo_model.ssl_keystore_location=dict_data["ssl_keystore_location"]

                authinfo_model.ssl_key_location = dict_data["ssl_key_location"]
                authinfo_model.ssl_certificate_location = dict_data["ssl_certificate_location"]

                authinfo_model.ssl_keystore_password=dict_data["ssl_keystore_password"]
                authinfo_model.ssl_key_password=dict_data["ssl_key_password"]
                authinfo_model.ssl_endpoint_identification_algorithm=dict_data["ssl_endpoint_identification_algorithm"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.SSL_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
                    
            elif auth_info_model.auth_type == AuthTypeEnum.LDAP.value:
                logger.info("updating values for LDAP auth_type table")
                authinfo_model = db.query(LDAPAuthenticationInfo).filter(LDAPAuthenticationInfo.id == auth_info_model.LDAP_auth_info_id).first()
                authinfo_model.ldap_sasl_jaas_config=dict_data["ldap_sasl_jaas_config"]
                authinfo_model.ldap_sasl_mechanism=dict_data["ldap_sasl_mechanism"]
                authinfo_model.ldap_ssl_truststore_location=dict_data["ldap_ssl_truststore_location"]
                authinfo_model.ldap_ssl_truststore_password=dict_data["ldap_ssl_truststore_password"]
                authinfo_model.ldap_security_protocol = dict_data["ldap_security_protocol"]
                authinfo_model.ldap_url= dict_data["ldap_url"]
                authinfo_model.ldap_user=dict_data["ldap_user"]
                authinfo_model.ldap_password=dict_data["ldap_password"]
                
                db.add(authinfo_model)
                db.flush()
                db.commit()

                auth_info_model.LDAP_auth_info_id = authinfo_model.id
                auth_info_model.auth_type = dict_data["auth_type"]
                auth_info_model.fed_kafka_bus_name = dict_data["fed_kafka_bus_name"]
                auth_info_model.created_by = dict_data["created_by"]
                auth_info_model.updated_by = dict_data["updated_by"]

                db.add(auth_info_model)
                db.flush()
                db.commit()
            else:
                return "Invalid Auth_type values"

        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("DataBase Connection Error", e)
    
    
    def get_data_by_id(db: Session,auth_type_info_name: str, fed_kafka_bus_name_info :str):
        logger.info("querying and getting records by using get_data_by_id")
        auth_type_obj = db.query(AuthType).filter(AuthType.auth_type == auth_type_info_name).filter(AuthType.fed_kafka_bus_name == fed_kafka_bus_name_info).first()
        try:
            if auth_type_obj:
                if auth_type_info_name == AuthTypeEnum.PLAINTEXT.value:
                    plaintext_id = auth_type_obj.plaintext_auth_info_id
                    plaintext_obj = db.query(PlainTextAuthenticationInfo).filter(PlainTextAuthenticationInfo.id == plaintext_id).first()
                    logger.info("querying and getting records by using get_data_by_id for PLAINTEXT auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "plaintext_id":plaintext_obj.id,
                        "plaintext_username": plaintext_obj.plaintext_username,
                        "plaintext_password":plaintext_obj.plaintext_password,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
            
                    
                elif auth_type_info_name == AuthTypeEnum.OAUTHBEARER.value:
                    OAuth_id = auth_type_obj.OAuth_auth_info_id
                    OAUth_obj = db.query(OAuthBearerAuthenticationInfo).filter(OAuthBearerAuthenticationInfo.id == OAuth_id).first()
                    logger.info("querying and getting records by using get_data_by_id for OAUTHBEARER auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "OAuth_auth_info_id":auth_type_obj.OAuth_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "OAuth_info_id":OAUth_obj.id,
                        "oauth_access_token":OAUth_obj.oauth_access_token,
                        "oauth_token_type":OAUth_obj.oauth_token_type,
                        "oauth_security_protocol":OAUth_obj.oauth_security_protocol,
                        "oauth_security_mechanism":OAUth_obj.oauth_security_mechanism,
                        "oauth_URL":OAUth_obj.oauth_URL,
                        "oauth_client_secret":OAUth_obj.oauth_client_secret,
                        "oauth_client_id":OAUth_obj.oauth_client_id,
                        "oauth_expires_in":OAUth_obj.oauth_expires_in,
                        "oauth_refresh_token":OAUth_obj.oauth_refresh_token,
                        "oauth_token_id":OAUth_obj.oauth_token_id,
                        "oauth_user_id":OAUth_obj.oauth_user_id,
                        "oauth_authorization":OAUth_obj.oauth_authorization,
                        "oauth_bearer":OAUth_obj.oauth_bearer,
                        "oauth_scope":OAUth_obj.oauth_scope,
                        "oauth_audience":OAUth_obj.oauth_audience,
                        "oauth_issuer":OAUth_obj.oauth_issuer,
                        "oauth_expiration":OAUth_obj.oauth_expiration,
                        "oauth_claim":OAUth_obj.oauth_claim,
                        "oauth_JWT":OAUth_obj.oauth_JWT,
                        "oauth_refresh":OAUth_obj.oauth_refresh,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.SCRAM.value:
                    scram_id = auth_type_obj.scram_auth_info_id
                    scram_obj = db.query(ScramAuthenticationInfo).filter(ScramAuthenticationInfo.id == scram_id).first()
                    logger.info("querying and getting records by using get_data_by_id for SCRAM auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "scram_auth_info_id":auth_type_obj.scram_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "scram_info_id":scram_obj.id,
                        "scram_salt":scram_obj.scram_salt,
                        "scram_iteration":scram_obj.scram_salt,
                        "scram_nonce":scram_obj.scram_nonce,
                        "scram_channel_binding":scram_obj.scram_channel_binding,
                        "scram_hi":scram_obj.scram_hi,
                        "scram_hi_calculation":scram_obj.scram_hi_calculation,
                        "scram_client_key":scram_obj.scram_client_key,
                        "scram_server_Key":scram_obj.scram_server_Key,
                        "scram_stored_key":scram_obj.scram_stored_key,
                        "scram_proof":scram_obj.scram_proof,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.KEYCLOAK.value:
                    keycloak_id = auth_type_obj.keycloak_auth_info_id
                    keycloak_obj = db.query(KeycloakAuthenticationInfo).filter(KeycloakAuthenticationInfo.id == keycloak_id).first()
                    logger.info("querying and getting records by using get_data_by_id for KEYCLOAK auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "keycloak_auth_info_id":auth_type_obj.keycloak_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "keycloak_info_id":keycloak_obj.id,
                        "keycloak_realm":keycloak_obj.keycloak_realm,
                        "keycloak_client":keycloak_obj.keycloak_client,
                        "keycloak_user":keycloak_obj.keycloak_user,
                        "keycloak_role":keycloak_obj.keycloak_role,
                        "keycloak_group":keycloak_obj.keycloak_group,
                        "keycloak_identity_provider":keycloak_obj.keycloak_identity_provider,
                        "keycloak_authenticator":keycloak_obj.keycloak_authenticator,
                        "keycloak_flow":keycloak_obj.keycloak_flow,
                        "keycloak_scope":keycloak_obj.keycloak_scope,
                        "keycloak_session":keycloak_obj.keycloak_session,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.GSSAPI.value:
                    logger.info("querying and getting records by using get_data_by_id for GSSAPI auth_type")
                    gssapi_id = auth_type_obj.GSSAPI_auth_info_id
                    gssapi_obj = db.query(GSSAPIAuthenticationInfo).filter(GSSAPIAuthenticationInfo.id == gssapi_id).first()
                    data = {
                        "id": auth_type_obj.id,
                        "GSSAPI_auth_info_id":auth_type_obj.GSSAPI_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "gssapi_info_id":gssapi_obj.id,
                        "GSSAPI_authentication_mechanism":gssapi_obj.GSSAPI_authentication_mechanism,
                        "GSSAPI_service_principal_name":gssapi_obj.GSSAPI_service_principal_name,
                        "GSSAPI_credentials":gssapi_obj.GSSAPI_credentials,
                        "GSSAPI_context":gssapi_obj.GSSAPI_context,
                        "GSSAPI_tokens":gssapi_obj.GSSAPI_tokens,
                        "GSSAPI_quality_of_protection":gssapi_obj.GSSAPI_quality_of_protection,
                        "GSSAPI_security_context_establishment":gssapi_obj.GSSAPI_security_context_establishment,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.KERBEROS.value:
                    kerberos_id = auth_type_obj.kerberos_auth_info_id
                    kerberos_obj = db.query(kerberosAuthenticationInfo).filter(kerberosAuthenticationInfo.id == kerberos_id).first()
                    logger.info("querying and getting records by using get_data_by_id for KERBEROS auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "kerberos_auth_info_id":auth_type_obj.kerberos_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "kerberos_info_id":kerberos_obj.id,
                        "kerberos_authentication":kerberos_obj.kerberos_authentication,
                        "kerberos_tickets":kerberos_obj.kerberos_tickets,
                        "kerberos_KDC":kerberos_obj.kerberos_KDC,
                        "kerberos_principal":kerberos_obj.kerberos_principal,
                        "kerberos_realm":kerberos_obj.kerberos_realm,
                        "kerberos_service":kerberos_obj.kerberos_service,
                        "kerberos_keytab":kerberos_obj.kerberos_keytab,
                        "kerberos_TGT":kerberos_obj.kerberos_TGT,
                        "kerberos_SPN":kerberos_obj.kerberos_SPN,
                        "kerberos_GSSAPI":kerberos_obj.kerberos_GSSAPI,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.SASL.value:
                    sasl_id = auth_type_obj.SASL_auth_info_id
                    sasl_obj = db.query(SASLAuthenticationInfo).filter(SASLAuthenticationInfo.id == sasl_id).first()
                    logger.info("querying and getting records by using get_data_by_id for SASL auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "SASL_auth_info_id":auth_type_obj.SASL_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "sasl_info_id":sasl_obj.id,
                        "sasl_authentication":sasl_obj.sasl_authentication,
                        "sasl_protocol":sasl_obj.sasl_protocol,
                        "sasl_mechanism":sasl_obj.sasl_mechanism,
                        "sasl_credential":sasl_obj.sasl_credential,
                        "sasl_service":sasl_obj.sasl_service,
                        "sasl_authorization":sasl_obj.sasl_authorization,
                        "sasl_channel_bindings":sasl_obj.sasl_channel_bindings,
                        "sasl_security":sasl_obj.sasl_security,
                        "sasl_identity":sasl_obj.sasl_identity,
                        "sasl_QOP":sasl_obj.sasl_QOP,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.SSL.value:
                    ssl_id = auth_type_obj.SSL_auth_info_id
                    ssl_obj = db.query(SSLAuthenticationInfo).filter(SSLAuthenticationInfo.id == ssl_id).first()
                    logger.info("querying and getting records by using get_data_by_id for SSL auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "SSL_auth_info_id":auth_type_obj.SSL_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "ssl_info_id":ssl_obj.id,
                        "ssl_truststore_location":ssl_obj.ssl_truststore_location,
                        "ssl_truststore_password":ssl_obj.ssl_truststore_password,
                        "ssl_keystore_location":ssl_obj.ssl_keystore_location,
                        "ssl_keystore_password":ssl_obj.ssl_keystore_password,

                        "ssl_certificate_location": ssl_obj.ssl_certifivate_location,
                        "ssl_key_location": ssl_obj.ssl_key_location,

                        "ssl_key_password":ssl_obj.ssl_key_password,
                        "ssl_endpoint_identification_algorithm":ssl_obj.ssl_endpoint_identification_algorithm,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
                    
                elif auth_type_info_name == AuthTypeEnum.LDAP.value:
                    ldap_id = auth_type_obj.LDAP_auth_info_id
                    ldap_obj = db.query(LDAPAuthenticationInfo).filter(LDAPAuthenticationInfo.id == ldap_id).first()
                    logger.info("querying and getting records by using get_data_by_id for LDAP auth_type")
                    data = {
                        "id": auth_type_obj.id,
                        "LDAP_auth_info_id":auth_type_obj.LDAP_auth_info_id,
                        "auth_type":auth_type_obj.auth_type,
                        "fed_kafka_bus_name":auth_type_obj.fed_kafka_bus_name,
                        "ldap_info_id":ldap_obj.id,
                        "ldap_sasl_jaas_config":ldap_obj.ldap_sasl_jaas_config,
                        "ldap_sasl_mechanism":ldap_obj.ldap_sasl_mechanism,
                        "ldap_ssl_truststore_location":ldap_obj.ldap_ssl_truststore_location,
                        "ldap_ssl_truststore_password":ldap_obj.ldap_ssl_truststore_password,
                        "ldap_security_protocol":ldap_obj.ldap_security_protocol,
                        "ldap_url":ldap_obj.ldap_url,
                        "ldap_user":ldap_obj.ldap_user,
                        "ldap_password":ldap_obj.ldap_password,
                        "created_by":auth_type_obj.created_by,
                        "updated_by":auth_type_obj.updated_by,
                        "created_datetime":auth_type_obj.created_datetime,
                        "updated_datetime":auth_type_obj.updated_datetime
                    }
            else:
                return {"status_message":f"No record found with this combination auth_type:{auth_type_info_name} and fed_kafka_bus_name:{fed_kafka_bus_name_info}" }
            return data
                
        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("Data Base Connection Error", e)


    def get_all_auth_type_info(db: Session):
        try:
            logger.info("Querying and getting all records from all auth_type (get_all_auth_type_info) tables")
            auth_type_list = db.query(AuthType).all()
            auth_type_info_list = []
            for auth_type_data in auth_type_list:
                auth_type_info_dict = {
                    "id": auth_type_data.id,
                    "auth_type": auth_type_data.auth_type,
                    "fed_kafka_bus_name": auth_type_data.fed_kafka_bus_name,
                    "created_by": auth_type_data.created_by,
                    "updated_by": auth_type_data.updated_by,
                    "created_datetime": auth_type_data.created_datetime,
                    "updated_datetime": auth_type_data.updated_datetime,
                }
                if auth_type_data.plaintext_auth_info_id:
                    plaintext_auth_info = db.query(PlainTextAuthenticationInfo).all()
                    for plaintext_info in plaintext_auth_info:
                        plaintext_info_dict = {
                            "plaintext_auth_info_id": plaintext_info.id,
                            "plaintext_username": plaintext_info.plaintext_username,
                            "plaintext_password": plaintext_info.plaintext_password
                        }
                        auth_type_info_dict.update(plaintext_info_dict)
                    
                elif auth_type_data.OAuth_auth_info_id:
                    OAuth_auth_info_record = db.query(OAuthBearerAuthenticationInfo).all()
                    for oauth_auth_info in OAuth_auth_info_record:
                        oauth_info_dict = {
                            "OAuth_auth_info_id":oauth_auth_info.id,
                            "oauth_access_token": oauth_auth_info.oauth_access_token,
                            "oauth_token_type": oauth_auth_info.oauth_token_type,
                            "oauth_security_protocol": oauth_auth_info.oauth_security_protocol,
                            "oauth_security_mechanism": oauth_auth_info.oauth_security_mechanism,
                            "oauth_URL": oauth_auth_info.oauth_URL,
                            "oauth_client_id": oauth_auth_info.oauth_client_id,
                            "oauth_client_secret": oauth_auth_info.oauth_client_secret,
                            "oauth_expires_in": oauth_auth_info.oauth_expires_in,
                            "oauth_refresh_token": oauth_auth_info.oauth_refresh_token,
                            "oauth_token_id": oauth_auth_info.oauth_token_id,
                            "oauth_user_id": oauth_auth_info.oauth_user_id,
                            "oauth_authorization": oauth_auth_info.oauth_authorization,
                            "oauth_bearer": oauth_auth_info.oauth_bearer,
                            "oauth_scope": oauth_auth_info.oauth_scope,
                            "oauth_audience": oauth_auth_info.oauth_audience,
                            "oauth_issuer": oauth_auth_info.oauth_issuer,
                            "oauth_expiration": oauth_auth_info.oauth_expiration,
                            "oauth_claim": oauth_auth_info.oauth_claim,
                            "oauth_JWT": oauth_auth_info.oauth_JWT,
                            "oauth_refresh": oauth_auth_info.oauth_refresh,
                        }
                        auth_type_info_dict.update(oauth_info_dict)
                        
                elif auth_type_data.scram_auth_info_id:
                    scram_auth_info = db.query(ScramAuthenticationInfo).all()
                    for scram_auth in scram_auth_info:
                        scram_info_dict = {
                            "scram_auth_info_id": scram_auth.id,
                            "scram_salt": scram_auth.scram_salt,
                            "scram_iteration": scram_auth.scram_iteration,
                            "scram_nonce": scram_auth.scram_nonce,
                            "scram_channel_binding": scram_auth.scram_channel_binding,
                            "scram_hi": scram_auth.scram_hi,
                            "scram_hi_calculation": scram_auth.scram_hi_calculation,
                            "scram_client_key": scram_auth.scram_client_key,
                            "scram_server_Key": scram_auth.scram_server_Key,
                            "scram_stored_key": scram_auth.scram_stored_key,
                            "scram_proof": scram_auth.scram_proof,
                        }
                        auth_type_info_dict.update(scram_info_dict)
                        
                elif auth_type_data.keycloak_auth_info_id:
                    keycloak_auth_info = db.query(KeycloakAuthenticationInfo).all()
                    for keycloak_auth in keycloak_auth_info:
                        keycloak_info_dict = {
                            "keycloak_auth_info_id": keycloak_auth.id,
                            "keycloak_realm": keycloak_auth.keycloak_realm,
                            "keycloak_client": keycloak_auth.keycloak_client,
                            "keycloak_user": keycloak_auth.keycloak_user,
                            "keycloak_role": keycloak_auth.keycloak_role,
                            "keycloak_group": keycloak_auth.keycloak_group,
                            "keycloak_identity_provider": keycloak_auth.keycloak_identity_provider,
                            "keycloak_authenticator": keycloak_auth.keycloak_authenticator,
                            "keycloak_flow": keycloak_auth.keycloak_flow,
                            "keycloak_scope": keycloak_auth.keycloak_scope,
                            "keycloak_session": keycloak_auth.keycloak_session,
                        }
                        auth_type_info_dict.update(keycloak_info_dict)
                        
                elif auth_type_data.GSSAPI_auth_info_id:
                    gssapi_auth_info = db.query(GSSAPIAuthenticationInfo).all()
                    for gssapi_auth in gssapi_auth_info:
                        gssapi_info_dict = {
                            "GSSAPI_auth_info_id": gssapi_auth.id,
                            "GSSAPI_authentication_mechanism": gssapi_auth.GSSAPI_authentication_mechanism,
                            "GSSAPI_service_principal_name": gssapi_auth.GSSAPI_service_principal_name,
                            "GSSAPI_credentials": gssapi_auth.GSSAPI_credentials,
                            "GSSAPI_context": gssapi_auth.GSSAPI_context,
                            "GSSAPI_tokens": gssapi_auth.GSSAPI_tokens,
                            "GSSAPI_quality_of_protection": gssapi_auth.GSSAPI_quality_of_protection,
                            "GSSAPI_security_context_establishment": gssapi_auth.GSSAPI_security_context_establishment
                        }
                        auth_type_info_dict.update(gssapi_info_dict)
                        
                elif auth_type_data.kerberos_auth_info_id:
                    kerberos_auth_info = db.query(kerberosAuthenticationInfo).all()
                    for kerberos_auth in kerberos_auth_info:
                        kerberos_info_dict = {
                            "kerberos_auth_info_id": kerberos_auth.id,
                            "kerberos_authentication": kerberos_auth.kerberos_authentication,
                            "kerberos_tickets": kerberos_auth.kerberos_tickets,
                            "kerberos_KDC": kerberos_auth.kerberos_KDC,
                            "kerberos_principal": kerberos_auth.kerberos_principal,
                            "kerberos_realm": kerberos_auth.kerberos_realm,
                            "kerberos_service": kerberos_auth.kerberos_service,
                            "kerberos_keytab": kerberos_auth.kerberos_keytab,
                            "kerberos_TGT": kerberos_auth.kerberos_TGT,
                            "kerberos_SPN": kerberos_auth.kerberos_SPN,
                            "kerberos_GSSAPI": kerberos_auth.kerberos_GSSAPI
                        }
                        auth_type_info_dict.update(kerberos_info_dict)
                        
                elif auth_type_data.SASL_auth_info_id:
                    sasl_auth_info = db.query(SASLAuthenticationInfo).all()
                    for sasl_auth in sasl_auth_info:
                        sasl_info_dict = {
                            "SASL_auth_info_id": sasl_auth.id,
                            "sasl_authentication": sasl_auth.sasl_authentication,
                            "sasl_protocol": sasl_auth.sasl_protocol,
                            "sasl_mechanism": sasl_auth.sasl_mechanism,
                            "sasl_credential": sasl_auth.sasl_credential,
                            "sasl_service": sasl_auth.sasl_service,
                            "sasl_authorization": sasl_auth.sasl_authorization,
                            "sasl_channel_bindings": sasl_auth.sasl_channel_bindings,
                            "sasl_security": sasl_auth.sasl_security,
                            "sasl_identity": sasl_auth.sasl_identity,
                            "sasl_QOP": sasl_auth.sasl_QOP
                        }
                        auth_type_info_dict.update(sasl_info_dict)
                        
                elif auth_type_data.SSL_auth_info_id:
                    ssl_auth_info = db.query(SSLAuthenticationInfo).all()
                    for ssl_auth in ssl_auth_info:
                        ssl_info_dict = {
                            "SSL_auth_info_id": ssl_auth.id,
                            "ssl_truststore_location": ssl_auth.ssl_truststore_location,
                            "ssl_truststore_password": ssl_auth.ssl_truststore_password,
                            "ssl_keystore_location": ssl_auth.ssl_keystore_location,
                            "ssl_keystore_password": ssl_auth.ssl_keystore_password,

                            "ssl_certificate_location": ssl_auth.ssl_certifivate_location,
                            "ssl_key_location": ssl_auth.ssl_key_location,

                            "ssl_key_password": ssl_auth.ssl_key_password,
                            "ssl_endpoint_identification_algorithm": ssl_auth.ssl_endpoint_identification_algorithm
                        }
                        auth_type_info_dict.update(ssl_info_dict)
                        
                        
                elif auth_type_data.LDAP_auth_info_id:
                    ldap_auth_info = db.query(LDAPAuthenticationInfo).all()
                    for ldap_auth in ldap_auth_info:
                        ldap_info_dict = {
                            "LDAP_auth_info_id": ldap_auth.id,
                            "ldap_sasl_jaas_config": ldap_auth.ldap_sasl_jaas_config,
                            "ldap_sasl_mechanism": ldap_auth.ldap_sasl_mechanism,
                            "ldap_ssl_truststore_location": ldap_auth.ldap_ssl_truststore_location,
                            "ldap_ssl_truststore_password": ldap_auth.ldap_ssl_truststore_password,
                            "ldap_security_protocol": ldap_auth.ldap_security_protocol,
                            "ldap_url": ldap_auth.ldap_url,
                            "ldap_user": ldap_auth.ldap_user,
                            "ldap_password": ldap_auth.ldap_password
                        }
                        auth_type_info_dict.update(ldap_info_dict)
                        
                auth_type_info_list.append(auth_type_info_dict)
                
            return auth_type_info_list
        
        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("Data Base Connection Error", e)

           
           
    def delete_auth_type_data_by_id(db: Session, auth_type_id: int):
        try:
            logger.info("Querying and deleting the auth_type table by using id")
            entry = db.query(AuthType).filter(AuthType.id == auth_type_id).first()
            db.delete(entry)
            db.commit()
            
        except exc.SQLAlchemyError as e:
            
            logger.debug(e)
            raise Exception("DataBase Connection Error", e)

