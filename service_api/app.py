"""Module which execute needed operations before server start and after server stop."""

from sanic.app import Sanic
from sanic_cors import CORS

from rfcommon_api.common.domain.user import UserObject
from service_api.constants import DEFAULT_SERVICE_NAME
from service_api import api_v1
from service_api.config import runtime_config
from service_api.services import database
from rfcommon_api.common import cache_manager
from rfcommon_api.common.services import logger
from service_api.services.rest_client import RESTClientRegistry
from rfcommon_api.common.exceptions import setup_exception_handler


app = Sanic(DEFAULT_SERVICE_NAME)
app.config.from_object(runtime_config())

cors = CORS(
    app,
    resources={r"*": {"origin": "*"}},
    expose_headers=[
        "Link, X-Pagination-Current-Page",
        "X-Pagination-Per-Page",
        "X-Pagination-Total-Count",
        "X-Client",
        "Authorization",
        "Content-Type",
        "X-Filename",
    ],
)

api_v1.load_api(app)
logger.register_server(app=app)
setup_exception_handler(app)
database.register_server(app=app)


@app.listener("before_server_start")
async def before_server_start(app, loop):
    """Initializing client of service and RedisCacheManager for app.

    RedisCacheManager by default saves the keys directly,
    without appending a prefix (which acts as a namespace) before server start.

    Args:
        app (Sanic): Sanic instance of service.
        loop (Loop): Reference to loop.

    """
    RESTClientRegistry.init(cache_manager.RedisCacheManager)
    UserObject.init(RESTClientRegistry)


@app.listener("after_server_stop")
async def after_server_stop(app, loop):
    """Release engines and close RedisCacheManager after server stop.

    Args:
        app (Sanic): Sanic instance of service.
        loop (Loop): Reference to loop.

    """
    await database.release_engines()
    await cache_manager.RedisCacheManager.close()
