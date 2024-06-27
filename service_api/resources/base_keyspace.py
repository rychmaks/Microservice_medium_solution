"""This module contains endpoint for key space resources."""

from http import HTTPStatus

from rfcommon_api.common.reqresp import map_response
from sanic.response import json
from sanic.views import HTTPMethodView

from service_api.domain import keyspace
from service_api.services.forms import ClientKeyspaceCreateForm


class KeyspaceResource(HTTPMethodView):
    """This class contains method which is endpoint for creating database."""

    async def post(self, request):
        """Creates a database.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            HTTP status code 200 and message that database exist
            or HTTP status code 201 and message with information that database was created,
            if such database wasn't exist.

        Example:
            .. include:: /endpoints_examples/keyspace_resource_post.txt

        """
        data, _ = ClientKeyspaceCreateForm().load(request.json)
        client_name = data["client_short_name"]

        # We put single database IP, but when it would be array please change row below.
        host = data["hosts"]
        is_created, message = await keyspace.create_client(host, client_name)
        return json(
            map_response({'headers': request.headers}, {"message": message}),
            HTTPStatus.CREATED.value if is_created else HTTPStatus.OK.value)
