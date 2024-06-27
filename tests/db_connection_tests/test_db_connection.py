import aiopg

from asynctest import patch

from tests import BaseTestCase

from service_api.services.database import get_engine, release_engines
from service_api.config import DevConfig


class TestDBConnection(BaseTestCase):

    @patch("rfcommon_api.common.services.logger.get_logger")
    @patch("service_api.services.database.__server_instance")
    async def test_engine(self, server_instance_mock, *args):
        server_instance_mock.config = {
            "DEFAULT_DB": DevConfig.DEFAULT_DB,
            "DB_USER": DevConfig.DB_USER,
            "DB_PASSWORD": DevConfig.DB_PASSWORD,
            "DB_URI_FORMAT": DevConfig.DB_URI_FORMAT,
        }
        engine = await get_engine()
        self.assertIsInstance(engine, aiopg.sa.engine.Engine)
        conn = await engine.acquire()
        async with conn.execute("SELECT 1 a, 2 b") as cursor:
            result = await cursor.fetchone()
        await conn.close()
        self.assertEqual(result, (1, 2))
        await release_engines()
