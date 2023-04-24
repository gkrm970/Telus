import logging


class LoggerHandler:

    def __init__(self, logger_instance='root', level='Info', line_buf=None):
        self.logger_instance = logger_instance
        self.level = level
        self.line_buf = line_buf
        self.logger = None

    def setup_logger(self):

        log_level = self.level
        numeric_log_level = getattr(logging, log_level.upper(), None)

        # Logger Formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] [PID:%(process)d TID:%(thread)d] %(message)s')

        # Initialize Default Logger
        self.logger = logging.getLogger(self.logger_instance)
        self.logger.setLevel(numeric_log_level)

        # Initialize StreamHandler
        ch = logging.StreamHandler()
        ch.setLevel(numeric_log_level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # Initialize wrapper logger
        logger = logging.getLogger('discovery-service-plugin')
        logger.setLevel(numeric_log_level)
        logger.addHandler(ch)

        # Initialize blocking scheduler logger
        logger = logging.getLogger('scheduler-instance')
        logger.setLevel(numeric_log_level)
        logger.addHandler(ch)

        # Initialize blocking scheduler logger
        logger = logging.getLogger('utility-logger')
        logger.setLevel(numeric_log_level)
        logger.addHandler(ch)

        # Initialize blocking scheduler logger
        logger = logging.getLogger('bg-scheduler-instance')
        logger.setLevel(numeric_log_level)
        logger.addHandler(ch)
