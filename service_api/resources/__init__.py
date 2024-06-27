"""This module contains basic classes for configuring service and test if service is available."""

from sanic.response import json
from sanic.views import HTTPMethodView

from service_api.services.decorators import register_engine, requires_auth, populate_request


class BaseResource(HTTPMethodView):
    """Sets needed decorators which will used in other classes with endpoints."""
    decorators = [register_engine, requires_auth, populate_request]


class SmokeResources(BaseResource):
    """Class for checking if service is available."""
    # NOTE: for SmokeResources no interaction with DB should be done, so
    #       removing `register_engine` decorator from the base class
    decorators = set(BaseResource.decorators).remove(register_engine)

    async def get(self, *args, **kwargs):
        """Simple test."""
        return json({"hello": "world"})
