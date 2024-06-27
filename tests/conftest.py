import pytest
import service_api

from asyncio import new_event_loop

from service_api.domain.keyspace import create_client
from service_api.services import database
from tests import TEST_CLIENT, CLIENT_DB_NAME, DB_NAME


@pytest.fixture(scope="session", autouse=True)
def db_fixture():

    loop = new_event_loop()
    default_db_host = loop.run_until_complete(database.discover_pg_source(DB_NAME))[0]
    loop.run_until_complete(create_client(default_db_host, TEST_CLIENT))
    loop.run_until_complete(database.release_engines())

    yield

    loop = new_event_loop()
    loop.run_until_complete(database.drop_all_service_keyspaces())
    loop.run_until_complete(database.drop_db(CLIENT_DB_NAME, default_db_host))
    loop.run_until_complete(database.release_engines())
    loop.close()


@pytest.fixture
def get_host(monkeypatch):
    loop = new_event_loop()
    host = loop.run_until_complete(database.discover_pg_source(DB_NAME))[0]
    loop.close()

    async def mock(*args, **kwargs):
        return host, 5432

    monkeypatch.setattr(service_api.services.database, "discover_pg_source", mock)
    return host
