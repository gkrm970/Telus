#from sys import exception
from sqlalchemy.orm import Session
from sqlalchemy import exc
from app.models.models import FedKafkaBuses,SchemaRegistry
from app.api.deps import get_db
from fastapi import Depends, HTTPException
from app.schemas.entity import Bus as FedKafkaSchema


from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger


API_NAME = "Crud FedKafkaBus"

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

class CRUDDevice:
    def create(db: Session, obj_in: FedKafkaSchema):
       
        dict_data = obj_in.__dict__

        try:
            logger.info("Strted-Inserting-Schema-Registry-Record")

            if dict_data["schema_registry_host"] and dict_data["schema_registry_port"] \
                and dict_data["schema_registry_version"]:


                schema_obj = SchemaRegistry(
                    schema_registry_host = dict_data["schema_registry_host"],
                    schema_registry_port = dict_data["schema_registry_port"],
                    schema_registry_version = dict_data["schema_registry_version"],
                    schema_auth_type = dict_data.get("schema_registry_auth_type"),
                    created_by = dict_data["created_by"],
                    updated_by = dict_data["updated_by"]  
                )
                db.add(schema_obj)
                db.commit()
                logger.info("Inserted-Schema-Registry-Record")
                db.refresh(schema_obj)

                logger.info("Strted-Inserting-Fed-Kafka-Bus-Record")

                fed_kafka_obj = FedKafkaBuses(
                    schema_registry_id = schema_obj.id,
                    instance_type = dict_data["instance_type"],
                    kafka_host = dict_data["kafka_host"],
                    kafka_port = dict_data["kafka_port"],
                    kafka_version = dict_data["kafka_version"],
                    kafka_auth_type = dict_data.get("kafka_auth_type"),
                    created_by = dict_data["created_by"],
                    updated_by = dict_data["updated_by"]
                )


                db.add(fed_kafka_obj)
                db.commit()
                db.refresh(fed_kafka_obj)

                logger.info("Inserted-Fed-Kafka-Bus-Record")

                
            else:
                logger.info("No-Schema-Registry-Record")

                logger.info("Strted-Inserting-Fed-Kafka-Bus-Record")
                fed_kafka_obj = FedKafkaBuses(

                    # auth_type_id = auth.id,
                    instance_type = dict_data["instance_type"],
                    kafka_host = dict_data["kafka_host"],
                    kafka_port = dict_data["kafka_port"],
                    kafka_version = dict_data["kafka_version"],
                    kafka_auth_type = dict_data.get("kafka_auth_type"),
                    created_by = dict_data["created_by"],
                    updated_by = dict_data["updated_by"]
                )

                db.add(fed_kafka_obj)
                db.commit()
                db.refresh(fed_kafka_obj)
                logger.info("Inserted-Fed-Kafka-Bus-Record")
        
        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("Data Base Connection Error", e)


    def update_fed_kafka_info(db: Session,fed_kafka_info_id: int, fed_kafka_info: str):
            
            fed_kafka_info_model = db.query(FedKafkaBuses).filter(FedKafkaBuses.id == fed_kafka_info_id).first()
            schema_register = db.query(SchemaRegistry).filter(SchemaRegistry.id == fed_kafka_info_id).first()


            dict_data = fed_kafka_info.__dict__

            
            if fed_kafka_info_model is None:
                raise HTTPException(status_code=404, detail="Record not found")


            try:
                logger.info("Strted-Inserting-Schema-Registry-Record")
                if dict_data["schema_registry_host"] and dict_data["schema_registry_port"] \
                and dict_data["schema_registry_version"]:

                    schema_registry_object = db.query(SchemaRegistry).filter(
                        SchemaRegistry.schema_registry_host == dict_data['schema_registry_host'],
                        SchemaRegistry.schema_registry_port == dict_data['schema_registry_port'],
                        SchemaRegistry.schema_auth_type == dict_data.get("schema_registry_auth_type"),
                        SchemaRegistry.schema_registry_version == dict_data['schema_registry_version']
                        ).first()

                    if schema_registry_object is not None:
                        fed_kafka_info_model.schema_registry_id = schema_registry_object.id
                        fed_kafka_info_model.instance_type = dict_data["instance_type"]
                        fed_kafka_info_model.kafka_host = dict_data["kafka_host"]
                        fed_kafka_info_model.kafka_port = dict_data["kafka_port"]
                        fed_kafka_info_model.kafka_version = dict_data["kafka_version"]
                        fed_kafka_info_model.kafka_auth_type = dict_data.get("kafka_auth_type")
                        fed_kafka_info_model.created_by = dict_data["created_by"]
                        fed_kafka_info_model.updated_by = dict_data["updated_by"]
                        db.add(fed_kafka_info_model)
                        db.commit()
                    elif schema_registry_object is None:
                        schema_register = SchemaRegistry()
                        schema_register.schema_registry_host = dict_data["schema_registry_host"]
                        schema_register.schema_registry_port = dict_data["schema_registry_port"]
                        schema_register.schema_auth_type = dict_data.get("schema_registry_auth_type")
                        schema_register.schema_registry_version = dict_data["schema_registry_version"]
                        schema_register.created_by = dict_data["created_by"]
                        schema_register.updated_by = dict_data["updated_by"]

                    # schema_id = schema_obj.id
                        db.add(schema_register)
                        db.commit()
                        logger.info("Inserted-Schema-Registry-Record")
                        db.refresh(schema_register)

                        logger.info("Strted-Updating-Fed-Kafka-Bus-Record")

                        fed_kafka_info_model.schema_registry_id = schema_register.id
                        fed_kafka_info_model.instance_type = dict_data["instance_type"]
                        fed_kafka_info_model.kafka_host = dict_data["kafka_host"]
                        fed_kafka_info_model.kafka_port = dict_data["kafka_port"]
                        fed_kafka_info_model.kafka_version = dict_data["kafka_version"]
                        fed_kafka_info_model.kafka_auth_type = dict_data.get("kafka_auth_type")
                        fed_kafka_info_model.created_by = dict_data["created_by"]
                        fed_kafka_info_model.updated_by = dict_data["updated_by"]

                        db.add(fed_kafka_info_model)
                        db.commit()
                        db.refresh(fed_kafka_info_model)
                        logger.info("Inserted-Fed-Kafka-Bus-Record")
                else:
                    logger.info("No-Schema-Registry-Record")

                    logger.info("Strted-Inserting-Fed-Kafka-Bus-Record")

                    fed_kafka_info_model.instance_type = dict_data["instance_type"]
                    fed_kafka_info_model.kafka_host = dict_data["kafka_host"]
                    fed_kafka_info_model.kafka_port = dict_data["kafka_port"]
                    fed_kafka_info_model.kafka_version = dict_data["kafka_version"]
                    fed_kafka_info_model.kafka_auth_type = dict_data.get("kafka_auth_type")
                    fed_kafka_info_model.created_by = dict_data["created_by"]
                    fed_kafka_info_model.updated_by = dict_data["updated_by"]
                
                    db.add(fed_kafka_info_model)
                    db.commit()
                    db.refresh(fed_kafka_info_model)
                    logger.info("Inserted-Fed-Kafka-Bus-Record")
        
            except exc.SQLAlchemyError as e:
                logger.debug(e)
                raise Exception("Data Base Connection Error", e)
             # end update

    def get_all_fed_kafka_info(db: Session):
        try:
            fed_kafka_list = db.query(FedKafkaBuses).all()
            schema_registry_list = db.query(SchemaRegistry).all()
            kafka_info_list = []
            
            for schema_regisrty in schema_registry_list:
                pass
            
            for fed_kafka in fed_kafka_list:
                if fed_kafka.schema_registry_id:
                    kafka_info_dict = {
                        "kafka_bus_id": fed_kafka.id,
                        "schema_registry_id": fed_kafka.schema_registry_id,
                        "kafka_host": fed_kafka.kafka_host,
                        "kafka_port": fed_kafka.kafka_port,
                        "instance_type":fed_kafka.instance_type,
                        "kafka_version": fed_kafka.kafka_version,
                        "kafka_auth_type":fed_kafka.kafka_auth_type,
                        "created_by":fed_kafka.created_by,
                        "updated_by":fed_kafka.updated_by,
                        "created_datetime":fed_kafka.created_datetime,
                        "updated_datetime":fed_kafka.updated_datetime,
                        "schemaregistry_id":schema_regisrty.id,
                        "schema_registry_host":schema_regisrty.schema_registry_host,
                        "schema_registry_port":schema_regisrty.schema_registry_port,
                        "schema_registry_version":schema_regisrty.schema_registry_version,
                        "schema_registry_auth_type": schema_regisrty.schema_auth_type,
                        "created_by":schema_regisrty.created_by,
                        "updated_by":schema_regisrty.updated_by,
                        "created_datetime":schema_regisrty.created_datetime,
                        "updated_datetime":schema_regisrty.updated_datetime,
                    }   
                else:
                    kafka_info_dict = {
                        "kafka_bus_id": fed_kafka.id,
                        "schema_registry_id": fed_kafka.schema_registry_id,
                        "kafka_host": fed_kafka.kafka_host,
                        "kafka_port": fed_kafka.kafka_port,
                        "instance_type":fed_kafka.instance_type,
                        "kafka_version": fed_kafka.kafka_version,
                        "kafka_auth_type":fed_kafka.kafka_auth_type,
                        "created_by":fed_kafka.created_by,
                        "updated_by":fed_kafka.updated_by,
                        "created_datetime":fed_kafka.created_datetime,
                        "updated_datetime":fed_kafka.updated_datetime
                    }

                kafka_info_list.append(kafka_info_dict)

            return kafka_info_list

        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("Data Base Connection Error", e)

    def get_data_by_id(db: Session,kafka_bus_info_id: int):
        try:
            # return db.query(FedKafkaBuses).filter(FedKafkaBuses.id == kafka_bus_info_id).first()
            fed_kafka_obj = db.query(FedKafkaBuses).filter(FedKafkaBuses.id == kafka_bus_info_id).first()
            schema_registry_obj = db.query(SchemaRegistry).filter(SchemaRegistry.id == fed_kafka_obj.schema_registry_id).first()
            if schema_registry_obj:
                fed_kafka_details = {
                    "fed_kafka_id": fed_kafka_obj.id,
                    "schema_registry_id":fed_kafka_obj.schema_registry_id,
                    "instance_type":fed_kafka_obj.instance_type,
                    "kafka_host":fed_kafka_obj.kafka_host,
                    "kafka_port":fed_kafka_obj.kafka_port,
                    "kafka_version":fed_kafka_obj.kafka_version,
                    "kafka_auth_type":fed_kafka_obj.kafka_auth_type,
                    "created_by":fed_kafka_obj.created_by,
                    "updated_by":fed_kafka_obj.updated_by,
                    "created_datetime":fed_kafka_obj.created_datetime,
                    "updated_datetime":fed_kafka_obj.updated_datetime,
                    "schemaregistry_id":schema_registry_obj.id,
                    "schema_registry_host":schema_registry_obj.schema_registry_host,
                    "schema_registry_port":schema_registry_obj.schema_registry_port,
                    "schema_registry_version":schema_registry_obj.schema_registry_version,
                    "schema_auth_type":schema_registry_obj.schema_auth_type,
                    "created_by":schema_registry_obj.created_by,
                    "updated_by":schema_registry_obj.updated_by,
                    "created_datetime":schema_registry_obj.created_datetime,
                    "updated_datetime":schema_registry_obj.updated_datetime,
                }
            else:
                fed_kafka_details = {
                    "fed_kafka_id": fed_kafka_obj.id,
                    "schema_registry_id":fed_kafka_obj.schema_registry_id,
                    "instance_type":fed_kafka_obj.instance_type,
                    "kafka_host":fed_kafka_obj.kafka_host,
                    "kafka_port":fed_kafka_obj.kafka_port,
                    "kafka_version":fed_kafka_obj.kafka_version,
                    "kafka_auth_type":fed_kafka_obj.kafka_auth_type,
                    "created_by":fed_kafka_obj.created_by,
                    "updated_by":fed_kafka_obj.updated_by,
                    "created_datetime":fed_kafka_obj.created_datetime,
                    "updated_datetime":fed_kafka_obj.updated_datetime,
                }

            return fed_kafka_details
            

        except exc.SQLAlchemyError as e:
            logger.debug(e)
            raise Exception("Data Base Connection Error", e)


def delete_data_by_id(db: Session, kafka_bus_info_id: int):
    try:
        fed_kafka_obj = db.query(FedKafkaBuses).filter(FedKafkaBuses.id == kafka_bus_info_id).first()
        if fed_kafka_obj is not None:
            kafka_bus_sechma = db.query(SchemaRegistry).filter(
                SchemaRegistry.id == fed_kafka_obj.schema_registry_id).first()
            if kafka_bus_sechma and fed_kafka_obj is not None:
                db.delete(kafka_bus_sechma)
                db.delete(fed_kafka_obj)
                db.commit()
                db.flush()
                res = {"response": "Record_Deleted Successfully", "status_code": 200}
            elif fed_kafka_obj is not None:
                db.delete(fed_kafka_obj)
                db.commit()
                db.flush()
                res = {"response": "Record_Deleted Successfully", "status_code": 200}
        else:
            res = {"status_code": 401,
                   "Request_Id": kafka_bus_info_id,
                   "status_message": "Request id is not present in DB, Try with valid one"}
        return res
    except exc.SQLAlchemyError as e:
        logger.debug(e)
        raise Exception("Data Base Connection Error", e)
