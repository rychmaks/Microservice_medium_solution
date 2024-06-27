"""This module is used for discovering database."""

from typing import List, Tuple

from rfcommon_api.common.sda import discover_data_source
from rfcommon_api.common.exceptions import ApplicationError


class DataBaseNotFoundException(ApplicationError):
    """Raised when specific database name not found in SDA."""

    def __init__(self, msg):
        """Sends msg and status code of exception to parent class.

        Args:
            msg (str): message of exception.

        """
        super().__init__(msg, status_code=503)


async def discover_pg_clients_database(service_name: str, run_locally=False) -> List[Tuple[str, str]]:
    """Discovers postgres clients database.

    Args:
        service_name: Name of service.
        run_locally (bool): A parameter that determines whether to run locally.

    Returns:
        Ip and name of db.

    Raises:
        DatabaseNotFound: If database does not exist, will raise this exception.

    """
    res = await discover_data_source(service_name, "datasearch", run_locally)
    if not res:
        raise DataBaseNotFoundException("SDA did not find '{}'".format(service_name))

    return [(r["ip"], r["name"]) for r in res if r["type"] == "postgresql" and r["name"].split("_")[0] == service_name]


async def discover_pg_source(db_name: str, run_locally=False):
    """Discovers Postgres DB.

    Args:
        db_name: Name of db.
        run_locally (bool): A parameter that determines whether to run locally.

    Returns:
        tuple: Ip and port of db.

    Raises:
        DatabaseNotFound: If database does not exist, will raise this exception.

    """
    res = await discover_data_source(db_name, "dataget", run_locally)
    if not res:
        raise DataBaseNotFoundException("SDA did not find source db '{}'".format(db_name))

    return res[0]["ip"], 5432
