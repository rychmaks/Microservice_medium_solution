import os
import psycopg2
import pytest

from asynctest import TestCase
from sqlalchemy import text

from tests.fixtures import FixtureLoader
from service_api.app import app
from service_api.constants import KEYSPACE_PREFIX
from service_api.services.database import get_engine, release_engines
from rfcommon_api.common.services.logger import logger
from service_api.services.discovery import discover_pg_source


TEST_CLIENT = os.environ.get("CI_APP_CLIENT", "test")
CLIENT_DB_NAME = f"{KEYSPACE_PREFIX}_{TEST_CLIENT}"
DB_NAME = "postgres"


@pytest.mark.usefixtures("db_fixture")
@pytest.mark.usefixtures("get_host")
class BaseTestCase(TestCase):
    app_client = TEST_CLIENT
    base_url = f"/{app.config.get('SERVICE_NAME')}/v1"
    headers = {"Content-type": "application/json", "X-Client": app_client, "Authorization": "SessionID xxx"}
    headers_without_xclient = {"Content-type": "application/json", "Authorization": "SessionID xxx"}
    fixture_file = "test_data.yaml"
    client_db_name = CLIENT_DB_NAME
    db_name = "postgres"

    def create_app(self):
        return app

    async def setUp(self):
        host, _ = await discover_pg_source(DB_NAME)
        await clear_tables(self.app_client, self.client_db_name, host)
        await FixtureLoader((self.app_client,), self.fixture_file, host).load_data()
        await release_engines()

    async def tearDown(self):
        await release_engines()


async def clear_tables(client_name, db_name, db_ip):
    try:
        engine = await get_engine(client=client_name, host=db_ip)
        get_tables_name_query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        async with engine.acquire() as conn:
            async for each_row in await conn.execute(get_tables_name_query):
                await conn.execute(text(f"TRUNCATE TABLE {each_row[0]} CASCADE;"))
                logger.info(f"Table '{each_row[0]}'' has been cleaned")
    except (psycopg2.DatabaseError, psycopg2.InterfaceError) as err:
        logger.error(f"An error occurred while cleaning DB '{db_name}', error: {err}")
    finally:
        await release_engines()
