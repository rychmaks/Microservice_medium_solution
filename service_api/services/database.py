"""This module contains all needed functions to work with database."""

from typing import Tuple, Optional
import asyncio

import psycopg2
from aiopg.sa import create_engine, Engine
from psycopg2 import DatabaseError, InterfaceError
from sanic.app import Sanic
from sqlalchemy.sql.ddl import CreateTable

from service_api.constants import KEYSPACE_PREFIX, COMMON_DB, DEFAULT_ENGINE_NAME
from service_api.models import models
from service_api.services.discovery import discover_pg_source, discover_pg_clients_database, DataBaseNotFoundException
from rfcommon_api.common.services.logger import logger

# http://aiopg.readthedocs.io/en/stable/core.html?highlight=create_pool#aiopg.create_pool
POOL_SIZE = 5
POOL_RECYCLE = 120
CONNECTION_TIMEOUT = 600
# parameter for logging executed SQL commands
ECHO = False
CONNECTION_LOCK = None

_engines = {}

__server_instance = None


def lock() -> asyncio.Lock:
    """This function returns instance of connection lock."""
    global CONNECTION_LOCK

    if not CONNECTION_LOCK:
        CONNECTION_LOCK = asyncio.Lock()
    return CONNECTION_LOCK


async def release_engines():
    """Release engines.

    This function mark all engine connections to be closed on getting back to pool and delete engine from dict.

    """
    for key in tuple(_engines.keys()):
        await close_engine(key)
        del _engines[key]


async def close_engine(client_name: str):
    """Close engine.

    This function mark all engine connections to be closed on getting back to pool.

    Args:
        client_name: Client short name.

    """
    engine = _engines[client_name]
    try:
        engine.close()
        await engine.wait_closed()
        logger.info(f"Engine {client_name} successfully released")
    except (DatabaseError, InterfaceError) as exc:
        logger.error(f"Engine {client_name} failed to close. Error: {exc}")


def register_server(app: Sanic):
    """Register server.

    Args:
        app: Instance of Sanic application.

    """
    global __server_instance
    __server_instance = app


async def db_uri(client_name: Optional[str] = None, host: Optional[str] = None) -> str:
    """Returns a URI describing a database connection.

    Args:
        client_name: Client short name. Default set to None.
        host: Link to a host. Default set to none.

    Returns:
        URI describing a database connection.

    """
    db_name = __server_instance.config["DEFAULT_DB"]

    if client_name:
        if client_name == COMMON_DB:
            db_name = COMMON_DB
        else:
            db_name = f"{KEYSPACE_PREFIX}_{client_name}"

    if not host:
        _host, _port = await discover_pg_source(db_name)
    else:
        _host, _port = host, __server_instance.config["DB_PORT"]

    uri = __server_instance.config["DB_URI_FORMAT"].format(
        user=__server_instance.config["DB_USER"],
        password=__server_instance.config["DB_PASSWORD"],
        host=_host,
        port=_port,
        db=db_name,
    )

    logger.debug(f">>>>>>>>>>> db uri: {uri}")

    return uri


def _create_engine(connection_url: str):
    """A coroutine for Engine creation.

    Args:
        connection_url: connection url.

    Returns:
        sqlalchemy.engine.Engine: Engine instance with embedded connection pool.

    """
    if ECHO:  # pragma: no cover
        logger.warning("ECHO MODE ENABLED FOR DATABASE CONNECTION")
    return create_engine(
        connection_url, maxsize=POOL_SIZE, pool_recycle=POOL_RECYCLE, timeout=CONNECTION_TIMEOUT, echo=ECHO
    )


async def get_engine(client: Optional[str] = None, host: Optional[str] = None) -> Engine:
    """Returns Engine instance. If no client passed return default engine.

    Args:
        client: Client short name from X-client. Default set to None.
        host: Link to a host. Default set to None.

    Returns:
        sqlalchemy.engine.Engine: Instance which provide a source of database connectivity and behavior.

    """
    global _engines
    if client:
        engine_name = client
    else:
        engine_name = DEFAULT_ENGINE_NAME

    if engine_name not in _engines:
        async with lock():
            connection_url = await db_uri(client_name=engine_name if engine_name != DEFAULT_ENGINE_NAME else None,
                                          host=host)
            _engines[engine_name] = await _create_engine(connection_url)

    try:
        async with _engines[engine_name].acquire() as conn:
            await conn.execute("select 1 a")
    except (DatabaseError, InterfaceError) as error:
        logger.debug(f"Connection error: {error} \n Trying to reconnect...")
        async with lock():
            await close_engine(engine_name)
            _engines.pop(engine_name)

            connection_url = await db_uri(client_name=engine_name if engine_name != DEFAULT_ENGINE_NAME else None,
                                          host=host)
            _engines[engine_name] = await _create_engine(connection_url)

    logger.debug(">>>> returning engine: %s" % engine_name)
    return _engines[engine_name]


async def create_db(client_name: Optional[str] = None, host: Optional[str] = None) -> Tuple[str, int]:
    """This function is used for creating client db.

    Args:
        client_name: Client short name.
        host: Postgres db.

    Returns:
        Message that db was created or message that db exists.

    Raises:
        DatabaseError: Raises when an operation related to db failed.
        InterfaceError: Raises when database connection fails for some reason.

    """
    try:
        engine = await get_engine(host=host)
        async with engine.acquire() as connection:
            check_client_db = await connection.execute(
                "SELECT datname FROM pg_catalog.pg_database WHERE datname='{0}_{1}';".format(
                    KEYSPACE_PREFIX, client_name
                )
            )
            if await check_client_db.fetchall():
                return f"Database '{KEYSPACE_PREFIX}_{client_name}' exists."
            else:
                await connection.execute("CREATE DATABASE {0}_{1};".format(KEYSPACE_PREFIX, client_name))

        engine = await get_engine(client_name, host)
        async with engine.acquire() as connection:
            async with connection.begin():
                for model in models:
                    create_expr = CreateTable(model)
                    await connection.execute(create_expr)
        return f"Database '{KEYSPACE_PREFIX}_{KEYSPACE_PREFIX}' created"
    except (DatabaseError, InterfaceError) as err:
        logger.error(err)
        raise err


async def drop_all_service_keyspaces():
    """This function is used for dropping all service keyspaces.

    Raises:
        DataBaseNotFoundException: Raises when database not found.

    """
    try:
        discovered_databases = await discover_pg_clients_database(service_name=KEYSPACE_PREFIX)
        for postgres_ip, db_name in discovered_databases:
            engine = await get_engine(host=postgres_ip)
            async with engine.acquire() as conn:

                terminate_query = f"select pg_terminate_backend(pid) from pg_stat_activity where datname='{db_name}'"
                await conn.execute(terminate_query)

                drop_query = f"drop database if exists {db_name};"
                await conn.execute(drop_query)

                logger.info(f"Dropped keyspace name: {db_name}")
    except DataBaseNotFoundException:
        logger.error(f"SDA did not find '{KEYSPACE_PREFIX}' Nothing to do here")
    finally:
        await release_engines()


async def drop_db(db_name, db_ip):
    """This function is used for dropping database.

    Raises:
        DatabaseError: Raises when an operation related to db failed.
        InterfaceError: Raises when database connection fails for some reason.

    """
    try:
        engine = await get_engine(host=str(db_ip))

        drop_connections_query = """SELECT pg_terminate_backend(pg_stat_activity.pid)
                                     FROM pg_stat_activity
                                     WHERE pg_stat_activity.datname = '{db_name}'
                                     AND pid <> pg_backend_pid();"""
        drop_connections_query = drop_connections_query.format(db_name=db_name)

        drop_db_query = "DROP DATABASE {db_name};"
        drop_db_query = drop_db_query.format(db_name=db_name)

        async with engine.acquire() as conn:
            await conn.execute(drop_connections_query)
            await conn.execute(drop_db_query)
            logger.info(f"Dropped keyspace name: {db_name}")
    except (psycopg2.DatabaseError, psycopg2.InterfaceError) as err:
        logger.error(f"SDA did not find '{db_name}', error: {err}")
    finally:
        await release_engines()
