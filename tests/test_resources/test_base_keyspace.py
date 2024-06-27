import json

from asynctest import patch, CoroutineMock, Mock, MagicMock
from psycopg2 import DatabaseError, InterfaceError

from service_api.services.database import _engines
from service_api.services.database import close_engine
from service_api.services.discovery import discover_pg_clients_database, DataBaseNotFoundException
from service_api.services.database import create_db
from tests import BaseTestCase, KEYSPACE_PREFIX


class TestKeyspaceResource(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.resource_url = f"{cls.base_url}/keyspaces"
        cls.keyspace_test_host = "10.2.2.111"

    @property
    def test_client(self):
        return self.create_app().test_client

    def test_missing_body_params(self):
        response = self.test_client.post(self.resource_url, gather_request=False, headers=self.headers,
                                         data=json.dumps({}))
        response_data = json.loads(response.json["error_message"].replace("\'", "\""))

        self.assertEqual(response.status, 422)
        self.assertIsInstance(response_data, dict)
        self.assertIn("hosts", response_data)
        self.assertIn("client_short_name", response_data)
        self.assertEqual(response_data["hosts"], ["Missing data for required field."])
        self.assertEqual(response_data["client_short_name"], ["Missing data for required field."])

    def test_missing_hosts_param(self):
        response = self.test_client.post(self.resource_url, gather_request=False, headers=self.headers,
                                         data=json.dumps({"client_short_name": self.app_client}))
        response_data = json.loads(response.json["error_message"].replace("\'", "\""))

        self.assertEqual(response.status, 422)
        self.assertIsInstance(response_data, dict)
        self.assertIn("hosts", response_data)
        self.assertEqual(response_data["hosts"], ["Missing data for required field."])

    def test_missing_client_short_name(self):
        response = self.test_client.post(self.resource_url, gather_request=False, headers=self.headers,
                                         data=json.dumps({"hosts": self.keyspace_test_host}))
        response_data = json.loads(response.json["error_message"].replace("\'", "\""))

        self.assertEqual(response.status, 422)
        self.assertIsInstance(response_data, dict)
        self.assertIn("client_short_name", response_data)
        self.assertEqual(response_data["client_short_name"], ["Missing data for required field."])

    def test_wrong_param_type(self):
        response = self.test_client.post(self.resource_url, gather_request=False, headers=self.headers,
                                         data=json.dumps({"hosts": 9999}))
        response_data = json.loads(response.json["error_message"].replace("\'", "\""))

        self.assertEqual(response.status, 422)
        self.assertIsInstance(response_data, dict)
        self.assertIn("hosts", response_data)
        self.assertEqual(response_data["hosts"], ["Not a valid string."])

    @patch("service_api.domain.keyspace.discover_pg_source", CoroutineMock())
    def test_create_db_when_exists(self):
        response = self.test_client.post(
            self.resource_url, gather_request=False, headers=self.headers,
            data=json.dumps({"hosts": self.keyspace_test_host, "client_short_name": self.app_client})
        )

        self.assertEqual(response.status, 200)
        self.assertIsInstance(response.json["message"], str)
        self.assertEqual(
            response.json["message"],
            f"Database '{KEYSPACE_PREFIX}_{self.app_client}' exists"
        )

    @patch("service_api.domain.keyspace.discover_pg_source",
           CoroutineMock(side_effect=DataBaseNotFoundException(
               f"SDA did not find source db 'rfadjustments_new_client'")
           ))
    @patch("service_api.domain.keyspace.database.create_db", CoroutineMock())
    def test_create_db_success(self):
        new_client_short_name = "new_client"

        response = self.test_client.post(
            self.resource_url, gather_request=False, headers=self.headers,
            data=json.dumps({"hosts": self.keyspace_test_host, "client_short_name": new_client_short_name})
        )

        self.assertEqual(response.status, 201)
        self.assertIsInstance(response.json["message"], str)
        self.assertEqual(
            response.json["message"],
            f"Database '{KEYSPACE_PREFIX}_{new_client_short_name}' successfully created"
        )

    @patch("service_api.services.database.get_engine",
           CoroutineMock(side_effect=InterfaceError)
           )
    async def test_create_db_failed(self):
        with self.assertRaises(InterfaceError):
            await create_db()

    @patch("service_api.services.discovery.discover_data_source", CoroutineMock(return_value=None))
    async def test_pg_clients_database_not_found(self):
        service_name = "adjustm"
        with self.assertRaises(DataBaseNotFoundException) as context:
            await discover_pg_clients_database(service_name=service_name)
        self.assertEqual(context.exception.status_code, 503)

    async def test_close_engine_write_error_on_except(self):
        with patch("service_api.domain.keyspace.database.logger", Mock()) as logger_mock:
            new_client_short_name = "new_client"

            engine_mock = Mock()
            engine_mock.close = Mock(side_effect=DatabaseError())
            _engines[new_client_short_name] = engine_mock

            await close_engine(new_client_short_name)
            del _engines[new_client_short_name]

            logger_mock.error.assert_called_once_with(f'Engine {new_client_short_name} failed to close. Error: ')
