from tinaa.logger.v1.tinaa_logger import get_app_logger

from app.core.config import settings
from tinaa.logger.v1.tinaa_logger import get_app_logger

logger_conf = [
    {
        "handler_name": settings.LOGGER_HANDLER_NAME,
        "log_level": settings.TINAA_LOG_LEVEL,
        "log_format": settings.LOGGER_FORMAT,
        "date_format": settings.LOGGER_DATE_FORMAT,
        "app_code": settings.LOGGER_APP_CODE,
        "app_name": settings.LOGGER_APP_NAME,
    }
]
logger = get_app_logger(log_conf=logger_conf, logger_name=settings.LOGGER_APP_NAME)




def init() -> None:

    return


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
