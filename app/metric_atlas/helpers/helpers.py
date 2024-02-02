import yaml
import datetime
import streamlit as st
from datetime import date
from typing import List
from dateutil.relativedelta import relativedelta
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from babel.numbers import format_currency
from metric_atlas.helpers import dbt_helpers
from metric_atlas.helpers.loaders import load_metric_from_yaml
from numerize.numerize import numerize

env = Environment(loader=FileSystemLoader(""), autoescape=select_autoescape())


def period_start_end_date(input_date, time_grain):
    today = input_date
    curr_quarter = int((today.month - 1) / 3 + 1)

    dayofweek = today.weekday()

    week_start = today - relativedelta(days=dayofweek)
    week_end = week_start + relativedelta(days=6)

    month_start = date(today.year, today.month, 1)
    month_end = month_start + relativedelta(months=1, days=-1)

    quarter_start = date(today.year, 3 * curr_quarter - 2, 1)
    quarter_end = quarter_start + relativedelta(months=3, days=-1)

    year_start = date(today.year, 1, 1)
    year_end = year_start + relativedelta(years=1, days=-1)

    if time_grain == "day":
        return (input_date, input_date)
    elif time_grain == "week":
        return (week_start, week_end)
    elif time_grain == "month":
        return (month_start, month_end)
    elif time_grain == "quarter":
        return (quarter_start, quarter_end)
    elif time_grain == "year":
        return (year_start, year_end)


def standard_periods(time_grain):
    today = datetime.date.today()

    current_period = period_start_end_date(today, time_grain)

    is_mid_period = False if today == current_period[1] else True

    end_date = today

    if is_mid_period is True:
        anchor_date = current_period[0]
    else:
        anchor_date = current_period[1] + relativedelta(days=1)

    six_months_ago = anchor_date + relativedelta(months=-6)
    one_year_ago = anchor_date + relativedelta(years=-1)
    two_years_ago = anchor_date + relativedelta(years=-2)

    if time_grain == "day":
        three_periods_ago = anchor_date + relativedelta(days=-3)
        six_periods_ago = anchor_date + relativedelta(days=-6)
    elif time_grain == "week":
        three_periods_ago = anchor_date + relativedelta(weeks=-3)
        six_periods_ago = anchor_date + relativedelta(weeks=-6)
    elif time_grain == "month":
        three_periods_ago = anchor_date + relativedelta(months=-3)
        six_periods_ago = anchor_date + relativedelta(months=-6)
    elif time_grain == "quarter":
        three_periods_ago = anchor_date + relativedelta(months=-9)
        six_periods_ago = anchor_date + relativedelta(months=-18)
    elif time_grain == "year":
        three_periods_ago = anchor_date + relativedelta(years=-3)
        six_periods_ago = anchor_date + relativedelta(years=-6)

    standard_time_period_options = [
        {
            "label": "Last Six Periods",
            "name": "last_six_periods",
            "start_date": period_start_end_date(six_periods_ago, time_grain)[0],
            "end_date": end_date,
        },
        {
            "label": "Last Three Periods",
            "name": "last_three_periods",
            "start_date": period_start_end_date(three_periods_ago, time_grain)[0],
            "end_date": end_date,
        },
        {
            "label": "Last Six Months",
            "name": "last_six_months",
            "start_date": period_start_end_date(six_months_ago, time_grain)[0],
            "end_date": end_date,
        },
        {
            "label": "Last Year",
            "name": "last_year",
            "start_date": period_start_end_date(one_year_ago, time_grain)[0],
            "end_date": end_date,
        },
        {
            "label": "Last Two Years",
            "name": "last_two_years",
            "start_date": period_start_end_date(two_years_ago, time_grain)[0],
            "end_date": end_date,
        },
    ]

    return standard_time_period_options


def get_metric_categories() -> List[str]:
    """
    Returns a list of metric categories.

    Returns:
    List[str]: a list of metric categories
    """
    path = "config/config.yml"

    with open(path, "r") as stream:
        metric_yml = yaml.safe_load(stream)
        metric_categories = metric_yml["metric_categories"]

    return metric_categories


def get_metric_definition(
    category_name: str, metric_source: List[str] = ["metric_map"]
) -> List[dict]:
    """Returns a list of metric definitions for the given category whether they are defined in fleetio_metrics or dbt_metrics.

    Args:
        category_name(str): A string representing the name of the category for which to retrieve the metric definitions.
        metric_source(List[str], optional): A list of strings representing the sources of the metric definitions. By default, only 'fleetio_metrics' source is used.

    Returns:
        A list of metric definitions sorted by their label

    Raises:
        FileNotFoundError: If the file for the specified category is not found in the metrics_definitions directory.
    """

    metric_definitions = []

    if "dbt_metrics" in metric_source:
        dbt_metric_definitions = dbt_helpers.get_supported_dbt_cloud_metric_definitions(
            category_name
        )
        metric_definitions += dbt_metric_definitions

    if "metric_map" in metric_source:
        # load yaml to dataclass
        yaml_metrics = load_metric_from_yaml(f"config/{category_name}.yml")

        # drop metrics already defined in dbt_metrics. TODO: maybe use set operation here instead of list comprehension
        unique_fleetio_metric_definitions = [
            metric
            for metric in yaml_metrics
            if metric.name not in [m["name"] for m in metric_definitions]
        ]
        metric_definitions += unique_fleetio_metric_definitions

    sorted_metrics = sorted(metric_definitions, key=lambda d: d.label)

    return sorted_metrics


def table_format(table_data, metric_definition):
    """
    Function to format items in tables
    Params: table_data(DataFrame), the data from the DataFrame
            metric_definition(dict), The defintiion of the selected metric
    Returns: dict, the formatted table with corresponding column options
    """

    metric_label = metric_definition.label
    metric_type = metric_definition.type
    standard_metrics = [
        metric_label,
        f"{metric_label} Previous Period",
        f"{metric_label} Trailing Six Periods",
        f"{metric_label} Previous Year",
        f"{metric_label} Three Period Moving Average",
        f"{metric_label} Previous Period Change",
        f"{metric_label} Trailing Six Periods Change",
        f"{metric_label} Previous Year Change",
        f"{metric_label} Three Period Moving Average Change",
    ]
    standard_percent_metrics = [
        f"{metric_label} Previous Period % Change",
        f"{metric_label} Trailing Six Periods % Change",
        f"{metric_label} Previous Year % Change",
        f"{metric_label} Three Period Moving Average % Change",
    ]
    standard_integer_columns = ["Days Into Period"]
    standard_date_columns = ["Period Started On", "Period Ended On"]
    columns = list(table_data.keys())

    for item in columns:
        if item in standard_date_columns:
            table_data[item] = table_data[item]
        elif item in standard_integer_columns:
            table_data[item] = table_data[item].astype(int)
        elif item in standard_percent_metrics:
            table_data[item] = round(pd.to_numeric(table_data[item]) * 100, 2)
            table_data[item] = table_data[item].apply(lambda x: str(x) + "%")
        elif item in standard_metrics:
            if metric_type == "currency":
                table_data[item] = table_data[item].apply(
                    lambda x: format_currency(x, "USD", locale="en_US")
                )
            elif metric_type == "percentage":
                table_data[item] = round(pd.to_numeric(table_data[item]) * 100, 2)
                table_data[item] = table_data[item].apply(lambda x: str(x) + "%")
            elif metric_type == "count":
                table_data[item] = pd.to_numeric(table_data[item]).round().astype(int)
            else:
                table_data[item] = table_data[item]
        else:
            table_data[item] = table_data[item]

    return {"table_data": table_data}


def slice_by_table_format(type, dataframe, metric_definition):
    """
    Function to format items in tables
    Params: table_data(DataFrame), the data from the DataFrame
            metric_definition(dict), The defintiion of the selected metric
    Returns: dict, the formatted table with corresponding column options
    """
    metric_type = metric_definition.type
    metric_label = metric_definition.label

    if type == "metrics":
        if metric_type == "currency":
            output_data = dataframe.style.format("${:,.2f}")
        elif metric_type == "percentage":
            output_data = dataframe.style.format("{:.2%}")
        elif metric_type == "count":
            output_data = dataframe.style.format("{:,.0f}")
        else:
            output_data = dataframe

    elif type == "raw":
        column_format = {}

        if metric_type == "currency":
            column_format[metric_label] = "${:,.2f}"
            output_data = dataframe.style.format(column_format)
        elif metric_type == "percentage":
            column_format[metric_label] = "{:.2%}"
            output_data = dataframe.style.format(column_format)
        elif metric_type == "count":
            column_format[metric_label] = "{:,.0f}"
            output_data = dataframe.style.format(column_format)
        else:
            output_data = dataframe

    return output_data


def empty_string_if_error(path_to_value):
    try:
        path_to_value
        value = path_to_value
    except Exception as e:
        print(e)
        value = ""

    return value


@st.cache_data
def cached_metrics() -> List:
    """
    Function to cache metrics
    Params: None
    Returns: File
    """
    metrics_list = []
    for category in get_metric_categories():
        metrics = get_metric_definition(category["name"])
        for metric in metrics:
            metric_data = {
                "category": metric.category,
                "name": metric.name,
                "label": metric.label,
                "description": metric.description,
                "search_label": f"{metric.category.capitalize()} | {metric.label}",
                "url": f"Metrics_Explorer?category={metric.category}&metric={metric.name}",
            }

            metrics_list.append(metric_data)

    return metrics_list


def populate_search_box_options(search_term) -> List:
    # TODO: make it able to pull from semantic layer
    metrics = cached_metrics()
    metrics_result = [
        (metric["search_label"], metric)
        for metric in metrics
        if search_term in metric["search_label"].lower()
    ]
    return metrics_result


def format_number(number, type, include_plus=False, is_inverted=False):
    """
    Function to format numbers to compact format
    Params: number(int), the number to be formatted
    Returns: str, the formatted number
    """
    is_negative = True if number < 0 else False
    number = abs(float(number))

    if number > 9999 or number < -9999:
        raw_number = numerize(float(number))
        is_compact = True
    else:
        raw_number = number
        is_compact = False

    if type == "currency":
        if is_compact is True:
            formatted_number = f"${raw_number}"
        else:
            formatted_number = format_currency(raw_number, "USD", locale="en_US")

    elif type == "percentage":
        formatted_number = f"{raw_number:.2%}"

    else:
        if is_compact is True:
            formatted_number = raw_number
        else:
            formatted_number = f"{raw_number:,.0f}"

    if is_negative is True:
        sign = "-"
    else:
        sign = "+"

    formatted_number = f"{sign}{formatted_number}"

    if is_inverted is True:
        if "-" in formatted_number:
            result = formatted_number.replace("-", "+")
        elif "+" in formatted_number:
            result = formatted_number.replace("+", "-")
        else:
            result = formatted_number
    else:
        result = formatted_number

    if include_plus is False:
        result = result.replace("+", "")

    return result
