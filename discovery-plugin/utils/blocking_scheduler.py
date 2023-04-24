import logging
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import utc

logger = logging.getLogger('scheduler-instance')


class SchedulerJob:
    def __init__(self, config):
        self.config = config
        self.scheduler = BlockingScheduler(timezone=utc)
        self.trigger_type = self.config.TRIGGER_TYPE
        self.interval_time = self.config.INTERVAL_TIME
        self.service_url = self.config.service_url

    def blockingscheduler(self, job_fn, access_token):
        logger.info('Inside blocking scheduler...')
        logger.info(f'service url is : {self.service_url}')
        self.scheduler.add_job(job_fn, args = [self.service_url, self.trigger_type, access_token], trigger=self.trigger_type,
                            seconds=self.interval_time)
        self.scheduler.start()

