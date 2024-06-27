"""This module contains needed methods for correct service starting."""

#! /usr/bin/env python
import argparse
import asyncio
import sys
from itertools import chain

import uvloop
from sanic.server import HttpProtocol

from service_api.app import app
from service_api.constants import (
    KEYSPACE_PREFIX,
    COMMON_DB,
    DEFAULT_SERVICE_NAME,
    DISCOVER_RETRY_NUM,
    DISCOVER_RETRY_TIMEOUT
)
from service_api.services.database import drop_all_service_keyspaces, drop_db, create_db
from service_api.services.discovery import discover_pg_clients_database, DataBaseNotFoundException, discover_pg_source
from rfcommon_api.common.services.logger import logger


async def ensure_all_dropped():
    """This function is used for checking if all keyspace was dropped.

    Raises:
        SystemExit: Raises when an Per-client DBs still discoverable.
    """

    for retries_left in range(DISCOVER_RETRY_NUM):
        res = await discover_pg_clients_database(KEYSPACE_PREFIX, False)
        db_list = list(filter(lambda dl: dl[1].startswith(KEYSPACE_PREFIX + '_'), res))
        if not db_list:
            logger.info('All gone')
            break
        logger.info('Database(s) still discoverable, sleeping for 61 second...')
        await asyncio.sleep(DISCOVER_RETRY_TIMEOUT)
    else:
        raise SystemExit("Per-client DBs still discoverable, purging NOT confirmed!")


async def drop_common_db():
    """This function is used for dropping database.

    Add log with information that database not found if raises DataBaseNotFoundException.

    Raises:
        SystemExit: Raises when an Common DB still discoverable.

    """
    # find and drop common db
    try:
        host, _ = await discover_pg_source(COMMON_DB, False)
        if host:
            await drop_db(COMMON_DB, host)
            for retries_left in range(DISCOVER_RETRY_NUM):
                if await discover_pg_source(COMMON_DB, False):
                    logger.info('common_db still discoverable, sleeping for 61 second ...')
                    await asyncio.sleep(DISCOVER_RETRY_TIMEOUT)
            else:
                raise SystemExit("Common DB still discoverable, purging NOT confirmed!")
    except DataBaseNotFoundException:
        logger.info("SDA did not find common db {}. Seems gone".format(COMMON_DB))


def discover_postgres_clients_db(run_locally=False):
    """Discovers postgres clients database.

    Add log with information that database not found if raises DataBaseNotFoundException.

    Args:
        run_locally (bool): A parameter that determines whether to run locally. Default set to None.

    Returns:
        int: 0.

    """

    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        # get all db's from discovery service
        rez = loop.run_until_complete(discover_pg_clients_database(KEYSPACE_PREFIX, run_locally))
        loop.close()
        host_db = [item for item in rez]
        print(":".join(list(chain.from_iterable(host_db))))  # noqa T001
    except DataBaseNotFoundException as exc:
        logger.error(f"Exception during clients databases discovering {exc}")
    return 0


def discover_postgres_common_db(run_locally=False):
    """Discovers postgres common database.

    Add log with information that database not found if raises DataBaseNotFoundException.

    Args:
        run_locally (bool): A parameter that determines whether to run locally. Default set to None.

    Returns:
        int: 0.

    """
    try:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        loop = asyncio.get_event_loop()
        host, _ = loop.run_until_complete(discover_pg_source(COMMON_DB, run_locally))
        loop.close()
        print(host)  # noqa T001
    except DataBaseNotFoundException as exc:
        logger.error(f"Exception during common database discovering {exc}")
    return 0


def drop_all_keyspaces(sleep_time=90):
    """This function is used for dropping all service keyspaces.

    Add log with information that database not found if raises DataBaseNotFoundException.

    Args:
        sleep_time: Suspension time. Default set to none.

    """
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    # drop all per-client db's
    loop.run_until_complete(drop_all_service_keyspaces())
    try:
        loop.run_until_complete(ensure_all_dropped())
    except DataBaseNotFoundException:
        logger.info('SDA did not find per-client databases for this service. Seems all gone')
    loop.close()


def get_common_db_name():
    """Print common db name."""
    print(COMMON_DB)  # noqa T001


def init_keyspaces(host, client_names=None):
    """This function is used for creating client db.

    Args:
        client_names (str): Client short name. Default set to None.
        host (str): Postgres db.

    """
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    try:
        for client_name in client_names:
            loop.run_until_complete(create_db(client_name, host))
    except TypeError:
        pass


def populate_fixtures(client_names, file_name):
    """This function is used for loading fixtures.

    Args:
        client_names (str): Name of client.
        file_name (str): Name of file where contains fixtures.

    """
    from tests.fixtures import FixtureLoader

    loader = FixtureLoader(client_names, file_name)
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(loader.load_data())


def start_celery_worker():
    """This function used to start a Celery worker instance."""
    from celery.app.base import Celery
    from celery.bin import worker

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    broker = loop.run_until_complete(app.config["RABBIT_CONNECTOR"]())
    loop.close()
    celery = Celery("remote", backend="amqp", broker=broker)
    celery.conf.update(app.config)

    __import__("service_api.services.celery_tasks")

    worker = worker.worker(app=celery)
    worker.run(queues=["{prefix}_celery".format(prefix=DEFAULT_SERVICE_NAME)], loglevel=app.config.get("LOG_LEVEL"))


def runserver(host, port):
    """This function setup params and run server.

    Args:
        host (str): Host where server will be running.
        port (str): Port where server will be running.

    """
    class CGDPHttpProtocol(HttpProtocol):
        """Class which configure request timeout."""

        def __init__(self, *args, **kwargs):
            """Setup request timeout."""
            if "request_timeout" in kwargs:
                kwargs.pop("request_timeout")
            super().__init__(*args, request_timeout=300, **kwargs)

    app.run(host=host, port=port, protocol=CGDPHttpProtocol)


def parse_args(args):
    """This function parses parameters before starting service."""

    parser = argparse.ArgumentParser(description="Sanic rest api skeleton", add_help=False)
    parser.add_argument("--help", action="help", help="show this help message and exit")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(get_common_db_name.__name__, add_help=False, help="Returns name of the common_database")

    sparser = subparsers.add_parser(
        discover_postgres_clients_db.__name__, add_help=False, help="Discover all clients dbs"
    )
    sparser.add_argument("-l", "--run_locally", type=bool, dest="run_locally", help="Run local. True or False")

    sparser = subparsers.add_parser(
        drop_all_keyspaces.__name__, add_help=False, help="Drop all client keyspaces. WARNING Do not use on PROD"
    )
    sparser.add_argument(
        "-t", "--sleep-time", dest="sleep_time", default=90, type=int, help="Sleep time before exit from drop procedure"
    )
    sparser = subparsers.add_parser(runserver.__name__, add_help=False, help="Discover all clients dbs")
    sparser.add_argument("-h", "--host", dest="host", default="0.0.0.0", type=str, help="Host address")
    sparser.add_argument("-p", "--port", dest="port", default=5000, type=int, help="Host post")
    subparsers.add_parser(start_celery_worker.__name__, add_help=False, help="Start celery worker")
    sparser = subparsers.add_parser(discover_postgres_common_db.__name__, add_help=False, help="Discover common db")
    sparser.add_argument("-l", "--run_locally", type=bool, dest="run_locally", help="Run local. True or False")
    sparser = subparsers.add_parser(init_keyspaces.__name__, add_help=False, help="Init keyspaces")
    sparser.add_argument("-h", "--host", dest="host", default="0.0.0.0", type=str, help="DB host")
    sparser.add_argument("--clients", dest="client_names", default=[], help="List of clients", action="append")
    sparser = subparsers.add_parser(populate_fixtures.__name__, add_help=False, help="Populate fixtures")
    sparser.add_argument("--clients", dest="client_names", default=[], help="List of clients", action="append")
    sparser.add_argument(
        "-f", dest="file_name", default="dataload_sample_data.yaml", help="Fixtures file name", type=str
    )
    return parser.parse_args(args=args)


def main(args=None):
    """This function is responsible for running the required functionality, depending on the arguments provided."""
    parsed_args = parse_args(args or sys.argv[1:])

    if parsed_args.command == discover_postgres_clients_db.__name__:
        discover_postgres_clients_db(parsed_args.run_locally)
    elif parsed_args.command == discover_postgres_common_db.__name__:
        discover_postgres_common_db(parsed_args.run_locally)
    elif parsed_args.command == drop_all_keyspaces.__name__:
        drop_all_keyspaces(parsed_args.sleep_time)
    elif parsed_args.command == get_common_db_name.__name__:
        get_common_db_name()
    elif parsed_args.command == start_celery_worker.__name__:
        start_celery_worker()
    elif parsed_args.command == runserver.__name__:
        runserver(parsed_args.host, parsed_args.port)
    elif parsed_args.command == init_keyspaces.__name__:
        init_keyspaces(parsed_args.host, parsed_args.client_names)
    elif parsed_args.command == populate_fixtures.__name__:
        populate_fixtures(parsed_args.client_names, parsed_args.file_name)
    else:
        runserver(parsed_args.host, parsed_args.port)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(
            "Unexpected exception occurred. Service is going to shutdown. Error message: {}".format(e),
            extra={"error_message": e},
        )
        exit(1)
    finally:
        logger.info("Service stopped.")
