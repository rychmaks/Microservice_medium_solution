"""This module contains endpoint for tier override."""

from rfcommon_api.common.reqresp import map_response
from sanic.response import json

from service_api.domain.arrangement import get_tiers
from service_api.resources import BaseResource
from service_api.services.forms import TierOverrideFilteringSchema


class TierOverride(BaseResource):
    """This class contains method which is endpoint for getting info about tier override."""

    async def get(self, request, project_id):
        """Gets information about tier override.

        Args:
             request: Instance of sanic.request.Request class.
             project_id: Id of project.

        Returns:
             Information about tiers override which are available and HTTP status code 200.

        Example:
            .. include:: /endpoints_examples/tier_override_get.txt

        """
        params, _ = TierOverrideFilteringSchema().load(dict(request.args))
        tiers = await get_tiers(headers=request['req_headers'], params=params)
        return json(map_response(request, tiers), status=200)
