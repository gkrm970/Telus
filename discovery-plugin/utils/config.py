import os

class Config:
    DEBUG = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

    THREAD_POOL_EXECUTORS = os.getenv('THREAD_POOL_EXECUTORS', 10)
    PROCESS_POOL_EXECUTORS = os.getenv('PROCESS_POOL_EXECUTORS', 5)
    JOB_DEFAULT_INSTANCES = os.getenv('JOB_DEFAULT_INSTANCES', 10)
    # Trigger Types - date, interval, cron
    TRIGGER_TYPE = os.getenv('TRIGGER_TYPE', 'interval')
