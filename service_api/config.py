# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""

import logging
import os
from functools import partial

from rfcommon_api.common.sda import get_rabbit_url
from service_api.constants import DEFAULT_SERVICE_NAME


async def static_rabbit_connector():  # pragma: no cover
    """This function used for returning rabbitmq connection url which configure due to environment variables.

    Returns:
         Rabbitmq connection url.

    """
    return [
        os.environ.get(
            "BROKER_URL", "amqp://guest:guest@{0}:5672/".format(os.environ.get("STATIC_RABBIT_HOST", "localhost"))
        )
    ]


async def dynamic_rabbit_connector(rabbit_user="guest", rabbit_password="guest"):  # pragma: no cover
    """This function used for returning rabbitmq connection url which configure due to variables that function gets.

    Args:
        rabbit_user (str): Rabbit user. Default set to `guest`.
        rabbit_password (str): Rabbit password. Default set to `guest`.

    Returns:
        Rabbitmq connection url.

    """
    return [await get_rabbit_url(rabbit_user, rabbit_password)]


class Config:
    """Constants for configuration."""

    SDA_HOST = os.environ.get("MSP_DOCKER_IP", "172.17.42.1")
    SDA_PORT = 5000
    DB_SERVICE_NAME = os.environ.get("DB_SERVICE_NAME", "/msp/database/postgresql")
    DB_PORT = os.environ.get("DB_PORT", 5432)
    DB_USER = os.environ.get("DB_USER", "camunda")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "camunda")
    DEFAULT_DB = os.environ.get("DEFAULT_DB", "postgres")
    DB_URI_FORMAT = "postgresql://{user}:{password}@{host}:{port}/{db}"
    RABBIT_CONNECTOR = static_rabbit_connector
    RABBIT_USER = os.environ.get("RABBIT_USER", "guest")
    RABBIT_PASSWORD = os.environ.get("RABBIT_PASSWORD", "guest")
    SERVICE_NAME = DEFAULT_SERVICE_NAME
    DEBUG = False
    LOG_FORMAT = "%(asctime)s %(levelname)8s %(message)s "
    LOG_DATEFMT = "%Y-%m-%dT%H:%M:%S"
    LOG_LEVEL = logging.DEBUG
    ZOOKEEPER_SESSION_TIMEOUT = os.environ.get("ZOOKEEPER_SESSION_TIMEOUT", 60 * 60)  # default value 1 hour


class ProdConfig(Config):
    """Production configuration."""

    RABBIT_CONNECTOR = partial(
        dynamic_rabbit_connector, rabbit_user=Config.RABBIT_USER, rabbit_password=Config.RABBIT_PASSWORD
    )
    LOG_FORMAT = (
        "%(asctime)s %(levelname)8s %(funcName)20s %(message)s %(type)s %(client)s %(user)s %(crud)s %(version)s"
    )
    LOG_LEVEL = logging.INFO


class DevConfig(Config):
    """Development configuration."""

    DEBUG = True


class QCConfig(Config):
    """QC configuration."""

    DEBUG = True


ENV_2_CONFIG = {"dev": DevConfig, "qc": QCConfig, "prod": ProdConfig}


def runtime_config(config=None):
    """Sets config as development configuration, if config parameter is none.

    Args:
        config: Configuration. Default set to None.

    Returns:
        class 'service_api.config.DevConfig': Data of development configuration such as db password, db port,
                                              db service name, db url format, db user, debug, default db, log datefmt,
                                              log format, log level, rabbit password, rabbit user, sda host, sda port,
                                              service name, zookeeper session timeout.

    """
    if config is None:
        env = os.environ.get("APP_ENV", "dev")
        assert env in ENV_2_CONFIG, "Unknown APP_ENV value: " + env
        config = ENV_2_CONFIG[env]

    return config
