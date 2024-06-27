import json
import uuid

from asynctest import (
    CoroutineMock,
    patch
)
from copy import deepcopy

from service_api.constants import (RF_SYSTEM_EVENTS, SYSTEM_EVENT_AMOUNT_OVERRIDE, ADJUSTMENT_UPDATED_TOPIC,
                                   SYSTEM_EVENT_TIER_OVERRIDE)
from service_api.services.forms import AdjustmentStatuses

from tests import BaseTestCase
from tests.mock_for_tests import AdjustmentMock, UserObjectMock


@patch("rfcommon_api.common.services.rest_client.projects.ProjectsRESTClient.get_project",
       CoroutineMock(return_value=AdjustmentMock.project_registry_data))
@patch("rfcommon_api.common.services.audit_logger.get_project_type_service_area",
       CoroutineMock(return_value=AdjustmentMock.project_registry_data["project_type"]))
@patch("rfcommon_api.common.services.audit_logger.get_user_login",
       CoroutineMock(return_value=UserObjectMock.registry_data["profile"]["login"]))
@patch("rfcommon_api.common.services.audit_logger.get_user_roles",
       CoroutineMock(return_value=UserObjectMock.registry_data["roles"]))
@patch("rfcommon_api.common.domain.user.UserObject.get_user_data",
       CoroutineMock(return_value=UserObjectMock.registry_data))
@patch("service_api.resources.adjustment_resources._validate_user_permission", CoroutineMock())
@patch("rfcommon_api.common.services.rest_client.notification.NotificationRESTClient.send_notification")
@patch("service_api.domain.adjustment.KafkaProducer.publish", side_effect=CoroutineMock())
class TestOverridesResources(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.resource_url = f"{cls.base_url}/adjustments"

    @property
    def test_client(self):
        return self.create_app().test_client

    def test_create_manual_override(self, kafka_mock, notification_mock):
        changes = [{"field": "adjustment_value", "oldvalue": "\"200\"", "newvalue": "\"0\""}]
        data = AdjustmentMock.create_manual_override_data
        message = {
            "client": BaseTestCase.app_client,
            "project_type": AdjustmentMock.project_registry_data["project_type"],
            "project_id": AdjustmentMock.project_registry_data["id"],
            "event": SYSTEM_EVENT_AMOUNT_OVERRIDE
        }

        with self.assertLogs(AdjustmentMock.logger_name, level=AdjustmentMock.log_level) as cm:
            request, resp = self.test_client.post(
                self.resource_url, headers=self.headers, data=json.dumps(data)
            )
            output_audit_log = json.loads(cm.records[0].message)
            audit_log = output_audit_log["AUDIT"]
            self.assertEqual(audit_log["action"], "Update")
            self.assertEqual(audit_log["statuscode"], 200)
            self.assertEqual(audit_log["changelog"]["entity"], "Adjustment")
            self.assertEqual(audit_log["changelog"]["changes"], changes)

        kafka_mock.assert_awaited_once_with(RF_SYSTEM_EVENTS, message)
        notification_mock.assert_awaited_once_with(
            context={"headers": request.headers},
            topic=ADJUSTMENT_UPDATED_TOPIC,
            data={"record_hash": data["record_hash"], "adjustment_id": uuid.UUID(resp.json["id"])}
        )
        self.assertEqual(resp.status, 201)
        self.assertEqual(list(resp.json.keys()), AdjustmentMock.adjustment_fields)
        self.assertEqual(resp.json["product_uuid"], data["product_uuid"], )
        self.assertEqual(resp.json["bu_uuid"], data["bu_uuid"])
        self.assertEqual(resp.json["project_uuid"], data["project_uuid"])
        self.assertEqual(resp.json["adjustment_value"], data["adjustment_value"])
        self.assertEqual(resp.json["comment"], data["comment"])
        self.assertEqual(resp.json["price_group_uuid"], data["price_group_uuid"])
        self.assertEqual(resp.json["status"], AdjustmentStatuses.not_applied.value)
        self.assertEqual(
            resp.json["user_full_name"],
            f"{UserObjectMock.registry_data['profile']['firstName']} "
            f"{UserObjectMock.registry_data['profile']['lastName']}"
        )

    def test_create_manual_override_with_adjustment_and_tier(self, kafka_mock, notification_mock):
        data = AdjustmentMock.create_manual_override_data_with_adjustment_and_tier_override_simultaneously

        resp = self.test_client.post(
            self.resource_url, headers=self.headers, data=json.dumps(data), gather_request=False
        )

        self.assertEqual(resp.status, 500)
        self.assertEqual(resp.json, {
            "error_message": "Validation error, can't add manual adjustment and tier override simultaneously"})

    # ToDo: determine with BA's about zero as value to override
    def test_create_manual_override_failed_without_adjustment_and_tier(self, kafka_mock, notification_mock):
        data = AdjustmentMock.create_manual_override_data_without_adjustment_and_tier_override_simultaneously

        resp = self.test_client.post(
            self.resource_url, headers=self.headers, data=json.dumps(data), gather_request=False
        )

        self.assertEqual(resp.status, 500)
        self.assertEqual(resp.json, {"error_message": "Validation error, missing a value to override"})

    def test_create_tier_override(self, kafka_mock, notification_mock):
        changes = [{"field": "tier_id", "oldvalue": "4342", "newvalue": "6786"}]
        data = AdjustmentMock.create_tier_override_data
        message = {
            "client": BaseTestCase.app_client,
            "project_type": AdjustmentMock.project_registry_data["project_type"],
            "project_id": AdjustmentMock.project_registry_data["id"],
            "event": SYSTEM_EVENT_TIER_OVERRIDE
        }

        with self.assertLogs(AdjustmentMock.logger_name, level=AdjustmentMock.log_level) as cm:
            request, resp = self.test_client.post(
                self.resource_url, headers=self.headers, data=json.dumps(data)
            )
            output_audit_log = json.loads(cm.records[0].message)
            audit_log = output_audit_log["AUDIT"]
            self.assertEqual(audit_log["action"], "Update")
            self.assertEqual(audit_log["statuscode"], 200)
            self.assertEqual(audit_log["changelog"]["entity"], "Adjustment")
            self.assertEqual(audit_log["changelog"]["changes"], changes)

        kafka_mock.assert_awaited_once_with(RF_SYSTEM_EVENTS, message)
        notification_mock.assert_awaited_once_with(
            context={"headers": request.headers},
            topic=ADJUSTMENT_UPDATED_TOPIC,
            data={"record_hash": data["record_hash"], "adjustment_id": uuid.UUID(resp.json["id"])}
        )
        self.assertEqual(resp.status, 201)
        self.assertEqual(list(resp.json.keys()), AdjustmentMock.adjustment_fields)
        self.assertEqual(resp.json["product_uuid"], data["product_uuid"])
        self.assertEqual(resp.json["bu_uuid"], data["bu_uuid"])
        self.assertEqual(resp.json["project_uuid"], data["project_uuid"])
        self.assertEqual(resp.json["adjustment_value"], data["adjustment_value"])
        self.assertEqual(resp.json["comment"], data["comment"])
        self.assertEqual(resp.json["price_group_uuid"], data["price_group_uuid"])
        self.assertEqual(resp.json["status"], AdjustmentStatuses.not_applied.value)
        self.assertEqual(
            resp.json["user_full_name"],
            f"{UserObjectMock.registry_data['profile']['firstName']} "
            f"{UserObjectMock.registry_data['profile']['lastName']}"
        )

    def test_update_manual_override(self, kafka_mock, notification_mock):
        changes = [{"field": "adjustment_value", "oldvalue": "\"200\"", "newvalue": "\"999999.0\""}]
        data = AdjustmentMock.update_manual_override_data
        message = {
            "client": BaseTestCase.app_client,
            "project_type": AdjustmentMock.project_registry_data["project_type"],
            "project_id": AdjustmentMock.project_registry_data["id"],
            "event": SYSTEM_EVENT_AMOUNT_OVERRIDE
        }

        with self.assertLogs(AdjustmentMock.logger_name, level=AdjustmentMock.log_level) as cm:
            request, resp = self.test_client.put(
                f"{self.resource_url}/32d256ae-a704-4bd2-aa2a-085d34ae4df2",
                headers=self.headers,
                data=json.dumps(data)
            )
            output_audit_log = json.loads(cm.records[0].message)
            audit_log = output_audit_log["AUDIT"]
            self.assertEqual(audit_log["action"], "Update")
            self.assertEqual(audit_log["statuscode"], 200)
            self.assertEqual(audit_log["changelog"]["entity"], "Adjustment")
            self.assertEqual(audit_log["changelog"]["changes"], changes)

        kafka_mock.assert_awaited_once_with(RF_SYSTEM_EVENTS, message)
        notification_mock.assert_awaited_once_with(
            context={"headers": request.headers},
            topic=ADJUSTMENT_UPDATED_TOPIC,
            data={"record_hash": data["record_hash"], "adjustment_id": uuid.UUID(resp.json["id"]), }
        )
        self.assertEqual(request.json["record_hash"], data["record_hash"])
        self.assertEqual(resp.status, 200)
        self.assertEqual(list(resp.json.keys()), AdjustmentMock.adjustment_fields)
        self.assertEqual(resp.json["adjustment_value"], data["adjustment_value"])
        self.assertEqual(resp.json["tier_override"], data["tier_override"])
        self.assertEqual(resp.json["comment"], data["comment"])
        self.assertEqual(resp.json["status"], AdjustmentStatuses.not_applied.value)
        self.assertEqual(resp.json["user"], resp.json["user"])
        self.assertEqual(
            resp.json["user_full_name"],
            f"{UserObjectMock.registry_data['profile']['firstName']} "
            f"{UserObjectMock.registry_data['profile']['lastName']}"
        )

    def test_update_tier_override(self, kafka_mock, notification_mock):
        changes = [{"field": "tier_id", "oldvalue": "6786", "newvalue": "1234"}]
        data = AdjustmentMock.update_tier_override_data
        message = {
            "client": BaseTestCase.app_client,
            "project_type": AdjustmentMock.project_registry_data["project_type"],
            "project_id": AdjustmentMock.project_registry_data["id"],
            "event": SYSTEM_EVENT_TIER_OVERRIDE
        }

        with self.assertLogs(AdjustmentMock.logger_name, level=AdjustmentMock.log_level) as cm:
            request, resp = self.test_client.put(
                f"{self.resource_url}/32d256ae-a704-4bd2-aa2a-085d34ae4d11",
                headers=self.headers,
                data=json.dumps(data)
            )
            output_audit_log = json.loads(cm.records[0].message)
            audit_log = output_audit_log["AUDIT"]
            self.assertEqual(audit_log["action"], "Update")
            self.assertEqual(audit_log["statuscode"], 200)
            self.assertEqual(audit_log["changelog"]["entity"], "Adjustment")
            self.assertEqual(audit_log["changelog"]["changes"], changes)

        kafka_mock.assert_awaited_once_with(RF_SYSTEM_EVENTS, message)
        notification_mock.assert_awaited_once_with(
            context={"headers": request.headers},
            topic=ADJUSTMENT_UPDATED_TOPIC,
            data={"record_hash": data["record_hash"], "adjustment_id": uuid.UUID(resp.json["id"])}
        )
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["tier_override"], data["tier_override"])
        self.assertEqual(list(resp.json.keys()), AdjustmentMock.adjustment_fields)
        self.assertEqual(resp.json["status"], AdjustmentStatuses.not_applied.value)

    def test_update_not_existing_tier_override(self, kafka_mock, notification_mock):
        data = AdjustmentMock.update_not_existing_tier_override_data
        resp = self.test_client.put(
            f"{self.resource_url}/32d256ae-a704-4bd2-aa2a-085d34ae4d99",
            headers=self.headers,
            data=json.dumps(data),
            gather_request=False
        )

        self.assertEqual(resp.status, 404)

    def test_manual_override_empty_strings_are_treated_as_nulls(self, kafka_mock, notification_mock):
        changes = [{"field": "adjustment_value", "oldvalue": "\"200\"", "newvalue": "\"0\""}]
        data = AdjustmentMock.create_manual_override_data
        data.update({
            "product_uuid": "",
            "bu_uuid": "",
        })

        with self.assertLogs(AdjustmentMock.logger_name, level=AdjustmentMock.log_level) as cm:
            resp = self.test_client.post(
                self.resource_url, headers=self.headers, data=json.dumps(data), gather_request=False
            )

            output_audit_log = json.loads(cm.records[0].message)
            audit_log = output_audit_log["AUDIT"]
            self.assertEqual(audit_log["action"], "Update")
            self.assertEqual(audit_log["statuscode"], 200)
            self.assertEqual(audit_log["changelog"]["entity"], "Adjustment")
            self.assertEqual(audit_log["changelog"]["changes"], changes)

        self.assertEqual(resp.status, 201)
        self.assertEqual(resp.json["product_uuid"], None)
        self.assertEqual(resp.json["bu_uuid"], None)


class TestSmokeResources(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.resource_url = f"{cls.base_url}/smoke"

    @property
    def test_client(self):
        return self.create_app().test_client

    def test_access_control_allow_methods(self):
        resp = self.test_client.get(
            self.resource_url, headers=self.headers, gather_request=False
        )

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json, {"hello": "world"})


class TestAdjustmentsResources(BaseTestCase):

    @property
    def test_client(self):
        return self.create_app().test_client

    def test_create_adjustment_missing_required_field(self):
        data = {
            "product_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d55",
            "bu_uuid": "b5cd5ce6-4c46-4e6d-1111-7df38fdd7d55",
            "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
            "comment": "Changed rebate to make more profit",
            "price_group_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d77"
        }
        resp = self.test_client.post(f"{self.base_url}/adjustments/",
                                     headers=self.headers, data=json.dumps(data),
                                     gather_request=False)
        self.assertEqual(resp.status, 422)

    @patch("service_api.resources.adjustment_resources._validate_user_permission", new=CoroutineMock())
    @patch(
        "rfcommon_api.common.domain.user.UserObject.get_user_data",
        new=CoroutineMock(return_value=UserObjectMock.registry_data)
    )
    def test_get_all_adjustments(self):
        params = {"page": 1}
        resp = self.test_client.get(f'{self.base_url}/adjustments',
                                    headers=self.headers,
                                    params=params,
                                    gather_request=False)

        self.assertEqual(resp.status, 200)

    @patch("rfcommon_api.common.domain.user.UserObject.get_user_data",
           CoroutineMock(return_value=UserObjectMock.registry_data))
    def test_get_adjustment(self):
        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df2",
                                    headers=self.headers,
                                    gather_request=False)

        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json["id"], "32d256ae-a704-4bd2-aa2a-085d34ae4df2")

    def test_get_not_existing_adjustment(self):
        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df1",
                                    headers=self.headers,
                                    gather_request=False)

        self.assertEqual(resp.status, 404)

    @patch("service_api.resources.adjustment_resources._validate_user_permission", new=CoroutineMock())
    def test_update_not_existing_adjustments(self):
        data = {
            "adjustment_value": 999999.00,
            "comment": "Update rebate to make more profit!!!",
            "record_hash": "record_hash"
        }
        resp = self.test_client.put(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df1",
                                    headers=self.headers,
                                    data=json.dumps(data),
                                    gather_request=False)

        self.assertEqual(resp.status, 404)

    @patch("service_api.resources.adjustment_resources._validate_user_permission", new=CoroutineMock())
    def test_apply_adjustment(self):
        data = {"project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d53"}
        resp = self.test_client.post(f"{self.base_url}/mark_adjustments_as_applied/",
                                     headers=self.headers, data=json.dumps(data),
                                     gather_request=False)
        self.assertEqual(resp.status, 200)
        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df3",
                                    headers=self.headers,
                                    gather_request=False)
        self.assertEqual(resp.json["status"], AdjustmentStatuses.applied.value)

    @patch("service_api.resources.adjustment_resources._validate_user_permission", new=CoroutineMock())
    def test_delete_not_applied_adjustment(self):
        data = {
            "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d54",
        }
        resp = self.test_client.post(f"{self.base_url}/delete_not_applied_overrides/",
                                     headers=self.headers, data=json.dumps(data),
                                     gather_request=False)
        self.assertEqual(resp.status, 200)

        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df4",
                                    headers=self.headers,
                                    gather_request=False)
        self.assertEqual(resp.status, 404)
        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df5",
                                    headers=self.headers,
                                    gather_request=False)
        self.assertEqual(resp.status, 404)
        resp = self.test_client.get(f"{self.base_url}/adjustments/32d256ae-a704-4bd2-aa2a-085d34ae4df6",
                                    headers=self.headers,
                                    gather_request=False)
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.json['status'], AdjustmentStatuses.applied.value)

    def test_remove_deprecated_adjustments(self):
        data = {"project_uuid": "aa2bd902-34ef-43ea-a13a-5e983ed72830"}
        resp = self.test_client.post(
            f"{self.base_url}/remove_deprecated_adjustments",
            headers=self.headers,
            data=json.dumps(data),
            gather_request=False
        )
        actual_adjustment = self.test_client.get(
            f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b73",
            headers=self.headers,
            gather_request=False
        )
        first_deprecated_adjustment = self.test_client.get(
            f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b71",
            headers=self.headers,
            gather_request=False
        )
        second_deprecated_adjustment = self.test_client.get(
            f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b72",
            headers=self.headers,
            gather_request=False
        )
        not_applied_adjustment = self.test_client.get(
            f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b74",
            headers=self.headers,
            gather_request=False
        )

        self.assertEqual(resp.status, 200)
        self.assertEqual(actual_adjustment.status, 404)
        self.assertEqual(first_deprecated_adjustment.status, 404)
        self.assertEqual(second_deprecated_adjustment.status, 404)
        self.assertEqual(not_applied_adjustment.status, 200)
        self.assertEqual(not_applied_adjustment.json["status"], AdjustmentStatuses.not_applied.value)

    def test_remove_deprecated_adjustments_no_not_applied(self):
        actual_adjustment = self.test_client.get(f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b75",
                                                 headers=self.headers,
                                                 gather_request=False
                                                 )

        self.assertEqual(actual_adjustment.status, 200)
        self.assertEqual(actual_adjustment.json["status"], AdjustmentStatuses.applied.value)

        data = {"project_uuid": "aa2bd902-34ef-43ea-a13a-5e983ed72831"}
        resp = self.test_client.post(f"{self.base_url}/remove_deprecated_adjustments",
                                     headers=self.headers,
                                     data=json.dumps(data),
                                     gather_request=False)
        # this adjustment should not be removed from DB
        actual_adjustment = self.test_client.get(f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b75",
                                                 headers=self.headers,
                                                 gather_request=False)

        self.assertEqual(resp.status, 200)
        self.assertEqual(actual_adjustment.status, 200)
        self.assertEqual(actual_adjustment.json["status"], AdjustmentStatuses.applied.value)

    def test_remove_deprecated_adjustments_no_applied(self):
        data = {"project_uuid": "aa2bd902-34ef-43ea-a13a-5e983ed72832"}
        resp = self.test_client.post(f"{self.base_url}/remove_deprecated_adjustments",
                                     headers=self.headers,
                                     data=json.dumps(data),
                                     gather_request=False)
        actual_adjustment = self.test_client.get(f"{self.base_url}/adjustments/613197bd-0e33-4ff9-80a8-d4114a210b76",
                                                 headers=self.headers,
                                                 gather_request=False)

        self.assertEqual(resp.status, 200)
        self.assertEqual(actual_adjustment.status, 200)
        self.assertEqual(actual_adjustment.json["status"], AdjustmentStatuses.not_applied.value)

    def test_get_project_adjustments(self):
        resp = self.test_client.get(
            f"{self.base_url}/project_adjustments/aa2bd902-34ef-43ea-a13a-5e983ed72832",
            headers=self.headers,
            gather_request=False
        )
        self.assertEqual(resp.status, 200)

        # there should be adjustment with latest date in group
        latest_adjustment = self.test_client.get(
            f"{self.base_url}/project_adjustments/b1673d2f-ab28-448b-9722-c81e118c018b",
            headers=self.headers,
            gather_request=False
        )

        self.assertEqual(latest_adjustment.status, 200)
        self.assertEqual(len(latest_adjustment.json), 1)

        self.assertEqual(latest_adjustment.json[0]["updated_at"], "2018-10-26T11:11:43.231740")

        # there should be list of adjustments  with latest date in every group
        latest_adjustments = self.test_client.get(
            f"{self.base_url}/project_adjustments/387bc469-2c73-4d48-9f1f-490ee8f915b9",
            headers=self.headers,
            gather_request=False
        )
        self.assertEqual(latest_adjustments.status, 200)
        self.assertEqual(latest_adjustments.json[0]["updated_at"], "2018-07-26T11:11:43.231740")
        self.assertEqual(latest_adjustments.json[1]["updated_at"], "2018-07-30T11:11:43.231740")

    def test_get_project_adjustments_from_not_existing_project(self):
        no_existing_adjustments = self.test_client.get(
            f"{self.base_url}/project_adjustments/b5cd5ce6-4c46-4e6d-a67d-7df38fd4rt75",
            headers=self.headers,
            gather_request=False
        )
        self.assertEqual(no_existing_adjustments.status, 404)


@patch("service_api.domain.adjustment.KafkaProducer.publish", CoroutineMock())
@patch("service_api.resources.adjustment_resources.log_audit_overrides", CoroutineMock())
@patch("rfcommon_api.common.services.rest_client.notification.NotificationRESTClient.send_notification",
       CoroutineMock())
@patch("rfcommon_api.common.services.rest_client.projects.ProjectsRESTClient.get_project",
       side_effect=CoroutineMock(return_value=AdjustmentMock.project_registry_data))
@patch("rfcommon_api.common.domain.user.UserObject.get_user_data",
       side_effect=CoroutineMock(return_value=UserObjectMock.registry_data))
class TestAdjustmentPermissions(BaseTestCase):

    @property
    def test_client(self):
        return self.create_app().test_client

    @property
    def resource_url(self):
        return f"{self.base_url}/adjustments"

    def test_manual_override_having_permissions(self, get_user_data_mock, get_project_registry_mock):
        response = self.test_client.post(
            self.resource_url,
            headers=self.headers,
            gather_request=False,
            data=json.dumps(AdjustmentMock.create_manual_override_data)
        )

        self.assertEqual(response.status, 201)

    def test_manual_override_with_unassigned_user(self, get_user_data_mock, get_project_registry_mock):
        user_data = deepcopy(UserObjectMock.registry_data)
        user_data["profile"]["login"] = "unassigned_user@somedomain.com"

        get_user_data_mock.side_effect = CoroutineMock(return_value=user_data)
        response = self.test_client.post(
            self.resource_url,
            headers=self.headers,
            gather_request=False,
            data=json.dumps(AdjustmentMock.create_manual_override_data)
        )

        self.assertEqual(response.status, 403)
        self.assertIn("error_message", response.json)
        self.assertEqual(response.json["error_message"], "User not assigned to the project")

    def test_manual_override_on_not_allowed_step(self, get_user_data_mock, get_project_registry_mock):
        project_data = deepcopy(AdjustmentMock.project_registry_data)
        project_data["workflow_step"] = "manager_review"

        get_project_registry_mock.side_effect = CoroutineMock(return_value=project_data)
        response = self.test_client.post(
            self.resource_url,
            headers=self.headers,
            gather_request=False,
            data=json.dumps(AdjustmentMock.create_manual_override_data)
        )

        self.assertEqual(response.status, 422)
        self.assertIn("error_message", response.json)
        self.assertEqual(
            response.json["error_message"], "Cant create or update adjustment on current project workflow step"
        )

    def test_manual_override_on_not_allowed_substep(self, get_user_data_mock, get_project_registry_mock):
        project_data = deepcopy(AdjustmentMock.project_registry_data)
        project_data["workflow_substep"] = ["pending_calculation"]

        get_project_registry_mock.side_effect = CoroutineMock(return_value=project_data)

        response = self.test_client.post(
            self.resource_url,
            headers=self.headers,
            gather_request=False,
            data=json.dumps(AdjustmentMock.create_manual_override_data)
        )

        self.assertEqual(response.status, 422)
        self.assertIn("error_message", response.json)
        self.assertEqual(
            response.json["error_message"], "Cant create or update adjustment on current project workflow step"
        )


class TestAdjustmentResourceFilters(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        cls.resource_url = f"{cls.base_url}/adjustments"

    @property
    def test_client(self):
        return self.create_app().test_client

    def test_filter_by_project_uuid(self):
        filter_params = "filter=project_uuid eq b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d54"
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 3)

    def test_filter_by_price_group_uuid(self):
        filter_params = "filter=price_group_uuid eq b5cd5ce6-4c46-1111-a67d-7df38fdd7d71"
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 6)

    def test_filter_by_bu_uuid(self):
        filter_params = "filter=bu_uuid eq 4e573553-53d0-46c6-b928-1e2434e87f91"
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 6)

    def test_filter_by_product_uuid(self):
        filter_params = "filter=product_uuid eq 7b69c8bf-b3c1-4a19-a7cd-654cc11ae9d5"
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 2)

    def test_filter_by_project_and_bu_uuids(self):
        filter_params = (
            "filter=bu_uuid eq 4e573553-53d0-46c6-b928-1e2434e87f91&"
            "filter=project_uuid eq aa2bd902-34ef-43ea-a13a-5e983ed72831"
        )
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 1)

    def test_filter_by_price_group_project_product_uuids(self):
        filter_params = (
            "filter=project_uuid eq 387bc469-2c73-4d48-9f1f-490ee8f915b9&"
            "filter=bu_uuid eq b5ccf502-3c3b-4a30-a180-c8d6b5573e9f&"
            "filter=product_uuid eq e6f799e8-c321-4f98-8f02-28775070f8d0"
        )
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 1)

    def test_filter_by_project_price_group_product_uuids(self):
        filter_params = (
            "filter=project_uuid eq b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d51&"
            "filter=price_group_uuid eq 321ec97e-88ca-4a6f-b8e3-28f5c77fb7d3&"
            "filter=product_uuid eq b5cd5ce6-4c46-1111-a67d-7df38fdd7d51"
        )
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 200)
        self.assertEqual(len(response.json), 1)

    def test_filter_with_unknown_parameter(self):
        incorrect_parameter = "bu_uid"
        filter_params = "filter={} eq 4e573553-53d0-46c6-b928-1e2434e87f91".format(incorrect_parameter)
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 500)
        self.assertEqual(response.json, {
            "error_message": f"Specified column [{incorrect_parameter}] was not found among possible ones."})

    def test_filter_with_incorrect_parameter_type(self):
        incorrect_parameter = "tier_override"
        type_of_parameter = "JSONB"
        filter_params = "filter={} eq 4e573553-53d0-46c6-b928-1e2434e87f91".format(incorrect_parameter)
        url = f"{self.resource_url}?{filter_params}"

        response = self.test_client.get(url, headers=self.headers, gather_request=False)

        self.assertEqual(response.status, 500)
        self.assertEqual(response.json, {
            "error_message": f"Sorting and filtering for column [{incorrect_parameter}] of type "
                             f"[{type_of_parameter}] is not supported"})
