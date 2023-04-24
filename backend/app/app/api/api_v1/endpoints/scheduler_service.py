import json
import ast
import logging
from app.database.session import engine
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from app.schemas.entity import DiscoveryModuleInternalDiscoveryScheduler as SchedulerPydentic
from app.api.deps import get_db, get_current_user
from app.schemas.token import TokenPayload
from app.core.config import settings
from starlette.responses import JSONResponse
from tinaa.logger.v1.tinaa_logger import get_app_logger

API_NAME = "Scheduler Api"
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
# from typing import List

router = APIRouter()

from app.models.models import SchedularModel


@router.post('/scheduler/create_scheduler')
async def create_scheduler(info: SchedulerPydentic, db: Session = Depends(get_db),
                           current_user: TokenPayload = Depends(get_current_user)):
    try:
        dict_data = info.__dict__
        all_schedular = db.query(SchedularModel).filter(SchedularModel.schedular_status == 'Active')
        fed_kafkabus_ids = []
        kafka_bus_id = []
        existed_bus_ids = []

        payload_fedkafkabus_id = dict_data["fed_kafka_bus_id"]
        logger.info(f'Bus id list from payload is : {payload_fedkafkabus_id}')

        normal_list = eval(payload_fedkafkabus_id)
        for bus_id in all_schedular:
            fed_kafkabus_ids.append(bus_id.fed_kafka_bus_id)
        logger.info(f'Bus id list from DB is: {fed_kafkabus_ids}')

        new_lst = [ast.literal_eval(i) for i in fed_kafkabus_ids]

        all_fed_kafkabus_ids = [item for sublist_id in new_lst for item in sublist_id]
        logger.info(f'Falttened DB list: {all_fed_kafkabus_ids}')

        for bus_id in normal_list:
            if bus_id in all_fed_kafkabus_ids:
                existed_bus_ids.append(bus_id)
                res = {
                    "status_code": 201,
                    "status_message": f"Scheduler already existed for bus id's: {existed_bus_ids}"
                }

            else:
                data = [kafka_bus_id.append(b_id) for b_id in normal_list if b_id not in all_fed_kafkabus_ids]
                bus_id = json.dumps(kafka_bus_id)
                logger.info(f'kafka_bus_id: {bus_id}')
                fed_kafka_scheduler_model = SchedularModel()
                fed_kafka_scheduler_model.schedular_status = info.schedular_status
                fed_kafka_scheduler_model.fed_kafka_bus_id = bus_id
                fed_kafka_scheduler_model.frequency = info.frequency
                fed_kafka_scheduler_model.created_by = info.created_by
                fed_kafka_scheduler_model.updated_by = info.updated_by

                db.add(fed_kafka_scheduler_model)
                db.commit()
                if existed_bus_ids:
                    status_message = f'Scheduler already existed for bus ids: {existed_bus_ids}, New scheduler created only for these: {bus_id}'
                else:
                    status_message = f'New scheduler created only for bus ids: {bus_id}'
                res = {
                    "status_code": 201,
                    "status_message": status_message
                }
                return res
        return res
    except:
        return "Provide valid payload "


@router.get('/scheduler/all_schedulers')
async def get_all_scheduler(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        all_schedular = db.query(SchedularModel).all()
        all_column = []
        for values in all_schedular:
            fed_kafka_scheduler_dict = {"id": values.id,
                                        "fed_kafka_bus_id": values.fed_kafka_bus_id,
                                        "schedular_status": values.schedular_status,
                                        "frequency": values.frequency,
                                        "created_by": values.created_by,
                                        "updated_by": values.updated_by
                                        }
            all_column.append(fed_kafka_scheduler_dict)

        return {'response': all_column, 'status': status.HTTP_200_OK}

    except:
        return "No scheduler record found "


@router.get("/scheduler/get_by_id/{scheduler_id}")
async def get_scheduler_by_id(scheduler_id: int, db: Session = Depends(get_db),
                              current_user: TokenPayload = Depends(get_current_user)):
    try:
        scheduler_object = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id).first()

        fed_kafka_scheduler_dict = {
            "id": scheduler_object.id,
            "fed_kafka_bus_id": scheduler_object.fed_kafka_bus_id,
            "schedular_status": scheduler_object.schedular_status,
            "frequency": scheduler_object.frequency,
            "created_by": scheduler_object.created_by,
            "updated_by": scheduler_object.updated_by
        }

        return fed_kafka_scheduler_dict, status.HTTP_200_OK
    except:
        return "Provide valid scheduler_id"


@router.get("/scheduler/get_active_schedulers", status_code=200)
async def get_active_schedulers(db: Session = Depends(get_db), current_user: TokenPayload = Depends(get_current_user)):
    try:
        Active_schedulers = db.query(SchedularModel).filter(SchedularModel.schedular_status == 'Active')

        response_list = []
        for fed_kafka_scheduler_model in Active_schedulers:
            fed_kafka_scheduler_dict = {
                "id": fed_kafka_scheduler_model.id,
                "fed_kafka_bus_id": fed_kafka_scheduler_model.fed_kafka_bus_id,
                "schedular_status": fed_kafka_scheduler_model.schedular_status,
                "frequency": fed_kafka_scheduler_model.frequency,
                "created_by": fed_kafka_scheduler_model.created_by,
                "updated_by": fed_kafka_scheduler_model.updated_by
            }
            response_list.append(fed_kafka_scheduler_dict)
        return {"response": response_list, "status": status.HTTP_200_OK}
    except:
        return "No active scheduler record found"


@router.get("/scheduler/get_inactive_schedulers", status_code=200)
async def get_inactive_schedulers(db: Session = Depends(get_db),
                                  current_user: TokenPayload = Depends(get_current_user)):
    try:
        Inctive_schedulers = db.query(SchedularModel).filter(SchedularModel.schedular_status == 'Inactive')
        logger.info(f'Inctive_schedulers:{Inctive_schedulers}')
        response_dict = {}
        response_list = []
        for fed_kafka_scheduler_model in Inctive_schedulers:
            fed_kafka_scheduler_dict = {
                "id": fed_kafka_scheduler_model.id,
                "schedular_status": fed_kafka_scheduler_model.schedular_status,
                "frequency": fed_kafka_scheduler_model.frequency,
                "created_by": fed_kafka_scheduler_model.created_by,
                "updated_by": fed_kafka_scheduler_model.updated_by
            }
            response_list.append(fed_kafka_scheduler_dict)
        response_dict['Inactive_schedulers records'] = response_list
        logger.info(f'response_dict: {response_dict}')
        return response_dict, status.HTTP_200_OK
    except:
        return "No Inactive scheduler record found"


@router.put('/scheduler/get_activate_scheduler_by_id/{scheduler_id}')
async def activate_scheduler(scheduler_id: str, db: Session = Depends(get_db),
                             current_user: TokenPayload = Depends(get_current_user)):
    try:
        fed_kafka_scheduler_model = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id,
                                                                    SchedularModel.schedular_status == "Inactive").first()
        if fed_kafka_scheduler_model is None:
            raise HTTPException

        fed_kafka_scheduler_model.schedular_status = "Active"

        db.add(fed_kafka_scheduler_model)
        db.commit()

        scheduler_object = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id).first()

        fed_kafka_scheduler_dict = {
            "id": scheduler_object.id,
            "schedular_status": scheduler_object.schedular_status,
            "frequency": scheduler_object.frequency,
            "created_by": scheduler_object.created_by,
            "updated_by": scheduler_object.updated_by
        }

        return "Scheduler activated", status.HTTP_200_OK, fed_kafka_scheduler_dict
    except:
        return " Provide valid scheduler_id"


@router.put('/scheduler/deactivate_scheduler/{scheduler_id}')
async def deactivate_scheduler(scheduler_id: str, db: Session = Depends(get_db),
                               current_user: TokenPayload = Depends(get_current_user)):
    try:
        fed_kafka_scheduler_model = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id,
                                                                    SchedularModel.schedular_status == "Active").first()
        if fed_kafka_scheduler_model is None:
            raise HTTPException

        fed_kafka_scheduler_model.schedular_status = "Inactive"

        db.add(fed_kafka_scheduler_model)
        db.commit()

        scheduler_object = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id).first()

        fed_kafka_scheduler_dict = {
            "id": scheduler_object.id,
            "schedular_status": scheduler_object.schedular_status,
            "frequency": scheduler_object.frequency,
            "created_by": scheduler_object.created_by,
            "updated_by": scheduler_object.updated_by
        }

        return "Scheduler deactivated", status.HTTP_200_OK, fed_kafka_scheduler_dict

    except:
        "Provide valid schedulers_id"


@router.delete('/scheduler/{scheduler_id}')
async def delete_scheduler_by_id(scheduler_id: int, db: Session = Depends(get_db),
                                 current_user: TokenPayload = Depends(get_current_user)):
    try:
        scheduler_object = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id).first()

        fed_kafka_scheduler_dict = {
            "id": scheduler_object.id,
            "schedular_status": scheduler_object.schedular_status,
            "frequency": scheduler_object.frequency,
            "created_by": scheduler_object.created_by,
            "updated_by": scheduler_object.updated_by
        }

        fed_kafka_scheduler_model = db.query(SchedularModel).filter(SchedularModel.id == scheduler_id).delete()

        if fed_kafka_scheduler_model is None:
            raise HTTPException
        db.commit()

        return {"Message": "Scheduler Deleted Successfully", "is ": fed_kafka_scheduler_dict,
                "status": status.HTTP_204_NO_CONTENT}
    except:
        return "No schedulers record found "


@router.delete('/scheduler/delete_all_inactive_schedulers')
async def delete_inactive_schedulers(db: Session = Depends(get_db),
                                     current_user: TokenPayload = Depends(get_current_user)):
    try:
        fed_kafka_scheduler_model = db.query(SchedularModel).filter(
            SchedularModel.schedular_status == 'Inactive').delete()

        if fed_kafka_scheduler_model is None:
            raise HTTPException
        db.commit()

        return {"Message": "Deleted all inactive schedulers.", "status": status.HTTP_204_NO_CONTENT}
    except:
        return "No Inactive schedulers record found "
