import json
import os
import requests
import re
import logging
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from service.discovery_plugin_service import discovery_service
from tinaa.utils.v1.auth_handler import AuthHandler, AuthenticationException

logger = logging.getLogger('utility-logger')
BUS_FREQ_REFERENCE = dict()
BUS_FREQ_MAIN = []


def do_auth() -> str:
    logger.info('inside do auth')
    AUTH_TOKEN_URL = os.getenv('AUTH_TOKEN_URL', 'http://dummy/token')
    CLIENT_ID = os.getenv('CLIENT_ID', 'test')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'test')
    #AUTH_TOKEN_URL = "https://auth.ocp01.toll6.tinaa.tlabs.ca/auth/realms/tinaa/protocol/openid-connect/token"
   
    config = {'oauth2': {'oauth2_client_id': CLIENT_ID, 'oauth2_client_secret': CLIENT_SECRET, 'oauth2_token_url': AUTH_TOKEN_URL}}
    logger.info(f'config obj is: {config["oauth2"]}')

    logger.debug(f'Auth config to get token is : {AUTH_TOKEN_URL}, {CLIENT_ID}, {CLIENT_SECRET}')
    auth = AuthHandler(config['oauth2'], logger)
    token = auth.get_access_token()
    logger.info(f'token is : {token}')

    return token

def bgscheduler(service_url, trigger_type, bus_id_frequency_lst, access_token):
    global BUS_FREQ_REFERENCE    
    global BUS_FREQ_MAIN    
    logger.info(f"******* scheduler logs start **********")
    for data in bus_id_frequency_lst:
        scheduler = BackgroundScheduler(timezone=utc)
        for interval_time, job_ids in data.items():
            job_ids = eval(job_ids)
            if BUS_FREQ_REFERENCE.get(interval_time) and BUS_FREQ_REFERENCE.get(interval_time) == job_ids:
                logger.info(f"Scheduler already running for Job ids - {job_ids}, hence skipping...")
                continue            
            elif BUS_FREQ_REFERENCE.get(interval_time) and BUS_FREQ_REFERENCE.get(interval_time) != job_ids:
                job_ids_before = BUS_FREQ_REFERENCE.get(interval_time)
                job_ids = list(set(job_ids).difference(set(job_ids_before)))
                if not job_ids:
                    continue
                logger.info(f"Scheduler already running for Job ids - {job_ids_before}, scheduling only for id's: {job_ids}")
            else :
                logger.info(f"Starting scheduler for job id's : {job_ids}")
            scheduler.add_job(
                discovery_service,
                args=[service_url, job_ids, access_token],
                trigger=trigger_type,
                seconds=interval_time,
            )
            scheduler.start()
            logger.info(
                f"Instance for the job_id's - {job_ids} at interval - {interval_time} has been scheduled")
            BUS_FREQ_MAIN.append({interval_time: job_ids})
            if BUS_FREQ_REFERENCE.get(interval_time):
                BUS_FREQ_REFERENCE[interval_time] = (BUS_FREQ_REFERENCE.get(interval_time) + job_ids)
                #print("if********", BUS_FREQ_REFERENCE)
            else:
                BUS_FREQ_REFERENCE[interval_time] = job_ids
    #print("BUS_FREQ_MAIN", BUS_FREQ_MAIN) 
      
    logger.info(f"******* scheduler logs end **********") 
    return BUS_FREQ_MAIN

def get_all_schedular(service_url, access_token):
    try:
        url=f'{service_url}scheduler/get_active_schedulers'
        headers = {'accept': 'application/json',
                   'Authorization': 'Bearer {}'.format(access_token)}
        response = requests.get(url, headers=headers)
        logger.info(f'response from schedulers are: {response.json()}')
        return response.json()
    except Exception as e:
        return str(e)


def schedular_frequency_value(service_url, trigger_type, access_token):
    try:
        #logger.info(f'Fetching all active schedulers using access token - {access_token}')
        all_schedular_resp = get_all_schedular(service_url, access_token)
        logger.info(f'Current active schedulers response is : {all_schedular_resp["response"]}')

        if all_schedular_resp['status']==200 and all_schedular_resp['response']:
            bus_id_frequency_lst = []
            for row in all_schedular_resp['response']:
                bus_id_frequency = {}
                if row['schedular_status'] == 'Active':
                    s = re.split(r'[^a-z]', row['frequency'])
                    hr = s[-1].startswith("h")
                    min = s[-1].startswith("m")
                    sec = s[-1].startswith("s")
                    if hr:
                        interval_obj = row['frequency'].split("h")[0]
                        seconds_value = int(interval_obj) * 60 * 60
                        bus_id_frequency[seconds_value] = row['fed_kafka_bus_id']
                    elif min:
                        interval_obj = row['frequency'].split("m")[0]
                        seconds_value = int(interval_obj) * 60
                        bus_id_frequency[seconds_value] = row['fed_kafka_bus_id']
                    elif sec:
                        interval_obj = row['frequency'].split("s")[0]
                        seconds_value=int(interval_obj)
                        bus_id_frequency[seconds_value] = row['fed_kafka_bus_id']
                        bus_id_frequency_lst.append(bus_id_frequency)

                    else:
                        raise ValueError(row['frequency']+" "+ "frequency value not contained in minutes or hours or seconds format")
            logger.info(f'Overall schedulers frequency to kafka bus id\'s mapping is : {bus_id_frequency_lst}')
            bgscheduler(service_url, trigger_type, bus_id_frequency_lst, access_token)
        else:
            logger.info(f'No schedulers have been configured...')
    except Exception as e:
        print("error occured in ",str(e))

