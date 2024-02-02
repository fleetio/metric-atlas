import streamlit as st
from dbt_metadata_client.client import Client
from dbt_metadata_client.dbt_metadata_api_schema import MetricNode
from typing import List, Dict
from metric_atlas.helpers.models.Metric import Metric


def dbt_cloud_connection():
    client = Client(api_token=st.secrets.dbt_cloud.dbt_api_key)
    return client


def format_dimensions_block(metric: MetricNode) -> List[Dict[str, str]]:
    """
    Takes the dimenstions and dimension labels configured in dbt_metrics meta tag and formats it according to how
    fleetio metrics expects the format to be.

    Args:
        metric (MetricNode): A dbt metric node that contains dimensions and metadata about labels.

    Returns:
        A list of dictionaries, where each dictionary represents a dimension and has the following keys:
            - name (str): The name of the dimension.
            - label (str): The label of the dimension, as defined in the dbt model's meta.dimension_labels.

    Raises:
        N/A
    """
    dimensions = metric.dimensions
    dimension_labels = getattr(metric, "meta.dimension_labels", [])
    dim_list = []
    for dim in dimensions:
        label = next(
            (
                dim_label.label
                for dim_label in dimension_labels
                if dim_label.name == dim
            ),
            dim,
        )
        dim_list.append({"name": dim, "label": label})
    return dim_list


def format_sql_block(metric: MetricNode) -> str:
    """
    Formats a dbt metric node's spec and converts the sql into fleetio metrics format.

    Args:
        metric (MetricNode): A dbt metric node.

    Returns:
        A formatted SQL string that represents that conforms to fleetio_metric format.

    Raises:
        N/A
    """
    calculation_method = metric.calculation_method
    filters = getattr(metric, "filters", None)
    sql = str(metric.sql)
    config = getattr(metric, "config", None)

    # Determine the function prefix and postfix based on the calculation method and filters.
    # TODO: will need to make this more robust to handle multiple filters and different combinations
    if calculation_method == "count" and filters:
        function_prefix = "count_if("
    else:
        function_prefix = f"{calculation_method}("
    function_postfix = ")"

    # Determine the null prefix and postfix based on the "treat null values as zero" config.
    null_prefix = "zeroifnull(" if config and config.treat_null_values_as_zero else ""
    null_postfix = ")" if config and config.treat_null_values_as_zero else ""

    # Combine the prefixes, SQL statement, and postfixes into a single string.
    sql_stmt = f"{null_prefix}{function_prefix}metric_source.{sql}{function_postfix}{null_postfix}"
    return sql_stmt


def generate_fleetio_metric_yml_fmt(dbt_metric: MetricNode) -> Metric:
    """
    Formats a dbt MetricNode object according to fleetio metric spec. Also attaches info on whether this dbt_metric
    came from an externally sourced dbt package

    Args:
        dbt_metric: The dbt MetricNode object to format.

    Returns:
        A dictionary containing the relevant attributes of the dbt_metric object, formatted for use in a YAML file.
    """
    # Extract relevant attributes from the MetricNode object.
    business_owner = getattr(dbt_metric.meta, "business_owner.name", "")
    data_team_owner = getattr(dbt_metric.meta, "data_team_owner.name", "")
    category = getattr(dbt_metric.meta, "category", "")
    description = dbt_metric.description
    dimensions = format_dimensions_block(dbt_metric)
    label = dbt_metric.label
    model_alias = dbt_metric.model.alias
    model_schema = dbt_metric.model.schema
    name = dbt_metric.name
    sql = format_sql_block(dbt_metric)
    filters = getattr(dbt_metric, "filters", [])
    time_grains = getattr(dbt_metric, "time_grains", [])
    timestamp = dbt_metric.timestamp
    type = dbt_metric.calculation_method
    external_package_metric = dbt_metric.package_name != "dbt_models"

    # Create Metric Object

    fleetio_metric_obj = Metric(
        name=name,
        type=type,
        category=category,
        schema=model_schema,
        model=model_alias,
        description=description,
        sql=sql,
        timestamp=timestamp,
        business_owner=business_owner,
        data_team_owner=data_team_owner,
        filters=filters,
        time_grains=time_grains,
        dimensions=dimensions,
        label=label,
        external_package_metric=external_package_metric,
    )

    return fleetio_metric_obj


def get_supported_dbt_cloud_metric_definitions(category: str = "") -> List[dict]:
    """
    Returns a list of supported metrics from the dbt cloud semantic layer formatted to fit
    into the fleetio_metric spec.

    Right now, we don't handle derived metrics

    Args:
    category (str, optional): the category to filter the metrics by

    Returns:
    List[dict]: a list of supported dbt cloud metric definitions
    """
    conn = dbt_cloud_connection()
    metrics: List[MetricNode] = conn.get_metrics(job_id=st.secrets.dbt_cloud.dbt_job_id)

    # We cannot handle derived metrics so lets filter those out
    supported_metrics = [
        generate_fleetio_metric_yml_fmt(metric)
        for metric in metrics
        if metric.type != "derived"
    ]
    if category == "external_dbt_packages":
        return [
            metric for metric in supported_metrics if metric.external_package_metric
        ]
    elif category == "finance":
        return [
            metric for metric in supported_metrics if not metric.external_package_metric
        ]  # hardcoded for now as no real metrics to test with
    elif category != "":
        return [metric for metric in supported_metrics if metric.category == category]
    else:
        return supported_metrics
