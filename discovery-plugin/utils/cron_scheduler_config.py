import os
import sys
import requests
import re

from utils.config import Config as BaseConfig
from utils.logger import LoggerHandler


class Config(BaseConfig):

    SERVICE_PROTOCOL = os.getenv('SERVICE_PROTOCOL', 'http')
    SERVICE_HOST = os.getenv('SERVICE_HOST', '10.17.36.156')
    SERVICE_PORT = os.getenv('SERVICE_PORT', '8088')
    SERVICE_ENDPOINT = os.getenv(
        'SERVICE_ENDPOINT', '/pubsub/v1/')
    service_url = SERVICE_PROTOCOL+"://"+SERVICE_HOST+":"+SERVICE_PORT+SERVICE_ENDPOINT
    INTERVAL_TIME = os.getenv('INTERVAL_TIME', 10)
    AUTH_TOKEN_URL = os.getenv('AUTH_TOKEN_URL', 'http://dummy/token')
    CLIENT_ID = os.getenv('CLIENT_ID', 'test')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', 'test')


# Configuration for different environments
class ProductionConfig(Config):
    """Configuration for production."""
    ENV = 'production'


class StagingConfig(Config):
    """Configuration for staging."""
    ENV = 'staging'


class TestingConfig(Config):
    """Configuration for testing."""
    ENV = 'testing'
    DEBUG = True


class DevelopmentConfig(Config):
    """Configuration for development."""
    ENV = 'development'
    DEBUG = True


class LocalConfig(Config):
    """Configuration for development."""
    ENV = 'local'
    DEBUG = True
