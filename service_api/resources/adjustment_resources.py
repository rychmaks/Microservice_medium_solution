"""This module contains endpoints for adjustments."""

from rfcommon_api.common.domain.user import UserObject
from rfcommon_api.common.exceptions import PermissionDenied, UnprocessibleEntity
from rfcommon_api.common.paginators import PaginationSchema, Pagination
from rfcommon_api.common.reqresp import map_response
from sanic.response import json

from service_api.constants import (
    WORKFLOW_STEP_ANALYST_REVIEW, WORKFLOW_SUBSTEP_ADJUSTMENTS, ADJUSTMENT_UPDATED_TOPIC
)
from service_api.domain.adjustment import (
    create_adjustment,
    get_adjustment_by_id,
    update_adjustment,
    delete_not_applied_adjustments,
    apply_adjustments,
    get_adjustments,
    remove_deprecated_adjustments,
    get_project_adjustments,
    log_audit_overrides
)
from service_api.resources import BaseResource
from service_api.services.forms import (
    CreateAdjustmentForm, UpdateAdjustmentForm, AppliedAdjustmentsForm, AdjustmentFilteringSchema
)
from service_api.services.rest_client import RESTClientRegistry


class AdjustmentsResource(BaseResource):
    """This class contains methods which are endpoints for getting and creating adjustments."""

    async def get(self, request):
        """Returns adjustments and sets into headers data about pagination.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            List with information about adjustments, HTTP status code 200 and headers with such parameters as
            `X-Pagination-Current-Page`, `X-Pagination-Per-Page`, `X-Pagination-Total-Count`.

        Example:
            .. include:: /endpoints_examples/adjustments_resource_get.txt

        """
        params, _ = AdjustmentFilteringSchema().load(dict(request.args))
        paging, _ = PaginationSchema().load(request.args)
        adjustments, count = await get_adjustments(request["db_engine"], params, paging)
        paginator = Pagination(total_count=count,
                               url=request.url,
                               page=paging['page'],
                               per_page=paging['per_page'])

        return json(map_response(request, adjustments), status=200, headers=paginator.pagination_headers())

    async def post(self, request):
        """Creates new adjustment.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            All information about new adjustment and HTTP status code 201.

        Example:
            .. include:: /endpoints_examples/adjustments_resource_post.txt

        """
        data, _ = CreateAdjustmentForm().load(request.json)
        await _validate_user_permission(data.get('project_uuid'), request.get('req_headers'), request['current_user'])
        record_hash = data.pop('record_hash', None)
        context = {'headers': request.headers}

        new_adjustment = await create_adjustment(
            request.get('db_engine'), request['current_user'], data, request['req_headers']
        )

        await log_audit_overrides(data, new_adjustment, request.headers)

        if record_hash:
            notification_cli = RESTClientRegistry.get('notifications')
            await notification_cli.send_notification(
                context=context,
                topic=ADJUSTMENT_UPDATED_TOPIC,
                data={'record_hash': record_hash, 'adjustment_id': new_adjustment.get('id')}
            )
        return json(map_response(request, new_adjustment), 201)


class AdjustmentResource(BaseResource):
    """This class contains methods which are endpoints for getting and creating adjustment with specified id."""

    async def get(self, request, adjustment_id):
        """Returns adjustment with specified id.

        Args:
            request: Instance of sanic.request.Request class.
            adjustment_id: id of adjustment.

        Returns:
            HTTP status code 200 and dict with information about adjustment with specified id.

        Example:
            .. include:: /endpoints_examples/adjustment_resource_get.txt

        """
        adjustment = await get_adjustment_by_id(request.get('db_engine'), adjustment_id)
        return json(map_response(request, dict(adjustment)), 200)

    async def put(self, request, adjustment_id):
        """Updates adjustment with specified id.

        Args:
            request: Instance of sanic.request.Request class.
            adjustment_id: id of adjustment.

        Returns:
            HTTP status code 200 and dict with information about adjustment which was updated.

        Example:
            .. include:: /endpoints_examples/adjustment_resource_put.txt


        """
        data, _ = UpdateAdjustmentForm().load(request.json)
        record_hash = data.pop('record_hash', None)
        project_id = dict(await get_adjustment_by_id(request.get('db_engine'), adjustment_id)).get('project_uuid')
        await _validate_user_permission(project_id, request.get('req_headers'), request['current_user'])

        new_adjustment = await update_adjustment(
            request.get('db_engine'), adjustment_id, data, request['current_user'], request['req_headers']
        )

        await log_audit_overrides(data, new_adjustment, request.headers)

        if record_hash:
            notification_cli = RESTClientRegistry.get('notifications')
            await notification_cli.send_notification(
                context={'headers': request.headers},
                topic=ADJUSTMENT_UPDATED_TOPIC,
                data={'record_hash': record_hash, 'adjustment_id': new_adjustment['id']}
            )
        return json(map_response(request, dict(new_adjustment)), 200)


class DeleteNotAppliedAdjustments(BaseResource):
    """This class contains method which is endpoint for deleting not applied adjustments."""

    async def post(self, request):
        """Deletes not applied adjustments.

        This method deletes adjustments which wasn't applied in project.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            Message that not applied adjustments have been deleted and HTTP status code 200.

        Example:
            .. include:: /endpoints_examples/delete_not_applied_adjustments_post.txt

        """
        data, _ = AppliedAdjustmentsForm().load(request.json)
        await delete_not_applied_adjustments(request.get('db_engine'), data)
        return json({"message": "Not applied adjustments have been deleted"}, 200)


class ApplyAdjustment(BaseResource):
    """This class contains method which is endpoint for applying not applied adjustments."""

    async def post(self, request):
        """Applies adjustments for project.

        This method applies adjustments with status 'Not Applied' for project.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            Message that not applied adjustments have been applied and HTTP status code 200.

        Example:
            .. include:: /endpoints_examples/apply_adjustment_post.txt

        """
        data, _ = AppliedAdjustmentsForm().load(request.json)
        await apply_adjustments(request.get('db_engine'), data)
        return json({"message": "Adjustments have been applied"}, 200)


class RemoveDeprecatedAdjustments(BaseResource):
    """This class contains method which is endpoint for deleting deprecated adjustments."""

    async def post(self, request):
        """Removes deprecated adjustments.

        This method deletes applied adjustment if for the same combination of
        project_uuid, price_group_uuid, bu_uuid and product_uuid exist adjustment with status 'Not Applied'.

        Args:
            request: Instance of sanic.request.Request class.

        Returns:
            Message that deprecated adjustments have been removed and HTTP status code 200.

        Example:
            .. include:: /endpoints_examples/remove_deprecated_adjustments_post.txt

        """

        data, _ = AppliedAdjustmentsForm().load(request.json)
        await remove_deprecated_adjustments(request.get('db_engine'), data)
        return json({"message": "Deprecated adjustments have been removed"}, 200)


class GetProjectAdjustments(BaseResource):
    """This class contains method which is endpoint for getting project adjustments."""

    async def get(self, request, project_id):
        """Returns adjustments for specified project.

        Args:
            request: Instance of sanic.request.Request class.
            project_id: id of project.

        Returns:
            All information about adjustments for specified project and HTTP status code 200.

        Example:
            .. include:: /endpoints_examples/get_project_adjustments_get.txt

        """
        project_adjustments = await get_project_adjustments(request.get('db_engine'), project_id)
        return json(map_response(request, project_adjustments), 200)


async def _validate_user_permission(project_id: str, headers: dict, user_obj: UserObject):
    """Validates user permission.

    Args:
        project_id: id of project.
        headers: Store information about `X-Client`, `Authorization` and `x-timezone`.
        user_obj: user object.

    Raises:
        UnprocessibleEntity: Raised if can't create or update adjustment on current project workflow step.
        PermissionDenied: Raised if user doesn't assigned to the project.

    """
    projects = RESTClientRegistry.get('projects')
    project_data = await projects.get_project(headers, project_id)
    if project_data.get(
            'workflow_step'
    ) != WORKFLOW_STEP_ANALYST_REVIEW or WORKFLOW_SUBSTEP_ADJUSTMENTS not in project_data.get(
        'workflow_substep'
    ):
        raise UnprocessibleEntity("Cant create or update adjustment on current project workflow step")
    user_data = await user_obj.get_user_data()
    if project_data['assignee'] != user_data['profile']['login']:
        raise PermissionDenied('User not assigned to the project')
