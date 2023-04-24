import logging
import os

from utils import cron_scheduler_config as config
from utils.logger import LoggerHandler
from utils.utils import schedular_frequency_value, do_auth
from utils.blocking_scheduler import SchedulerJob

logger = logging.getLogger('discovery-service-plugin')


def main():
    log_level = config.Config.LOG_LEVEL
    LoggerHandler('discovery-service-plugin', log_level).setup_logger()
    logger.info('************** Blocking Scheduler - Discovery Plugin service ******************')
    logger.info('Fetching access token to use authentication')
    access_token = do_auth()

    env = os.getenv('ENV', 'local')

    if env == 'local':
        logger.info('Starting scheduler using local configuration')
        local_config = config.LocalConfig()
        SchedulerJob(local_config).blockingscheduler(schedular_frequency_value, access_token)
    elif env == 'development':
        logger.info('Starting scheduler using development configuration')
        dev_config = config.DevelopmentConfig()
        SchedulerJob(dev_config).blockingscheduler(schedular_frequency_value, access_token)
    elif env == 'staging':
        logger.info('Starting scheduler using staging configuration')
        staging_config = config.StagingConfig()
        SchedulerJob(staging_config).blockingscheduler(schedular_frequency_value, access_token)
    elif env == 'production':
        logger.info('Starting scheduler using production configuration')
        prod_config = config.ProductionConfig()
        SchedulerJob(prod_config).blockingscheduler(schedular_frequency_value, access_token)
    elif env == 'testing':
        logger.info('Starting scheduler using test configuration')
        test_config = config.TestingConfig()
        SchedulerJob(test_config).blockingscheduler(schedular_frequency_value, access_token)
    else:
        logger.error('Invalid environment is provided')


if __name__ == '__main__':
    main()

