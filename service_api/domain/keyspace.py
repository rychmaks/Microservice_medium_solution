"""Provide needed functionality for database creating."""

from rfcommon_api.common.services.logger import logger
from service_api.constants import KEYSPACE_PREFIX
from service_api.services import database
from service_api.services.discovery import discover_pg_source, DataBaseNotFoundException


async def create_client(host: str, client_name: str) -> (bool, str):
    """Function for creating database if such doesn't exist.

    Args:
        host: Postgres db host.
        client_name: Client short name

    Returns:
        False and message that database exist
        or True and message with information that database was created,
        if such database wasn't exist.

    """
    client_db_name = f"{KEYSPACE_PREFIX}_{client_name}"
    try:
        await discover_pg_source(client_db_name)
        return False, f"Database '{client_db_name}' exists"
    except DataBaseNotFoundException:
        await database.create_db(client_name=client_name, host=host)
        logger.info(f"Database '{client_db_name}' successfully created")
        return True, f"Database '{client_db_name}' successfully created"
