from asynctest import (
    CoroutineMock,
    patch,
)

from tests import BaseTestCase
from tests.mock_for_tests import ArrangementMock


@patch("rfcommon_api.common.services.rest_client.arrangment.ArrangementsRESTClientV2.get_methodology_definitions",
       CoroutineMock(return_value=ArrangementMock.qualification_methodology))
@patch("rfcommon_api.common.services.rest_client.projects.ProjectsRESTClient.get_project",
       CoroutineMock(return_value={"project_date_start": "2018-11-21", "project_date_end": "2018-11-27"}))
class TestArrangementResources(BaseTestCase):

    @property
    def test_client(self):
        return self.create_app().test_client

    @property
    def resource_url(self):
        return f"{self.base_url}/tier_override"

    @patch(
        "rfcommon_api.common.services.rest_client.arrangment.ArrangementsRESTClientV2.get_price_group_methodologies",
        CoroutineMock(return_value=ArrangementMock.price_group_methodology_new_tier_format)
    )
    @patch("service_api.domain.arrangement.get_product_uuid_list_from_product_group",
           CoroutineMock(return_value=["dba4f78c-7488-11e8-93f3-0242ac110018"]))
    def test_get_tiers_with_new_tier_format(self):
        price_group_uuid = "20247d5f58-1574-42cf-94af-b4c22c4045ac"
        product_uuid = "dba4f78c-7488-11e8-93f3-0242ac110018"
        url = (
            f"{self.resource_url}/00000000-0000-0000-0000-000000000000"
            f"?filter=price_group_uuid eq {price_group_uuid}&filter=product_uuid eq {product_uuid}"
        )

        response = self.test_client.get(url, headers=self.headers, gather_request=False)
        expected_result = [
            {
                "tier_id": 111,
                "tier_name": "tier_1",
                "values": [
                    {
                        "earliest_date": "2018-11-01",
                        "latest_date": "2018-11-30",
                        "value": 5
                    }
                ]
            },

            {
                "tier_id": 222,
                "tier_name": "tier_2",
                "values": [
                    {
                        "earliest_date": "2018-11-01",
                        "latest_date": "2018-11-15",
                        "value": 10
                    }
                ]
            }
        ]
        self.assertEqual(response.status, 200)
        self.assertEqual(response.json, expected_result)

    @patch(
        "rfcommon_api.common.services.rest_client.arrangment.ArrangementsRESTClientV2.get_price_group_methodologies",
        CoroutineMock(return_value=ArrangementMock.pgm_aggregate_by_product_new_tier_format)
    )
    def test_get_tiers_with_new_tier_format_aggregate_by_product(self):
        price_group_uuid = "20247d5f58-1574-42cf-94af-b4c22c4045ac"
        url = (
            f"{self.resource_url}/00000000-0000-0000-0000-000000000000"
            f"?filter=price_group_uuid eq {price_group_uuid}"
        )

        resp = self.test_client.get(url, headers=self.headers, gather_request=False)
        expected_result = [
            {
                "tier_id": 111,
                "tier_name": "tier_1",
                "values": [
                    {
                        "earliest_date": "2018-11-01",
                        "latest_date": "2018-11-30",
                        "value": 5
                    }
                ]
            },
            {
                "tier_id": 222,
                "tier_name": "tier_2",
                "values": [
                    {
                        "earliest_date": "2018-11-01",
                        "latest_date": "2018-11-30",
                        "value": 10
                    }
                ]
            }
        ]
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json, expected_result)

    @patch(
        "rfcommon_api.common.services.rest_client.arrangment.ArrangementsRESTClientV2.get_price_group_methodologies",
        CoroutineMock(
            return_value=ArrangementMock.price_group_methodology_new_tier_format_without_methodology_definition_uuid)
    )
    def test_get_tiers_with_new_tier_format_without_methodology_definition_uuid(self):
        with patch(
                "rfcommon_api.common.services.rest_client.arrangment.ArrangementsRESTClientV2.get_methodology_definitions",  # noqa E501
                CoroutineMock(return_value=None)):
            price_group_uuid = "20247d5f58-1574-42cf-94af-b4c22c4045ac"
            product_uuid = "dba4f78c-7488-11e8-93f3-0242ac110018"
            url = (
                f"{self.resource_url}/00000000-0000-0000-0000-000000000000"
                f"?filter=price_group_uuid eq {price_group_uuid}&filter=product_uuid eq {product_uuid}"
            )

            response = self.test_client.get(url, headers=self.headers, gather_request=False)
            expected_result = []
            self.assertEqual(response.status, 200)
            self.assertEqual(response.json, expected_result)
