"""This module defines the service routing system."""

from sanic import Blueprint
from sanic.app import Sanic


def load_api(app: Sanic):
    """This function contains URL template.

    A set of mappings of processing functions to specific query strings.

    """
    from service_api.resources import SmokeResources
    from service_api.resources.base_keyspace import KeyspaceResource
    from service_api.resources.adjustment_resources import AdjustmentsResource
    from service_api.resources.adjustment_resources import AdjustmentResource
    from service_api.resources.adjustment_resources import DeleteNotAppliedAdjustments
    from service_api.resources.adjustment_resources import ApplyAdjustment
    from service_api.resources.adjustment_resources import RemoveDeprecatedAdjustments
    from service_api.resources.arrangement_resources import TierOverride
    from service_api.resources.adjustment_resources import GetProjectAdjustments

    api_prefix = "/{service_name}/v1".format(service_name=app.config.get("SERVICE_NAME"))
    api_v1 = Blueprint("v1", url_prefix=api_prefix)

    api_v1.add_route(SmokeResources.as_view(), "/smoke", strict_slashes=False)
    api_v1.add_route(KeyspaceResource.as_view(), "/keyspaces", strict_slashes=False)
    api_v1.add_route(AdjustmentsResource.as_view(), "/adjustments/", strict_slashes=False)
    api_v1.add_route(AdjustmentResource.as_view(), "/adjustments/<adjustment_id:uuid>", strict_slashes=False)
    api_v1.add_route(DeleteNotAppliedAdjustments.as_view(), "/delete_not_applied_overrides/", strict_slashes=False)
    api_v1.add_route(ApplyAdjustment.as_view(), "/mark_adjustments_as_applied/", strict_slashes=False)
    api_v1.add_route(RemoveDeprecatedAdjustments.as_view(), "/remove_deprecated_adjustments/", strict_slashes=False)
    api_v1.add_route(TierOverride.as_view(), "/tier_override/<project_id:uuid>", strict_slashes=False)
    api_v1.add_route(GetProjectAdjustments.as_view(), "/project_adjustments/<project_id:uuid>", strict_slashes=False)
    app.blueprint(api_v1)
