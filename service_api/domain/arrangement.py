"""This module contains all needed functions to provide information for tier override."""

import json

from service_api.constants import SB_QUALIFICATION_METHODOLOGY_TYPE_PBID, SB_QUALIFICATION_METHODOLOGY_TYPE_REBATE
from service_api.services.rest_client import RESTClientRegistry


async def get_product_uuid_list_from_product_group(product_group_uuid: str, headers: dict):
    """This function provide list of product uuids from product group.

    Args:
        product_group_uuid: Uuid of product group.
        headers: Store information about `X-Client`, `Authorization` and `x-timezone`.

    Returns:
        list: List of product uuids.

    """
    arrangements_client = RESTClientRegistry.get('arrangements')
    product_group_products = await arrangements_client.get_product_group_product(
        headers=headers,
        params=f'filter=product_group_uuid eq {product_group_uuid}'
    )
    return (p['product_uuid'] for p in product_group_products)


async def form_plain_tier(raw_tiers: str, headers: dict, product_uuid: str = None):
    """This function forms plain tier depending on project type.

    Args:
        raw_tiers: List of tiers which are available for use.
        headers: Headers store information about `X-Client`, `Authorization` and `x-timezone`.
        product_uuid: Uuid of product. Defaults set to None.

    Returns:
        list: List of tiers which are available for qualification methodology, which configured by user.

    """
    # user input comes from arrangements_api as a string with escaped characters and extra spaces inside
    tiers = json.loads(raw_tiers, strict=False)
    result = []
    # in rebate project tiers can be found by key 'tiers' and in PBID project by key 'eligibility_tiers'
    for tier in tiers.get('tiers', tiers.get('eligibility_tiers', [])):
        ranges = tier.get('ranges')
        for _range in ranges:
            values = _range.get('values')
            for item in _range.get('products'):
                # search for the requested product among the tier products
                if item.get('all_products') or product_uuid in (p.get('product_id') for p in item.get('product', [])):
                    result.append({
                        "tier_id": tier['tier_id'],
                        "tier_name": tier['tier_name'],
                        "values": values
                    })
                    break
                # search for the requested product among the tier product groups
                for product_group in item.get('product_groups', []):
                    product_uuids_gen = await get_product_uuid_list_from_product_group(
                        product_group_uuid=product_group['product_group_uuid'], headers=headers
                    )
                    if product_uuid in product_uuids_gen:
                        result.append({
                            "tier_id": tier['tier_id'],
                            "tier_name": tier['tier_name'],
                            "values": values
                        })
                        break
    return result


async def get_tiers(headers: dict, params):
    """Gets all tiers.

    This function is used for getting all tiers which are available for qualification methodology,
    which configured by user.

    Args:
        headers: Headers store information about `X-Client`, `Authorization` and `x-timezone`.
        params (dict): Params contain value for `price_group_id` and `product_uuid`. Also it contain `filter` (list)
                       there are two dicts where store information about price group id and product uuid and their
                       values.

    Returns:
        list: List of tiers which are available for qualification methodology, which configured by user.
              Otherwise, if qualification methodology doesn't exist function returns empty list.

    """
    arrangements_client = RESTClientRegistry.get('arrangements')
    # get all methodology instances related to the price group
    price_group_methodologies = await arrangements_client.get_price_group_methodologies(
        headers=headers, params=f"filter=price_group_uuid eq {params['price_group_uuid']}&query_date_treatment=all"
    )

    qual_methodology = None
    # check if methodology with methodology type logic_qualification added to the price group
    query_filters = [
        f'methodology_type in {SB_QUALIFICATION_METHODOLOGY_TYPE_PBID},{SB_QUALIFICATION_METHODOLOGY_TYPE_REBATE}'
    ]
    for pg_methodology in price_group_methodologies:
        _filters = query_filters + [f'methodology_definition_uuid eq {pg_methodology["methodology_definition_uuid"]}']
        qual_methodology_definition = await arrangements_client.get_methodology_definitions(
            headers=headers, params='&'.join(f'filter={_filter}' for _filter in _filters)
        )
        if qual_methodology_definition:
            qual_methodology = pg_methodology
            break
    if not qual_methodology:
        return []

    return await form_plain_tier(
        raw_tiers=qual_methodology['user_input'], product_uuid=params.get('product_uuid'), headers=headers
    )
