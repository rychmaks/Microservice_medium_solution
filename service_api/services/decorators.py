"""This module contains all needed basic decorators.

The wrappers are simple request and response objects which you can subclass to do whatever you want them to do.
The request object contains the information transmitted by the client and the response object contains all the
information sent back to the browser.

"""

from functools import wraps

from service_api.services.database import get_engine
from service_api.constants import COMMON_DB
from rfcommon_api.common.domain.user import UserObject


def register_engine(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Wrapper for creating in request new key: `db_engine`.

        This wrapper is used for creating in request new key: `db_engine`,
        which contains information about instance of Engine which used.

        Args:
            request (Request): request.
            args (tuple): parameters which send to `func`.
            kwargs (dict): parameters which send to `func`.

        Returns:
            Result of `func` execution.

        """
        request["db_engine"] = await get_engine(client=request.headers.get("X-Client", COMMON_DB))
        response = await func(request, *args, **kwargs)
        return response

    return wrapper


def requires_auth(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        """Check whether user is authorized to use an endpoint in a web application.

        If user not authorized `session_id` set to None.

        Args:
            request (Request): request.
            args (tuple): parameters which send to `func`.
            kwargs (dict): parameters which send to `func`.

        Returns:
            Result of `func` execution.

        Raises:
             IndexError: Raised when a sequence subscript is out of range.
             KeyError: Raised when tries to access a key that isn’t in a dictionary in `request`.

        """
        try:
            request["session_id"] = request.headers["Authorization"].split(" ")[1]
        except (IndexError, KeyError):
            request["session_id"] = None
        response = await func(request, *args, **kwargs)
        return response

    return wrapper


def populate_request(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        """This wrapper is used for creating in request two new keys: `current_user` and `req_headers`.

        Key `req_headers` contains information about X-Client, authorization, x-timezone.

        Args:
            request (Request): request.
            args (tuple): parameters which send to `func`.
            kwargs (dict): parameters which send to `func`.

        Returns:
            Result of `func` execution.

        """
        headers = {
            'X-Client': request.headers.get('X-Client'),
            'Authorization': request.headers.get('Authorization'),
            'x-timezone': request.headers.get('x-timezone', 'UTC')
        }
        request['req_headers'] = headers
        request['current_user'] = UserObject(headers)

        response = await func(request, *args, **kwargs)
        return response

    return wrapper
