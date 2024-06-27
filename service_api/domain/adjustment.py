"""Provide all needed functionality for work with adjustments.

This module contains all needed functionality for work with adjustments: create adjustment, get adjustment by id,
update adjustment, delete not applied adjustments, apply adjustments, get adjustments, remove deprecated adjustments,
get project adjustments.

"""

from aiopg.sa import Engine
from aiopg.transaction import Transaction, IsolationLevel
from multidict import CIMultiDict

from rfcommon_api.common.exceptions import NotFoundException
from service_api.services.rest_client import RESTClientRegistry
from rfcommon_api.common.constants import AuditLogActions
from rfcommon_api.common.utils import asyncio_task
from rfcommon_api.common.services.rest_client.projects import ProjectNotFound
from rfcommon_api.common.services.audit_logger import log_audit_message, create_changelog
from service_api.models import Adjustments
from service_api.services.forms import AdjustmentStatuses
from sqlalchemy.sql import select, and_, or_, exists, func
from rfcommon_api.common.services import query_manager
from rfcommon_api.common.domain.user import UserObject
from rfcommon_api.common.services.kafka import KafkaProducer
from service_api.constants import RF_SYSTEM_EVENTS, SYSTEM_EVENT_AMOUNT_OVERRIDE, SYSTEM_EVENT_TIER_OVERRIDE


async def create_adjustment(engine: Engine, user_obj: UserObject, data: dict, headers: dict) -> dict:
    """This function creates new adjustment.

    Args:
        engine: Instance which provides a source of database connectivity and behavior.
        user_obj: Instance which provide an information about the user.
        data: Dict which contains values for: uuid of product, comment, uuid of price group, uuid of bu,
              adjustment, tier override, uuid of project, total rebate amount and id.
        headers: Store information about `X-Client`, `Authorization` and `x-timezone`.

    Returns:
        Dictionary which contains such information about adjustment: id, uuid of project, uuid of price group,
        uuid of bu, uuid of product, adjustment value, tier override, comment, user mail, full name of user,
        status and when it was updated.

    """
    user_data = await user_obj.get_user_data()
    data['user_full_name'] = f"{user_data['profile'].get('firstName')} {user_data['profile'].get('lastName')}"
    data['status'] = AdjustmentStatuses.not_applied.value
    data['user'] = user_data['profile'].get('login')

    data = {column: value for column, value in data.items() if column in Adjustments.c.keys()}

    async with engine.acquire() as conn:
        await conn.execute(Adjustments.insert().values(**data))
        async with conn.execute(Adjustments.select().where(Adjustments.c.id == data['id'])) as cur:
            adjustment = await cur.fetchone()

        # Send warning
        event = SYSTEM_EVENT_AMOUNT_OVERRIDE if data.get('adjustment_value') is not None else SYSTEM_EVENT_TIER_OVERRIDE
        await _send_system_event(headers.get('X-Client'), data.get('project_uuid'), event)
        return dict(adjustment)


async def get_adjustment_by_id(engine: Engine, adjustment_id: str) -> dict:
    """This function gives information about adjustment with some id.

    Args:
        engine: Instance which provides a source of database connectivity and behavior.
        adjustment_id: Id of adjustment.

    Returns:
        Dictionary which contains such information about adjustment: id, uuid of project, uuid of price group,
        uuid of bu, uuid of product, adjustment value, tier override, comment, user mail, full name of user,
        status and when it was updated.

    Raises:
        NotFoundException: If adjustment with `adjustment_id` doesn't exist, will raise this exception.

    """
    async with engine.acquire() as conn:
        async with conn.execute(Adjustments.select().where(Adjustments.c.id == adjustment_id)) as cur:
            adjustment = await cur.fetchone()
        if not adjustment:
            raise NotFoundException(message="Adjustment not found.")
        return adjustment


async def update_adjustment(engine: Engine, adjustment_id: str, data: dict, user_obj: UserObject,
                            headers: dict) -> dict:
    """This function updates adjustment with id which is specified.

    Args:
        engine: Instance which provides a source of database connectivity and behavior.
        adjustment_id: Id of adjustment.
        data: dict which contains values for: Comment, adjustment value, tier override, total rebate amount.
        user_obj: Instance which provide an information about the user.
        headers: Store information about `X-Client`, `Authorization` and `x-timezone`.

    Returns:
        Dictionary which contains such information about adjustment: id, uuid of project, uuid of price group,
        uuid of bu, uuid of product, adjustment value, tier override, comment, user mail, full name of user,
        status and when it was updated.

    """
    user_data = await user_obj.get_user_data()
    async with engine.acquire() as conn:
        async with Transaction(conn, IsolationLevel.serializable, readonly=False, deferrable=False) as tr:
            async with tr.point():
                await conn.execute(
                    Adjustments.update(
                    ).where(
                        Adjustments.c.id == adjustment_id
                    ).values(
                        adjustment_value=data['adjustment_value'],
                        tier_override=data['tier_override'],
                        comment=data['comment'],
                        user=user_data['profile'].get('login'),
                        user_full_name=f"{user_data['profile'].get('firstName')} {user_data['profile'].get('lastName')}"
                    )
                )
        adjustment = await get_adjustment_by_id(engine, adjustment_id)
        # Send warning
        event = SYSTEM_EVENT_AMOUNT_OVERRIDE if data.get('adjustment_value') else SYSTEM_EVENT_TIER_OVERRIDE
        await _send_system_event(headers.get('X-Client'), adjustment.get('project_uuid'), event)
        return dict(adjustment)


async def delete_not_applied_adjustments(engine: Engine, data: dict):
    """Deletes not applied adjustments.

    This function deletes adjustments which wasn't applied for some project which has the same uuid as
    uuid of project in `data`.

    Args:
        engine: Instance which provides a source of database connectivity and behavior.
        data: Dict which contains value of uuid of project.

    """
    async with engine.acquire() as conn:
        async with Transaction(conn, IsolationLevel.serializable, readonly=False, deferrable=False) as tr:
            async with tr.point():
                await conn.execute(
                    Adjustments.delete(
                    ).where(and_(
                        Adjustments.c.project_uuid == data["project_uuid"],
                        Adjustments.c.status == AdjustmentStatuses.not_applied.value
                    )
                    )
                )


async def apply_adjustments(engine: Engine, data: dict):
    """Applies adjustments.

    This function applies adjustments with status 'Not Applied' for some project which has the same uuid as
    uuid of project in `data`.

    Args:
        engine: Instance which provide a source of database connectivity and behavior.
        data: Dict which contains value of uuid of project.

    """
    async with engine.acquire() as conn:
        async with Transaction(conn, IsolationLevel.serializable, readonly=False, deferrable=False) as tr:
            async with tr.point():
                await conn.execute(
                    Adjustments.update(
                    ).where(and_(
                        Adjustments.c.project_uuid == data["project_uuid"],
                        Adjustments.c.status != AdjustmentStatuses.applied.value
                    )
                    ).values(
                        status=AdjustmentStatuses.applied.value
                    )
                )


async def get_adjustments(engine: Engine, params, paging):
    """Gets all adjustments.

    This function gets all adjustments which satisfy filter. Maximum total count of adjustments which function can
    return is equal to `per_page` parameter.

    Args:
        engine: Instance which provides a source of database connectivity and behavior.
        params (dict): Dict which can contains parameters for filtering or sorting or logic.
        paging (dict): Dict which contains two keys: `page` and `per_page`.

    Returns:
        tuple: List of adjustments info and total count of adjustments.

    """
    query = select([Adjustments])
    query = query_manager.apply_filter(
        table=Adjustments,
        query=query,
        filters=params.get("filter"),
        sorting=params.get("sort"),
        logic=params.get("logic")
    )
    count_query = query_manager.apply_counts(query)
    if paging.get("page"):
        query = query_manager.apply_paging(query, paging)

    async with engine.acquire() as conn:
        adjustments = []
        async for row in await conn.execute(query):
            adjustments.append(dict(row))

        cur = await conn.execute(count_query)
        total_count = await cur.scalar()

    return adjustments, total_count


async def remove_deprecated_adjustments(engine: Engine, data: dict):
    """Removes deprecated adjustments.

    This function deletes applied adjustment if for the same combination of
    project_uuid, price_group_uuid, bu_uuid and product_uuid exist adjustment with status 'Not Applied'.

    Args:
        engine: Instance which provide a source of database connectivity and behavior.
        data: Dict which contains value of uuid of project.

    """
    adjustments1 = Adjustments.alias('adjustments1')

    delete_query = Adjustments.delete(
    ).where(
        and_(
            Adjustments.c.project_uuid == data['project_uuid'],
            Adjustments.c.status == AdjustmentStatuses.applied.value,
            exists(select([adjustments1.c.id]).where(
                and_(
                    Adjustments.c.project_uuid == adjustments1.c.project_uuid,
                    Adjustments.c.price_group_uuid == adjustments1.c.price_group_uuid,
                    or_(
                        Adjustments.c.bu_uuid == adjustments1.c.bu_uuid,
                        Adjustments.c.bu_uuid.is_(None)
                    ),
                    or_(
                        Adjustments.c.product_uuid == adjustments1.c.product_uuid,
                        Adjustments.c.product_uuid.is_(None)
                    ),
                    adjustments1.c.status == AdjustmentStatuses.not_applied.value
                )
            ))
        )
    )

    async with engine.acquire() as conn:
        async with Transaction(conn, IsolationLevel.serializable, readonly=False, deferrable=False) as tr:
            async with tr.point():
                await conn.execute(delete_query)


async def get_project_adjustments(engine: Engine, project_uuid: str) -> list:
    """Gives data of the latest adjustments.

    This function gives data of the latest adjustments for each combination
    of price_group_uuid, bu_uuid and product_uuid for particular project.

    Args:
        engine: Instance which provide a source of database connectivity and behavior.
        project_uuid: Project id.

    Returns:
        The latest adjustment for each combination of price_group_uuid, bu_uuid and product_uuid for particular project.

    """
    partitions_ordered_by_date = select(
        [
            Adjustments,
            func.row_number().over(
                partition_by=(
                    Adjustments.c.price_group_uuid,
                    Adjustments.c.bu_uuid,
                    Adjustments.c.product_uuid,
                    Adjustments.c.project_uuid
                ),
                order_by=Adjustments.c.updated_at.desc()).label('row_numb')
        ]
    ).alias('partitions_ordered_by_date')

    query = select([Adjustments]).where(
        and_(
            partitions_ordered_by_date.c.row_numb == 1,
            Adjustments.c.id == partitions_ordered_by_date.c.id,
            Adjustments.c.project_uuid == project_uuid
        )
    )
    async with engine.acquire() as conn:
        adjustments = []
        async for row in await conn.execute(query):
            adjustments.append(dict(row))
    return adjustments


async def _send_system_event(client, project_uuid, event):
    """This private method used for sending warnings about some event.

    Args:
        client (str): Name of client.
        project_uuid (UUID): Project id.
        event (str): Name of event, can be `amount_override` or `tier_override`.

    Raises:
        ProjectNotFound: If project with `project_uuid` does not exist, will raise this exception.

    """
    project_cli = RESTClientRegistry.get('projects')
    project = await project_cli.get_project({'X-Client': client}, project_uuid)
    if not project:
        raise ProjectNotFound("Project wasn't found")

    message = {
        'client': client,
        'project_type': project['project_type'],
        'project_id': project['id'],
        'event': event
    }
    await KafkaProducer.publish(RF_SYSTEM_EVENTS, message)


@asyncio_task
async def log_audit_overrides(request_payload, new_adjustment, headers):
    """This function used for creating information about adjustment changes.

    Args:
        request_payload (dict): Dict which includes all information about adjustment: amount of total rebate,uuid of bu,
                                uuid of price group, value of tier override and adjustment value, uuid of product and
                                uuid of project, comment which relates to adjustment, id of adjustment, user full name
                                and user email, status of adjustment.
        new_adjustment (dict): This parameter contains the same data as `request_payload`, difference between
                               this params is that instead of amount of total rebate `new_adjustment`
                               contains date of updating and `new_adjustment` has one more parameter: id of tier.
        headers (CIMultiDict): This parameter contains information about: connection, host, length of content, x-login,
                               accept-language, accept-encoding, x-client, user-agent, content-type, authorization,
                               x-projecttypes-group, x-timezone.

    """
    action = AuditLogActions.ACTION_UPDATE
    adjustment_value = 'adjustment_value'

    if new_adjustment[adjustment_value] is not None:
        log_message = 'Manual override'
        total_rebate_amount = 'total_rebate_amount'

        changelog_oldvalue = {
            adjustment_value: request_payload[total_rebate_amount],
        }
        changelog_newvalue = {
            adjustment_value: new_adjustment[adjustment_value],
        }

    else:
        log_message = 'Tier override'

        tier_id = 'tier_id'
        tier_override = 'tier_override'

        changelog_oldvalue = {
            tier_id: request_payload[tier_id],
        }
        changelog_newvalue = {
            tier_id: new_adjustment[tier_override][tier_id],
        }

    changelog = create_changelog(action, 'Adjustment', changelog_oldvalue, changelog_newvalue)

    await log_audit_adjustment(new_adjustment, action, log_message, changelog, headers,
                               request_payload.get('project_type'))


async def log_audit_adjustment(new_adjustment, action, log_message, changelog, headers, project_type=None):
    """Sending information about adjustment.

    This function used for sending information about adjustment changes to function
    which must creates new log about it.

    Args:
        new_adjustment (dict): Dict which includes all information about adjustment: date of updating, uuid of bu,
                               uuid of price group, value of tier override and adjustment value, uuid of product and
                               uuid of project, comment which relates to adjustment, id of adjustment, user full name
                               and user email, status of adjustment.
        action (str): Action which can has such value: 'Create' or 'Read' or 'Update' or 'Delete'.
        log_message (str): Log message.
        changelog (dict): Dict which has such keys: `entity`, `changeid`, `changes`.
        headers (CIMultiDict): This parameter contains information about: connection, host, length of content, x-login,
                               accept-language, accept-encoding, x-client, user-agent, content-type, authorization,
                               x-projecttypes-group, x-timezone.
        project_type: Type of project. Defaults set to None.

    """
    headers = CIMultiDict(headers)
    required_headers = CIMultiDict({
        'X-Client': headers.get('X-Client', ''),
        'Authorization': headers.get('Authorization', ''),
        'x-timezone': headers.get('x-timezone', 'UTC'),
    })

    await log_audit_message(
        context={'headers': required_headers},
        message=log_message,
        action=action,
        project_uuid=new_adjustment['project_uuid'],
        project_type=project_type,
        adjustment=new_adjustment,
        changelog=changelog
    )
