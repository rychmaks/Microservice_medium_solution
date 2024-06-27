"""Initialises sessions, users, projects, metadata, notifications, arrangements."""

from rfcommon_api.common.services.rest_client.base import RESTClientRegistry
from rfcommon_api.common.services.rest_client.session import SessionRESTClient
from rfcommon_api.common.services.rest_client.users import UsersRESTClient
from rfcommon_api.common.services.rest_client.projects import ProjectsRESTClient
from rfcommon_api.common.services.rest_client.metadata import MetadataRESTClient
from rfcommon_api.common.services.rest_client.notification import NotificationRESTClient
from rfcommon_api.common.services.rest_client.arrangment import ArrangementsRESTClientV2

__all__ = ("RESTClientRegistry",)

# Implicitly creates "cached_{client_name}" version of regular RESTClient
RESTClientRegistry.register("sessions", SessionRESTClient)
RESTClientRegistry.register("users", UsersRESTClient)
RESTClientRegistry.register("projects", ProjectsRESTClient)
RESTClientRegistry.register("metadata", MetadataRESTClient)
RESTClientRegistry.register("notifications", NotificationRESTClient)
RESTClientRegistry.register("arrangements", ArrangementsRESTClientV2)
