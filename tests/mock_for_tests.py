from multidict import CIMultiDict


class AdjustmentMock:
    log_level = 'AUDIT'
    logger_name = 'audit_log'

    create_manual_override_data = {
        "product_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d55",
        "bu_uuid": "b5cd5ce6-4c46-4e6d-1111-7df38fdd7d55",
        "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
        "adjustment_value": 0,
        "cal_total_rebate_amt": 200,
        "comment": "Changed rebate to make more profit",
        "price_group_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d77",
        "record_hash": "record_hash",
        "tier_override": None,
    }

    create_manual_override_data_with_adjustment_and_tier_override_simultaneously = {
        "product_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d55",
        "bu_uuid": "b5cd5ce6-4c46-4e6d-1111-7df38fdd7d55",
        "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
        "adjustment_value": 199.34,
        "tier_id": 4342,
        "tier_override": {
            "tier_id": 6786,
            "tier_name": "Tier2",
            "values": [
                {
                    'earliest_date': '2000-01-01',
                    'latest_date': None,
                    'value': 10,
                },
            ],
        },
        "cal_total_rebate_amt": 200,
        "comment": "Changed rebate to make more profit",
        "price_group_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d77",
        "record_hash": "record_hash",
    }

    create_manual_override_data_without_adjustment_and_tier_override_simultaneously = {
        "product_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d55",
        "bu_uuid": "b5cd5ce6-4c46-4e6d-1111-7df38fdd7d55",
        "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
        "adjustment_value": None,
        "tier_override": None,
        "cal_total_rebate_amt": 200,
        "comment": "Changed rebate to make more profit",
        "price_group_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d77",
        "record_hash": "record_hash",
    }

    create_tier_override_data = {
        "product_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d55",
        "bu_uuid": "b5cd5ce6-4c46-4e6d-1111-7df38fdd7d55",
        "project_uuid": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
        "adjustment_value": None,
        "comment": "Changed rebate to make more profit 1",
        "price_group_uuid": "b5cd5ce6-4c46-1111-a67d-7df38fdd7d77",
        "record_hash": "record_hash",
        "tier_id": 4342,
        "tier_override": {
            "tier_id": 6786,
            "tier_name": "Tier2",
            "values": [
                {
                    'earliest_date': '2000-01-01',
                    'latest_date': None,
                    'value': 10,
                },
            ],
        },
    }

    update_manual_override_data = {
        "cal_total_rebate_amt": 200,
        "adjustment_value": 999999.00,
        "comment": "Update rebate to make more profit!!!",
        "tier_override": None,
        "record_hash": "record_hash"
    }

    update_tier_override_data = {
        "adjustment_value": None,
        "comment": "Update adjustment",
        "record_hash": "record_hash",
        "tier_id": 6786,
        "tier_override": {
            "tier_id": 1234,
            "tier_name": "Tier2",
            "values": [
                {
                    'earliest_date': '2000-02-23',
                    'latest_date': None,
                    'value': 5,
                },
            ],
        },
    }

    update_not_existing_tier_override_data = {
        "adjustment_value": None,
        "comment": "Update adjustment",
        "record_hash": "record_hash",
        "tier_override": {
            "tier_id": 4567,
            "tier_name": "Tier",
            "values": [
                {
                    'earliest_date': '2000-02-23',
                    'latest_date': None,
                    'value': 5,
                },
            ],
        },
    }

    required_headers = CIMultiDict({
        'X-Client': 'test',
        'Authorization': 'test',
        'x-timezone': 'UTC',
    })

    calculated_values = {
        'total_rebate_amount': 500,
        'tier_id': 2,
    }

    changelog_changeid = 'f2b1bf6e-90c0-4771-856b-63fdde2c2ffa'
    manual_override_changelog = {
        'entity': 'Adjustment',
        'changeid': changelog_changeid,
        'changes': [
            {
                'field': 'adjustment_value',
                'oldvalue': str(calculated_values['total_rebate_amount']),
                'newvalue': str(create_manual_override_data['adjustment_value']),
            }
        ]
    }

    tier_override_changelog = {
        'entity': 'Adjustment',
        'changeid': changelog_changeid,
        'changes': [
            {
                'field': 'tier_id',
                'oldvalue': str(calculated_values['tier_id']),
                'newvalue': str(create_tier_override_data['tier_override']['tier_id']),
            }
        ]
    }

    project_registry_data = {
        "assignee": "test_user_first_name@somedomain.com",
        "workflow_step": "analyst_review",
        "workflow_substep": ["adjustments"],
        "project_type": "rf_sales_based",
        "id": "b5cd5ce6-4c46-4e6d-a67d-7df38fdd7d55",
    }

    adjustment_fields = [
        'id',
        'project_uuid',
        'price_group_uuid',
        'bu_uuid',
        'product_uuid',
        'adjustment_value',
        'tier_override',
        'comment',
        'user',
        'user_full_name',
        'status',
        'updated_at',
    ]


class ArrangementMock:

    qualification_methodology = {
        "methodology_definition_uuid": "ba9a8889-f47e-4723-98ba-78b01e25d2fb",
        "effective_date": "2018-10-16T15:42:08.203435",
        "owner": "REBATES",
        "name": "Multi-Parameter Qualification (Percent)",
        "template_type": "logic",
        "methodology_type": "logic_qualification_rebate",
        "template": "\"\"\"\nMulti-parameter qualification methodology,which returns percent.\n\"\"\"\nimport functools\nfrom datetime import datetime\nfrom decimal import Decimal, getcontext\n\nfrom pyspark.sql import DataFrame\nfrom pyspark.sql.functions import array, udf, col\nfrom pyspark.sql.types import DecimalType, IntegerType, StringType, StructField, StructType\n\ngetcontext().prec = 32  # set Decimal precision to 32 digits\nEVALUATION_BU_COLUMN = \"evaluation_bu_uuid\"\nEVALUATION_PRODUCT_COLUMN = \"evaluation_product_uuid\"\n\nEVALUATION_VALUE_COLUMN = \"eval_value\"  # column name for value from evaluation methodology\nNUMBER_OF_EV_METH_INPUT_COLUMNS = 3\nREQUIRED_KWARGS = {'evaluation_results'}\n\n\ndef validate_input(methodology):\n    @functools.wraps(methodology)\n    def decorator(context, *, input_parameters=None, methodology_inputs=None, **kwargs):\n        if not methodology_inputs:\n            raise Exception('No methodology input is passed to methodology')\n        if not input_parameters:\n            raise Exception('No input parameters is passed to methodology')\n        if not input_parameters.get('project'):\n            raise Exception('Input parameter requires project field')\n        if not input_parameters['project'].get('start_date') or not input_parameters['project'].get('end_date'):\n            raise Exception('Input parameters requires start_date and end_date in project')\n        if not kwargs.get('evaluation_results'):\n            raise Exception('No evaluation results were passed to methodology.')\n        kwargs_set = set(kwargs)\n        issubset = REQUIRED_KWARGS.issubset(kwargs_set)\n        if issubset:\n            for _ev_res in kwargs.get('evaluation_results'):\n                if not (hasattr(_ev_res, 'data_frame') and isinstance(getattr(_ev_res, 'data_frame'), DataFrame)):\n                    raise Exception('Passed results do not contain dataframes.')\n        return methodology(context, input_parameters=input_parameters, methodology_inputs=methodology_inputs,\n                           **kwargs)\n\n    return decorator\n\n\n# =====================================RUN METHOD============================================\n\n@validate_input\ndef run(context, input_parameters=None, methodology_inputs=None, tier_convert_function=None, **kwargs):\n    \"\"\"\n    Main methodology function\n    Args:\n        context: Context instance\n        input_parameters: dictionary object\n        methodology_inputs: dictionary object\n        tier_convert_function: function for converting tiers input\n        **kwargs:\n\n    Returns:\n        qualification_result(DataFrame) result DF\n    \"\"\"\n    eval_value = context.add_scope_prefix(EVALUATION_VALUE_COLUMN, context.get_current_entity()[\"price_group_uuid\"])\n    # get tiers parameters\n    tiers_main = methodology_inputs.get(\"tiers\")\n    if not tiers_main:\n        raise Exception(\"Tiers input parameter is not passed to the qualification methodology\")\n    tiers_main = tier_convert_function(tiers=tiers_main, project=input_parameters['project'], product_or_bu='prod')\n\n    # get outputs of the evaluation methodologies\n    evaluation_results = kwargs.get(\"evaluation_results\")\n\n    # validate base tiers\n    validate_base_tiers(context=context, tiers_main=tiers_main, input_parameters=input_parameters)\n\n    evaluation_bu_column = context.add_scope_prefix(\n        EVALUATION_BU_COLUMN, context.get_current_entity()[\"price_group_uuid\"]\n    )\n\n    evaluation_product_column = context.add_scope_prefix(EVALUATION_PRODUCT_COLUMN,\n                                                         context.get_current_entity()[\"price_group_uuid\"])\n\n    eval_met_list_of_dfs = [result.data_frame for result in evaluation_results]\n\n    # we assume that if eval_types are both aggregate number of rows cant be greater than one\n    # TODO delete\n    if context.get_current_entity().get(\"product_evaluation_type\", 'individual') == \"aggregate\" and \\\n            context.get_current_entity().get(\"business_unit_evaluation_type\", 'individual') == \"aggregate\":\n        for ev_df in eval_met_list_of_dfs:\n            if ev_df.count() > 1:\n                raise Exception(\"DF from evaluation methodology has mor than 1 row.(\"\n                                \"product_evaluation_type=aggregate,business_unit_evaluation_type=aggregate)\")\n    # join multiple input DF\n    join_on = [evaluation_bu_column, evaluation_product_column]\n    joined_eval_df = None\n    for idx, ev_df in enumerate(eval_met_list_of_dfs):\n        number = idx + 1\n        if not joined_eval_df:\n            joined_eval_df = ev_df.withColumnRenamed(eval_value, \"value_1\")\n        else:\n            joined_eval_df = joined_eval_df.join(ev_df, join_on, \"inner\"). \\\n                withColumnRenamed(eval_value, \"value_{}\".format(number))\n    list_of_ev_col_names = [\"value_{}\".format(n) for n in range(1, len(eval_met_list_of_dfs) + 1)]\n\n    # generate udf_result column\n    joined_eval_df = joined_eval_df.withColumn(\n        \"udf_result\",\n        get_tier(\n            list_of_ev_col_names,\n            tiers_main=tiers_main,\n            project_dates=input_parameters['project'],\n            price_group=context.get_current_entity(),\n            evaluation_product_column=evaluation_product_column\n        )\n    )\n    # extract info from udf_result\n    tier_id_column = context.add_scope_prefix(\"tier_id\", context.get_current_entity()[\"price_group_uuid\"])\n    result_df = joined_eval_df.withColumn(\n        tier_id_column,\n        joined_eval_df[\"udf_result\"].getItem(\"tier_id\"),\n    ).withColumn(\n        context.add_scope_prefix(\"tier_name\", context.get_current_entity()[\"price_group_uuid\"]),\n        joined_eval_df[\"udf_result\"].getItem(\"tier_name\"),\n    ).withColumn(\n        context.add_scope_prefix(\"tier_percent\", context.get_current_entity()[\"price_group_uuid\"]),\n        joined_eval_df[\"udf_result\"].getItem(\"tier_percent\").cast(DecimalType(precision=32, scale=16)),\n    ).withColumn(\n        context.add_scope_prefix(\"base_tier_id\", context.get_current_entity()[\"price_group_uuid\"]),\n        joined_eval_df[\"udf_result\"].getItem(\"base_tier_id\"),\n    ).withColumn(\n        context.add_scope_prefix(\"base_tier_name\", context.get_current_entity()[\"price_group_uuid\"]),\n        joined_eval_df[\"udf_result\"].getItem(\"base_tier_name\"),\n    ).withColumn(\n        context.add_scope_prefix(\"base_tier_percent\", context.get_current_entity()[\"price_group_uuid\"]),\n        joined_eval_df[\"udf_result\"].getItem(\"base_tier_percent\").cast(DecimalType(precision=32, scale=16))\n    ).drop(\"udf_result\")\n\n    # remove all rows without tier\n    result_df = result_df.filter(result_df[tier_id_column].isNotNull())\n    ret_columns = [context.Result.get_output_column(\n        title=\"Achieved Tier Name\",\n        column_scope_id=context.get_current_entity()[\"price_group_uuid\"],\n        data_type='string',\n        field='tier_name'\n    ), context.Result.get_output_column(\n        title=\"Base Tier Name\",\n        column_scope_id=context.get_current_entity()[\"price_group_uuid\"],\n        data_type='string',\n        field='base_tier_name'\n    )]\n\n    columns_which_no_show_on_ui = [context.Result.get_output_column(\n        title=\"Achieved Tier ID\",\n        column_scope_id=context.get_current_entity()[\"price_group_uuid\"],\n        data_type='integer',\n        field='tier_id'\n    ), context.Result.get_output_column(\n        title=\"Base Tier ID\",\n        column_scope_id=context.get_current_entity()[\"price_group_uuid\"],\n        data_type='integer',\n        field='base_tier_id'\n    )]\n    for column in columns_which_no_show_on_ui:\n        column['show_on_ui'] = False\n        ret_columns.append(column)\n\n    for column in list_of_ev_col_names:\n        result_df = result_df.drop(col(column))\n\n    qualification_result = context.wrap_to_result(output_name='qualification_percent_summary', data_frame=result_df,\n                                                  columns=ret_columns,\n                                                  output_scope_id=context.get_current_entity()[\"price_group_uuid\"])\n    return qualification_result\n\n\n# =========================================FUNCTIONS=============================================\n\ndef get_tier(list_of_ev_column_names, *, tiers_main, project_dates, price_group, evaluation_product_column):\n    # Schema of data that will be stored in udf_result column\n    schema = StructType([\n        StructField(\"base_tier_id\", IntegerType(), True),\n        StructField(\"base_tier_name\", StringType(), True),\n        StructField(\"base_tier_percent\", DecimalType(precision=32, scale=16), True),\n        StructField(\"tier_id\", IntegerType(), True),\n        StructField(\"tier_name\", StringType(), True),\n        StructField(\"tier_percent\", DecimalType(precision=32, scale=16), True)\n    ])\n    list_of_col_names = None\n    if price_group[\"product_evaluation_type\"] == \"individual\":\n        list_of_col_names = list_of_ev_column_names.copy()\n        list_of_col_names.insert(0, evaluation_product_column)\n\n    elif price_group[\"product_evaluation_type\"] == \"aggregate\":\n        list_of_col_names = list_of_ev_column_names.copy()\n    if not list_of_col_names:\n        raise Exception(\"List of columns names that will be passed to UDF function is empty.\")\n    arr_of_col_names = array(list_of_col_names)\n\n    @udf(returnType=schema)\n    def get_tier_udf(col_values) -> StructType():\n        \"\"\"\n        Multi-parameter tier qualifier iterates over columns and defines applicable tier.\n        Args:\n            col_values:\n\n        Returns:\n            base_tier_id\n            base_tier_name\n            base_tier_percent/amount\n            tier_id\n            tier_name\n            tier_percent/amount\n\n        \"\"\"\n        tiers = []\n        prod_uuid = None\n        validate_ranges_partial, check_if_all_values_in_ranges_partial = None, None\n        if price_group[\"product_evaluation_type\"] == \"individual\":\n            ev_values = col_values[1:]\n            prod_uuid = col_values[0]\n            if not prod_uuid:\n                raise Exception(\"Invalid data in input Dataframe.\")\n            tiers = tiers_main.get(prod_uuid)\n            if not tiers:\n                # raise Exception(\"No info about tiers for Product Unit {}\".format(prod_uuid))\n                return None, \"\", None, None, \"\", None\n            # partial for all values\n            validate_ranges_partial = functools.partial(validate_ranges, ev_values=ev_values)\n            check_if_all_values_in_ranges_partial = functools.partial(check_if_all_values_in_ranges,\n                                                                      ev_values=ev_values)\n        elif price_group[\"product_evaluation_type\"] == \"aggregate\":\n            ev_values = col_values[:]\n            prod_uuid = \"\"\n            tiers = tiers_main.get(prod_uuid)\n            if not tiers:\n                # raise Exception(\"No info about tiers for Product Unit {}\".format(prod_uuid))\n                return None, \"\", None, None, \"\", None\n            # partial for all values after 2 agg_bu and product\n            validate_ranges_partial = functools.partial(validate_ranges, ev_values=ev_values)\n            check_if_all_values_in_ranges_partial = functools.partial(check_if_all_values_in_ranges,\n                                                                      ev_values=ev_values)\n\n        if not tiers or prod_uuid is None:\n            raise Exception(\"No tiers or prod_uuid\")\n        inclusive_ranges = get_ranges_with_inclusive_logic_for_highest_values(tiers=tiers)\n        base_tier_id, base_tier_name, base_tier_percent = None, \"\", None\n        num_of_basis_tiers = 0\n        for tier in tiers:\n            if tier.get(\"is_basis\"):\n                num_of_basis_tiers += 1\n                base_tier_id = tier.get(\"tier_id\")\n                base_tier_name = tier.get(\"tier_name\")\n                if base_tier_id:\n                    base_tier_percent = get_value_by_tier_id(base_tier_id, project_dates=project_dates, tiers=tiers,\n                                                             prod_uuid=prod_uuid)\n                if not base_tier_percent:\n                    raise Exception(\"Couldn't find valid value for basis tier with id {}\".format(base_tier_id))\n        if num_of_basis_tiers > 1:\n            raise Exception(\"Invalid user_input. You have multiple basis tiers.\")\n        if not validate_ranges_partial and not check_if_all_values_in_ranges_partial:\n            raise Exception(\"Could`nt use internal function. Input or internal error.\")\n        for tier in tiers:\n            validate_ranges_partial(tier=tier)\n            if check_if_all_values_in_ranges_partial(tier=tier, inclusive_ranges=inclusive_ranges):\n                return base_tier_id, base_tier_name, base_tier_percent, \\\n                       tier[\"tier_id\"], tier[\"tier_name\"], get_value_by_tier_id(tier[\"tier_id\"],\n                                                                                project_dates=project_dates,\n                                                                                tiers=tiers, prod_uuid=prod_uuid)\n            # tier_id,tier_name,tier_percent\n        return None, \"\", None, None, \"\", None\n\n    return get_tier_udf(arr_of_col_names)\n\n\ndef get_ranges_with_inclusive_logic_for_highest_values(tiers):\n    \"\"\"\n    This function returns dict of ranges with tier_ids provided as a values in list.\n    Key is the range index and value is the  list of tier_ids.\n    If in return dict value is None,that means that highest value [\"to\"] was provided as None value.\n    Args:\n        tiers:\n\n    Returns:\n        max_values_loc(dict)\n    \"\"\"\n    max_initialized = False\n    max_values_loc = {}  # key is a range idx and values is tier_id\n    max_value = []\n    for tier in tiers:\n        ranges = tier.get(\"params_ranges\", None)\n        if not max_initialized:\n            for idx, tier_range in enumerate(ranges):\n                max_values_loc[idx] = []\n                if tier_range.get(\"to\") is None:\n                    max_values_loc[idx] = None\n                max_value.append(tier_range[\"to\"])\n            max_initialized = True\n            continue\n        for idx, tier_range in enumerate(ranges):\n            if tier_range.get(\"to\") is None:\n                max_values_loc[idx] = None\n            if max_values_loc[idx] is not None and max_value[idx] is not None and (tier_range[\"to\"] > max_value[idx]):\n                max_value[idx] = tier_range[\"to\"]\n\n    for tier in tiers:\n        ranges = tier.get(\"params_ranges\", None)\n        for idx, tier_range in enumerate(ranges):\n            if max_values_loc[idx] is not None and max_value[idx] is not None and (tier_range[\"to\"] == max_value[idx]):\n                max_values_loc[idx].append(tier.get(\"tier_id\"))\n\n    return max_values_loc\n\n\ndef get_value_by_tier_id(tier_id: int, project_dates: dict, tiers: list, prod_uuid: str):\n    \"\"\"\n    This function chooses right value (percent/money amount) for\n    tier.\n    Args:\n        prod_uuid:\n        tier_id:\n        project_dates:\n        tiers:\n\n    Returns:\n        result_value(Decimal)\n\n    \"\"\"\n    if not prod_uuid:\n        prod_uuid = \"AGGREGATE\"\n    if not project_dates:\n        raise Exception(\"No params dates specified in project\")\n    date_format_start_date = date_format_end_date = '%Y-%m-%dT%H:%M:%S.%f'\n    if len(project_dates[\"start_date\"]) < 11:\n        date_format_start_date = '%Y-%m-%d'\n    if len(project_dates[\"end_date\"]) < 11:\n        date_format_end_date = '%Y-%m-%d'\n    start_date = datetime.strptime(project_dates[\"start_date\"], date_format_start_date).date()\n    end_date = datetime.strptime(project_dates[\"end_date\"], date_format_end_date).date()\n    num_of_intersections = 0\n    result_value = None\n    for tier in tiers:\n        if tier[\"tier_id\"] == tier_id:\n            for value in tier[\"values\"]:\n                earliest_date = convert_str_to_date(value[\"earliest_date\"])\n                latest_date = value.get(\"latest_date\", None)\n                if latest_date:\n                    latest_date = convert_str_to_date(latest_date)\n                if earliest_date <= start_date and \\\n                        (latest_date is None or end_date <= latest_date):\n                    result_value = value[\"value\"]\n                if check_intersection_of_dates(start_date, end_date, earliest_date, latest_date):\n                    num_of_intersections += 1\n                if num_of_intersections > 1:\n                    raise Exception(\"Invalid user input. Date from context intersects with \"\n                                    \"two or more value dates (earliest,latest) \"\n                                    \"in tier with id {tier_id} in product {prod_uuid}.\"\n                                    .format(tier_id=tier_id, prod_uuid=prod_uuid))\n            if result_value is None:\n                raise Exception(\"Invalid user_input. Can`t find valid value in tier \"\n                                \"with id {tier_id} in product {prod_uuid}.\"\n                                .format(tier_id=tier_id, prod_uuid=prod_uuid))\n            else:\n                return Decimal(str(result_value))\n\n\ndef validate_ranges(tier: dict, ev_values: list):\n    \"\"\"\n    Function validates ranges in tiers by comparing its length and checking absence\n    Args:\n        tier:\n        ev_values:\n    \"\"\"\n    params_ranges = tier.get(\"params_ranges\", None)\n    if params_ranges is None:\n        raise Exception(\"No params ranges specified in tier with id {}\".format(tier.get('tier_id')))\n    if len(params_ranges) != len(ev_values):\n        raise Exception(\"Number of parameters from evaluation methodologies are not equal to number of params \"\n                        \"defined by user in tier with id {}\".format(tier.get('tier_id')))\n\n\ndef check_intersection_of_dates(start_date, end_date, earliest_date, latest_date) -> bool:\n    \"\"\"\n    Check if date from context intersects with dates from tiers.\n    Args:\n        start_date:\n        end_date:\n        earliest_date:\n        latest_date:\n\n    Returns:\n        bool\n    \"\"\"\n    if latest_date is None:\n        return earliest_date < end_date\n    else:\n        return min(end_date, latest_date) > max(start_date, earliest_date)\n\n\ndef convert_str_to_date(date_str):\n    try:\n        return datetime.strptime(date_str, '%Y-%m-%d').date()\n    except ValueError:\n        raise ValueError(\"Incorrect data format, should be YYYY-MM-DD\")\n\n\ndef check_if_all_values_in_ranges(tier, ev_values, inclusive_ranges) -> bool:\n    \"\"\"\n    Function checks if all values from evaluation methodologies\n    hit in ranges\n    Args:\n        tier:\n        ev_values:\n        inclusive_ranges:\n\n    Returns:\n        bool\n    \"\"\"\n    ranges = tier[\"params_ranges\"]\n    tier_id = tier[\"tier_id\"]\n    # iterate over ranges and values\n    in_range = [False] * len(ranges)\n    for idx, (tier_range, ev_value) in enumerate(zip(ranges, ev_values)):\n        if Decimal(str(tier_range[\"from\"])) <= Decimal(str(ev_value)):\n            # Check inclusive logic\n            if inclusive_ranges.get(idx) is not None and tier_id in inclusive_ranges[idx]:\n                if Decimal(str(tier_range[\"to\"])) is not None and Decimal(str(tier_range[\"to\"])) \\\n                        >= Decimal(str(ev_value)):  # >=\n                    in_range[idx] = True\n                    continue\n            if tier_range[\"to\"] is None or Decimal(str(tier_range[\"to\"])) > Decimal(str(ev_value)):  # >\n                in_range[idx] = True\n    all_in_range = set(in_range)\n    if all_in_range == {True}:\n        return True\n    return False\n\n\ndef get_min_value_id(*, tiers, project_dates, prod_uuid):\n    \"\"\"\n    Get tier with minimal value (percent/amount)\n    Args:\n        prod_uuid:\n        tiers:\n        project_dates:\n\n    Returns:\n        min_value_id\n    \"\"\"\n    min_initialized = False\n    min_value = None\n    min_value_id = None\n    for tier in tiers:\n        if not min_initialized:\n            min_value = get_value_by_tier_id(tier.get('tier_id'), project_dates=project_dates, tiers=tiers,\n                                             prod_uuid=prod_uuid)\n            min_value_id = tier.get('tier_id')\n            min_initialized = True\n        tier_value = get_value_by_tier_id(tier.get('tier_id'), project_dates=project_dates, tiers=tiers,\n                                          prod_uuid=prod_uuid)\n        if tier_value < min_value:\n            min_value = tier_value\n            min_value_id = tier.get('tier_id')\n    return min_value_id\n\n\ndef validate_base_tiers(*, tiers_main, context, input_parameters):\n    \"\"\"\n    Function checks if base ties contains lowest value\n    Args:\n        input_parameters:\n        tiers_main:\n        context::\n    \"\"\"\n    project_dates = input_parameters['project']\n    pd_agg_type = context.get_current_entity().get(\"product_evaluation_type\", 'individual')\n    if pd_agg_type == \"aggregate\":\n        prod_uuid = ''\n        tiers = tiers_main.get(prod_uuid)\n        if not tiers:\n            raise Exception(\"No AGGREGATE tiers for PRODUCT\")\n        min_value_idx = get_min_value_id(tiers=tiers, project_dates=project_dates, prod_uuid=prod_uuid)\n        for tier in tiers:\n            if tier.get(\"tier_id\") != min_value_idx and tier.get(\"is_basis\"):\n                raise Exception(\"Basis tier contains value greater than minimal fro product AGGREGATE.\")\n\n    elif pd_agg_type == \"individual\":\n        for prod_uuid, tiers in tiers_main.items():\n            min_value_idx = get_min_value_id(tiers=tiers, project_dates=project_dates, prod_uuid=prod_uuid)\n            for tier in tiers:\n                if tier.get(\"tier_id\") != min_value_idx and tier.get(\"is_basis\"):\n                    raise Exception(\"Basis tier contains value greater than minimal for product {prod_uuid}.\".format(\n                        prod_uuid=prod_uuid))\n",
        "description": "Description",
        "data_source_list": [
            "indirect"
        ],
        "user_input_format": "{\n  \"name\": \"Multi-Parameter Qualification (Percent)\",\n  \"fieldDefs\": [\n    {\n      \"label\": \"Tiers\",\n      \"type\": \"custom-key-value\",\n      \"field\": \"tiers\",\n      \"actionLabel\": \"Add Tier\",\n      \"model\": [\n        {\n          \"label\": \"Tier id\",\n          \"type\": \"integer\",\n          \"field\": \"tier_id\",\n          \"placeholder\": 1,\n          \"validation\": {\n            \"required\": true\n          },\n          \"order\": 1\n        },\n        {\n          \"label\": \"Tier name\",\n          \"type\": \"string\",\n          \"field\": \"tier_name\",\n          \"placeholder\": \"tier name\",\n          \"validation\": {\n            \"required\": true\n          },\n          \"order\": 2\n        },\n        {\n          \"label\": \"Is base tier?\",\n          \"type\": \"boolean\",\n          \"field\": \"is_base\",\n          \"placeholder\": \"base tier\",\n          \"order\": 3\n        },\n        {\n          \"label\": \"Products\",\n          \"type\": \"custom-key-value\",\n          \"field\": \"products\",\n          \"actionLabel\": \"Add product\",\n          \"order\": 4,\n          \"model\": [\n            {\n              \"label\": \"Product\",\n              \"type\": \"search-modal\",\n              \"multiple\": false,\n              \"field\": \"product\",\n              \"appConfigMap\": \"products\",\n              \"actionLabel\": \"Search for Product\",\n              \"actionType\": \"post-render-search-modal\",\n              \"order\": 1\n            },\n            {\n              \"label\": \"Ranges\",\n              \"type\":\"custom-key-value\",\n              \"field\":\"ranges\",\n              \"actionLabel\": \"Add range\",\n              \"order\": 2,\n              \"model\": [\n                {\n                  \"label\": \"Earliest date\",\n                  \"type\": \"date\",\n                  \"field\": \"earliest_date\",\n                  \"validation\": {\n                    \"required\": true\n                  },\n                  \"order\": 1\n                },\n                {\n                  \"label\": \"Latest date\",\n                  \"type\": \"date\",\n                  \"field\": \"latest_date\",\n                  \"validation\": {\n                    \"required\": false\n                  },\n                  \"order\": 2\n                },\n                {\n                  \"label\": \"Evaluation parameters\",\n                  \"type\":\"custom-key-value\",\n                  \"field\": \"evaluation_parameters\",\n                  \"actionLabel\": \"Add eval param\",\n                  \"order\": 3,\n                  \"model\": [\n                      {\n                        \"label\": \"Range start\",\n                        \"type\": \"float\",\n                        \"field\": \"from\",\n                        \"order\": 1\n                      },\n                      {\n                        \"label\": \"Range end\",\n                        \"type\": \"float\",\n                        \"field\": \"to\",\n                        \"order\": 2\n                      }\n                  ]\n                }\n              ]\n            },\n            {\n              \"label\": \"Values\",\n              \"type\":\"custom-key-value\",\n              \"field\":\"values\",\n              \"actionLabel\": \"Add values\",\n              \"order\": 3,\n              \"model\": [\n                {\n                  \"label\": \"Earliest date\",\n                  \"type\": \"date\",\n                  \"field\": \"earliest_date\",\n                  \"validation\": {\n                    \"required\": true\n                  },\n                  \"order\": 1\n                },\n                {\n                  \"label\": \"Latest date\",\n                  \"type\": \"date\",\n                  \"field\": \"latest_date\",\n                  \"order\": 2\n                },\n                {\n                  \"label\": \"Value\",\n                  \"type\": \"float\",\n                  \"field\": \"value\",\n                  \"validation\": {\n                    \"required\": true\n                  },\n                  \"order\": 3\n                }\n              ]\n            }\n          ]\n        }\n      ],\n      \"order\": 1\n    }\n  ],\n  \"actions\": [\n    {\n      \"label\": \"Save\",\n      \"type\": \"primary\"\n    },\n    {\n      \"label\": \"Reset\",\n      \"type\": \"secondary\"\n    }\n  ]\n}\n",
        "system_input_format": None,
        "output_format": None,
        "earliest_date": "1900-01-01",
        "latest_date": "9999-12-31",
        "record_status": "prod",
        "record_source_uuid": None
    }

    price_group_methodology_new_tier_format = [
        {
            "price_group_methodology_uuid": "85f085ee-4b4f-49e3-a4d2-ae68d2258323",
            "effective_date": "2018-10-24T09:08:19.673540",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ba9a8889-f47e-4723-98ba-78b01e25d2fb",
            "owner": "REBATES",
            "name": "Multi-Parameter Qualification (Percent)",
            "description": "Description",
            "user_input": """
                {
                        "tiers": [
                        {
                        "tier_id": 111,
                        "tier_name": "tier_1",
                        "is_base": true,
                        "ranges": [
                            {
                                "evaluation_parameters": [
                                    {
                                        "from": 0,
                                        "to": 20
                                    }
                                ],
                                "products": [
                                    {
                                        "all_products": false,
                                        "product_id": "dba4f78c-7488-11e8-93f3-0242ac110021",
                                        "product_groups":
                                            [
                                                {
                                                    "product_group_uuid":"111"
                                                }
                                            ]
                                    }
                                ],
                                "values": [
                                    {
                                        "earliest_date": "2018-11-01",
                                        "latest_date": "2018-11-30",
                                        "value": 5
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "tier_id": 222,
                        "tier_name": "tier_2",
                        "is_base": false,
                        "ranges": [
                            {
                                "evaluation_parameters": [
                                    {
                                        "from": 20,
                                        "to": 50
                                    }
                                ],
                                "products": [
                                    {
                                        "all_products": false,
                                        "product": [
                                        {
                                           "product_id": "dba4f78c-7488-11e8-93f3-0242ac110018"
                                        }
                                        ]
                                    }
                                ],
                                "values": [
                                    {
                                        "earliest_date": "2018-11-01",
                                        "latest_date": "2018-11-15",
                                        "value": 10
                                    }
                                ]
                            }
                        ]
                    }
                ]
                }""",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "4998d28b-983b-4eca-870e-5ddd361bf7c5",
            "effective_date": "2018-10-24T09:08:19.755232",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "b3ff63df-b7f3-44a9-b4a8-24011bb761f3",
            "owner": "REBATES",
            "name": "Growth (Gross/Net Sales) Evaluation",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"rounding_strategy\": \"normal\",\n    \"rounding_decimal_places\": 2,\n    \"baseline_methodology\": {\n        \"owner\": \"REBATES\",\n        \"earliest_date\": \"1900-01-01\",\n        \"record_status\": \"prod\",\n        \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n        \"effective_date\": \"2018-10-24T08:53:14.778370\",\n        \"latest_date\": null,\n        \"methodology_definition_uuid\": \"5fc9c76d-f6ad-410f-8742-33b7708e67dd\",\n        \"user_input\": \"{\\n    \\\"type\\\": \\\"amount\\\"\\n}\",\n        \"price_group_methodology_uuid\": \"6486e351-56f2-4b52-adea-529bd102e5e1\",\n        \"name\": \"Growth Baseline Submitted Values\",\n        \"description\": \"Description\",\n        \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n    }\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "de413997-291b-4332-b19c-072d6b7a1bab",
            "effective_date": "2018-10-24T09:08:19.428111",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ca7b2954-8dce-480e-b4d9-825769b844ba",
            "owner": "REBATES",
            "name": "Market Share (Gross/Net Sales) Evaluation",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"market_share_data_source_list\": \"DDD\"\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "2c78e42a-9b47-49e9-8455-27463d4d7cc9",
            "effective_date": "2018-10-24T09:08:19.861077",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ce1f3eb4-8b2b-42d6-a815-5f493d528cdb",
            "owner": "REBATES",
            "name": "Price Group Master",
            "description": "Description",
            "user_input": "{\n    \"evaluations\": [\n        {\n            \"evaluation_methodology\": {\n                \"owner\": \"REBATES\",\n                \"earliest_date\": \"1900-01-01\",\n                \"record_status\": \"prod\",\n                \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n                \"effective_date\": \"2018-10-24T08:53:14.156591\",\n                \"latest_date\": null,\n                \"methodology_definition_uuid\": \"ca7b2954-8dce-480e-b4d9-825769b844ba\",\n                \"user_input\": \"{\\n    \\\"sales_type\\\": \\\"net\\\",\\n    \\\"market_share_data_source_list\\\": \\\"DDD\\\"\\n}\",\n                \"price_group_methodology_uuid\": \"de413997-291b-4332-b19c-072d6b7a1bab\",\n                \"name\": \"Market Share (Gross/Net Sales) Evaluation\",\n                \"description\": \"Description\",\n                \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n            }\n        },\n        {\n            \"evaluation_methodology\": {\n                \"owner\": \"REBATES\",\n                \"earliest_date\": \"1900-01-01\",\n                \"record_status\": \"prod\",\n                \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n                \"effective_date\": \"2018-10-24T08:54:54.609880\",\n                \"latest_date\": null,\n                \"methodology_definition_uuid\": \"b3ff63df-b7f3-44a9-b4a8-24011bb761f3\",\n                \"user_input\": \"{\\n    \\\"sales_type\\\": \\\"net\\\",\\n    \\\"rounding_strategy\\\": \\\"normal\\\",\\n    \\\"rounding_decimal_places\\\": 2,\\n    \\\"baseline_methodology\\\": {\\n        \\\"owner\\\": \\\"REBATES\\\",\\n        \\\"earliest_date\\\": \\\"1900-01-01\\\",\\n        \\\"record_status\\\": \\\"pend\\\",\\n        \\\"price_group_uuid\\\": \\\"247d5f58-1574-42cf-94af-b4c22c4045ac\\\",\\n        \\\"effective_date\\\": \\\"2018-10-24T08:53:14.778370\\\",\\n        \\\"latest_date\\\": null,\\n        \\\"methodology_definition_uuid\\\": \\\"5fc9c76d-f6ad-410f-8742-33b7708e67dd\\\",\\n        \\\"user_input\\\": \\\"{\\\\n    \\\\\\\"type\\\\\\\": \\\\\\\"amount\\\\\\\"\\\\n}\\\",\\n        \\\"price_group_methodology_uuid\\\": \\\"6486e351-56f2-4b52-adea-529bd102e5e1\\\",\\n        \\\"name\\\": \\\"Growth Baseline Submitted Values\\\",\\n        \\\"description\\\": \\\"Description\\\",\\n        \\\"record_source_uuid\\\": \\\"bdb4af84-a616-47b5-89e5-0ad30834722d\\\"\\n    }\\n}\",\n                \"price_group_methodology_uuid\": \"4998d28b-983b-4eca-870e-5ddd361bf7c5\",\n                \"name\": \"Growth (Gross/Net Sales) Evaluation\",\n                \"description\": \"Description\",\n                \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n            }\n        }\n    ]\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "6486e351-56f2-4b52-adea-529bd102e5e1",
            "effective_date": "2018-10-24T09:08:19.592918",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "5fc9c76d-f6ad-410f-8742-33b7708e67dd",
            "owner": "REBATES",
            "name": "Growth Baseline Submitted Values",
            "description": "Description",
            "user_input": "{\n    \"type\": \"amount\"\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "089622b0-63d5-4389-9639-28c44314b7e1",
            "effective_date": "2018-10-24T09:08:19.507621",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "17f2d405-4a51-4dc1-a49b-9e37c7a13adb",
            "owner": "REBATES",
            "name": "Payment Calculation (Percent)",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"rounding_strategy\": \"normal\",\n    \"rounding_decimal_places\": 2\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        }
    ]

    price_group_methodology_new_tier_format_without_methodology_definition_uuid = [
        {
            "price_group_methodology_uuid": "85f085ee-4b4f-49e3-a4d2-ae68d2258323",
            "effective_date": "2018-10-24T09:08:19.673540",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": None,
            "owner": "REBATES",
            "name": "Multi-Parameter Qualification (Percent)",
            "description": "Description",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        }
    ]

    # product_evaluation_type='aggregate'. pgm - price group methodology
    pgm_aggregate_by_product_new_tier_format = [
        {
            "price_group_methodology_uuid": "85f085ee-4b4f-49e3-a4d2-ae68d2258323",
            "effective_date": "2018-10-24T09:08:19.673540",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ba9a8889-f47e-4723-98ba-78b01e25d2fb",
            "owner": "REBATES",
            "name": "Multi-Parameter Qualification (Percent)",
            "description": "Description",
            "user_input": """
                {
                        "tiers": [
                        {
                        "tier_id": 111,
                        "tier_name": "tier_1",
                        "is_base": true,
                        "ranges": [
                            {
                                "evaluation_parameters": [
                                    {
                                        "from": 0,
                                        "to": 20
                                    }
                                ],
                                "products": [
                                    {
                                        "all_products": true
                                    }
                                ],
                                "values": [
                                    {
                                        "earliest_date": "2018-11-01",
                                        "latest_date": "2018-11-30",
                                        "value": 5
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "tier_id": 222,
                        "tier_name": "tier_2",
                        "is_base": false,
                        "ranges": [
                            {
                                "evaluation_parameters": [
                                    {
                                        "from": 20,
                                        "to": 50
                                    }
                                ],
                                "products": [
                                    {
                                        "all_products": true,
                                        "product": []
                                    }
                                ],
                                "values": [
                                    {
                                        "earliest_date": "2018-11-01",
                                        "latest_date": "2018-11-30",
                                        "value": 10
                                    }
                                ]
                            }
                        ]
                    }
                ]
                }""",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "4998d28b-983b-4eca-870e-5ddd361bf7c5",
            "effective_date": "2018-10-24T09:08:19.755232",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "b3ff63df-b7f3-44a9-b4a8-24011bb761f3",
            "owner": "REBATES",
            "name": "Growth (Gross/Net Sales) Evaluation",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"rounding_strategy\": \"normal\",\n    \"rounding_decimal_places\": 2,\n    \"baseline_methodology\": {\n        \"owner\": \"REBATES\",\n        \"earliest_date\": \"1900-01-01\",\n        \"record_status\": \"prod\",\n        \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n        \"effective_date\": \"2018-10-24T08:53:14.778370\",\n        \"latest_date\": null,\n        \"methodology_definition_uuid\": \"5fc9c76d-f6ad-410f-8742-33b7708e67dd\",\n        \"user_input\": \"{\\n    \\\"type\\\": \\\"amount\\\"\\n}\",\n        \"price_group_methodology_uuid\": \"6486e351-56f2-4b52-adea-529bd102e5e1\",\n        \"name\": \"Growth Baseline Submitted Values\",\n        \"description\": \"Description\",\n        \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n    }\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "de413997-291b-4332-b19c-072d6b7a1bab",
            "effective_date": "2018-10-24T09:08:19.428111",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ca7b2954-8dce-480e-b4d9-825769b844ba",
            "owner": "REBATES",
            "name": "Market Share (Gross/Net Sales) Evaluation",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"market_share_data_source_list\": \"DDD\"\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "2c78e42a-9b47-49e9-8455-27463d4d7cc9",
            "effective_date": "2018-10-24T09:08:19.861077",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "ce1f3eb4-8b2b-42d6-a815-5f493d528cdb",
            "owner": "REBATES",
            "name": "Price Group Master",
            "description": "Description",
            "user_input": "{\n    \"evaluations\": [\n        {\n            \"evaluation_methodology\": {\n                \"owner\": \"REBATES\",\n                \"earliest_date\": \"1900-01-01\",\n                \"record_status\": \"prod\",\n                \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n                \"effective_date\": \"2018-10-24T08:53:14.156591\",\n                \"latest_date\": null,\n                \"methodology_definition_uuid\": \"ca7b2954-8dce-480e-b4d9-825769b844ba\",\n                \"user_input\": \"{\\n    \\\"sales_type\\\": \\\"net\\\",\\n    \\\"market_share_data_source_list\\\": \\\"DDD\\\"\\n}\",\n                \"price_group_methodology_uuid\": \"de413997-291b-4332-b19c-072d6b7a1bab\",\n                \"name\": \"Market Share (Gross/Net Sales) Evaluation\",\n                \"description\": \"Description\",\n                \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n            }\n        },\n        {\n            \"evaluation_methodology\": {\n                \"owner\": \"REBATES\",\n                \"earliest_date\": \"1900-01-01\",\n                \"record_status\": \"prod\",\n                \"price_group_uuid\": \"247d5f58-1574-42cf-94af-b4c22c4045ac\",\n                \"effective_date\": \"2018-10-24T08:54:54.609880\",\n                \"latest_date\": null,\n                \"methodology_definition_uuid\": \"b3ff63df-b7f3-44a9-b4a8-24011bb761f3\",\n                \"user_input\": \"{\\n    \\\"sales_type\\\": \\\"net\\\",\\n    \\\"rounding_strategy\\\": \\\"normal\\\",\\n    \\\"rounding_decimal_places\\\": 2,\\n    \\\"baseline_methodology\\\": {\\n        \\\"owner\\\": \\\"REBATES\\\",\\n        \\\"earliest_date\\\": \\\"1900-01-01\\\",\\n        \\\"record_status\\\": \\\"pend\\\",\\n        \\\"price_group_uuid\\\": \\\"247d5f58-1574-42cf-94af-b4c22c4045ac\\\",\\n        \\\"effective_date\\\": \\\"2018-10-24T08:53:14.778370\\\",\\n        \\\"latest_date\\\": null,\\n        \\\"methodology_definition_uuid\\\": \\\"5fc9c76d-f6ad-410f-8742-33b7708e67dd\\\",\\n        \\\"user_input\\\": \\\"{\\\\n    \\\\\\\"type\\\\\\\": \\\\\\\"amount\\\\\\\"\\\\n}\\\",\\n        \\\"price_group_methodology_uuid\\\": \\\"6486e351-56f2-4b52-adea-529bd102e5e1\\\",\\n        \\\"name\\\": \\\"Growth Baseline Submitted Values\\\",\\n        \\\"description\\\": \\\"Description\\\",\\n        \\\"record_source_uuid\\\": \\\"bdb4af84-a616-47b5-89e5-0ad30834722d\\\"\\n    }\\n}\",\n                \"price_group_methodology_uuid\": \"4998d28b-983b-4eca-870e-5ddd361bf7c5\",\n                \"name\": \"Growth (Gross/Net Sales) Evaluation\",\n                \"description\": \"Description\",\n                \"record_source_uuid\": \"bdb4af84-a616-47b5-89e5-0ad30834722d\"\n            }\n        }\n    ]\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "6486e351-56f2-4b52-adea-529bd102e5e1",
            "effective_date": "2018-10-24T09:08:19.592918",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "5fc9c76d-f6ad-410f-8742-33b7708e67dd",
            "owner": "REBATES",
            "name": "Growth Baseline Submitted Values",
            "description": "Description",
            "user_input": "{\n    \"type\": \"amount\"\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        },
        {
            "price_group_methodology_uuid": "089622b0-63d5-4389-9639-28c44314b7e1",
            "effective_date": "2018-10-24T09:08:19.507621",
            "price_group_uuid": "247d5f58-1574-42cf-94af-b4c22c4045ac",
            "methodology_definition_uuid": "17f2d405-4a51-4dc1-a49b-9e37c7a13adb",
            "owner": "REBATES",
            "name": "Payment Calculation (Percent)",
            "description": "Description",
            "user_input": "{\n    \"sales_type\": \"gross\",\n    \"rounding_strategy\": \"normal\",\n    \"rounding_decimal_places\": 2\n}",
            "earliest_date": "1900-01-01",
            "latest_date": None,
            "record_status": "prod",
            "record_source_uuid": "bdb4af84-a616-47b5-89e5-0ad30834722d"
        }
    ]


class UserObjectMock:
    registry_data = {
        "roles": ["rf-sales-analyst"],
        "profile": {
            "firstName": "test_user_first_name",
            "lastName": "test_user_last_name",
            "login": "test_user_first_name@somedomain.com",
        },
    }
