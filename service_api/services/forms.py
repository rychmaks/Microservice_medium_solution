"""Contains data for creating forms and methods for serializing data."""

from uuid import uuid4
from marshmallow import fields, post_load, pre_load
from marshmallow.validate import OneOf
from sqlalchemy.dialects.postgresql import JSON, JSONB, ARRAY
from enum import Enum, unique

from service_api.models import Adjustments

from rfcommon_api.common.services.form import RequestFilteringSchema, BaseForm


class NullUUID(fields.UUID):
    """UUID field that treats empty strings '' as a null value."""

    def _deserialize(self, value, attr, obj):
        """Check if value is not empty.

        Args:
            value (str): Some uuid.
            attr (str): Name of attribute.
            obj (dict): Dictionary with full information about the object.

        Returns:
            None if value equal `''`. Otherwise, returns the same function which is in parent class.

        """
        if value == '':
            return None
        return super()._deserialize(value, attr, obj)


@unique
class AdjustmentStatuses(Enum):
    """Contains all possible parameters for adjustment statuses."""

    not_applied = 'Not Applied'
    applied = 'Applied'

    @staticmethod  # noqa A003
    def list():
        """Sends a list of all possible parameters for adjustment statuses.

        Returns:
             list: List of all adjustment statuses.

        """
        return list(map(lambda a: a.value, AdjustmentStatuses))


@unique
class TierFilterOptions(Enum):
    """Contains all possible parameters for tier filter options."""

    price_group_uuid = 'price_group_uuid'
    product_uuid = 'product_uuid'
    tier_id = 'tier_id'

    @staticmethod  # noqa A003
    def list():
        """Sends a list of all possible parameters for tier filter options.

        Returns:
            list: List of all tier filter options.

        """
        return list(map(lambda a: a.value, TierFilterOptions))


class AdjustmentFilteringSchema(RequestFilteringSchema):
    """Check that the name of column is valid for sorting and filtering."""

    model = Adjustments

    def _validate_column_name(self, column_name):
        """Check that the name of column is valid.

        Args:
            column_name (str): name of column.

        Raises:
             ValidationError: Raise exception when (de)serialization fails.

        """
        if column_name not in self.model.c:
            raise self._validation_error(
                message=f"Specified column [{column_name}] was not found among possible ones."
            )
        elif isinstance(self.model.c[column_name].type, (JSON, JSONB, ARRAY)):
            raise self._validation_error(
                message=f"Sorting and filtering for column [{column_name}] of type "
                f"[{self.model.c[column_name].type}] is not supported"
            )


class TierFiltersForm(BaseForm):
    """Contains all possible parameters for tier filters form."""

    field = fields.String(validate=OneOf(TierFilterOptions.list()), required=True)
    operation = fields.String(required=True)
    value = fields.String(required=True)


class TierOverrideFilteringSchema(BaseForm):
    """This class is a tier override filtering schema.

    Class has methods to invoke before and after deserializing an object.

    """

    filter = fields.Nested(TierFiltersForm, many=True, required=True)  # noqa A003

    @pre_load
    def parse_filters(self, data):
        """This function is used for parsing filters which is in `data`.

        Args:
            data (dict): Dictionary which contains one key `filter` and value for this key is a list of all filters.

        Returns:
             dict: Dictionary with parsed filters.

        """
        result = []
        for item in data['filter']:
            item = item.split(' ')
            f = {
                'field': item[0],
                'operation': item[1],
                'value': item[2]
            }
            result.append(f)
        return {'filter': result}

    @post_load
    def _populate_data_with_filter_fields(self, data):
        """This function is used for populate data with filter fields.

        Args:
            data (dict): Dictionary which contains one key `filter` and value for this key is a list of all filters.

        Returns:
            dict: Dictionary with populated data with filter fields.

        """
        for f in data['filter']:
            data[f['field']] = f['value']
        return data


class ClientKeyspaceCreateForm(BaseForm):
    """Contains all possible parameters for creating client keyspace form."""

    client_short_name = fields.String(required=True)
    hosts = fields.String(required=True)


class CreateAdjustmentForm(BaseForm):
    """This class contains all possible parameters for creating client adjustment form.

    Here registered a method to invoke after deserializing an object.

    """

    id = fields.UUID(required=False)  # noqa A003
    product_uuid = NullUUID(required=True, allow_none=True)
    bu_uuid = NullUUID(required=True, allow_none=True)
    project_uuid = fields.UUID(required=True)
    price_group_uuid = fields.UUID(required=True)
    adjustment_value = fields.Decimal(required=True, allow_none=True)
    tier_override =  fields.Dict(allow_none=True, required=False)
    comment = fields.String(required=True)
    user_full_name = fields.String(required=False)
    status = fields.String(validate=OneOf(AdjustmentStatuses.list()), required=False)
    user = fields.String(required=False)
    record_hash = fields.String(required=False)
    cal_total_rebate_amt = fields.Decimal(allow_none=True, required=False, attribute="total_rebate_amount")
    tier_id = fields.Integer(allow_none=True, required=False)

    @post_load
    def generate_uuid(self, data):
        """Generate id for adjustment.

        Args:
            data (dict): dictionary which contains all needed information about an adjustment.

        Returns:
            dict:

        Raises:
            ValidationError: Raise exception when data contains two values: `adjustment_value` and `tier_override`
                             or both of that values are equal to None.

        """
        if data.get('adjustment_value') and data.get('tier_override'):
            raise self._validation_error(
                f"Validation error, can't add manual adjustment and tier override simultaneously"
            )
        if data.get('adjustment_value') is None and data.get('tier_override') is None:
            raise self._validation_error(f"Validation error, missing a value to override")
        if not data.get("id"):
            data["id"] = str(uuid4())
        return data


class UpdateAdjustmentForm(BaseForm):
    """Contains all possible parameters for update adjustment form."""

    adjustment_value = fields.Decimal(allow_none=True, required=False, default=None)
    comment = fields.String(required=True)
    tier_override = fields.Dict(allow_none=True, required=False, default=None)
    record_hash = fields.String(required=False)
    cal_total_rebate_amt = fields.Decimal(allow_none=True, required=False, attribute="total_rebate_amount")
    tier_id = fields.Integer(allow_none=True, required=False)


class AppliedAdjustmentsForm(BaseForm):
    """Contains all possible parameters for applied adjustment form."""

    project_uuid = fields.UUID(required=True)


class ProjectPeriodForm(BaseForm):
    """Contains all possible parameters for project period form."""

    project_date_start = fields.Date(required=True)
    project_date_end = fields.Date(required=True)
