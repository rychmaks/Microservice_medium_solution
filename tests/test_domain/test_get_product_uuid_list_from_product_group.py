from multidict._multidict import CIMultiDict

from service_api.domain.arrangement import get_product_uuid_list_from_product_group
from asynctest import patch, CoroutineMock, MagicMock
from tests import BaseTestCase

REQUIRED_HEADERS = CIMultiDict({
    "X-Client": "test",
    "Authorization": "test",
    "x-timezone": "UTC"
})

PRODUCT_GROUP_UUID = '111'


class TestArrangementsDomain(BaseTestCase):

    @patch('service_api.domain.arrangement.RESTClientRegistry')
    async def test_get_product_uuid_list_from_product_group_success(self, mock_arrangments_client):
        arrangement_mock = MagicMock()
        arrangement_mock.get_product_group_product = CoroutineMock(return_value=[{'product_uuid': '123'}])
        mock_arrangments_client.get = MagicMock(return_value=arrangement_mock)
        actual = await get_product_uuid_list_from_product_group(PRODUCT_GROUP_UUID, REQUIRED_HEADERS)
        expected = ['123']
        self.assertEqual(expected, list(actual))
