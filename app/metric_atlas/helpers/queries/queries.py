import streamlit as st
import metric_atlas.helpers.helpers as helpers
import snowflake.connector
from jinja2 import Environment, FileSystemLoader, select_autoescape
import duckdb
from metric_atlas.Config import Config

env = Environment(loader=FileSystemLoader(""), autoescape=select_autoescape())


def generate_query(
    schema,
    table,
    date_field,
    time_grain,
    start_date,
    end_date,
    metrics=[],
    filters=[],
    is_mid_period=False,
):
    periods_per_year = {"day": 365, "week": 52, "month": 12, "quarter": 4, "year": 1}

    # Calculate the number of days into the current period.
    current_period_start = helpers.period_start_end_date(end_date, time_grain)[0]
    days_into_current_period = (end_date - current_period_start).days + 1

    if metrics[0].is_pre_aggregated is True:
        template = env.get_template(
            "metric_atlas/helpers/queries/metrics_query_pre_aggregated.sql"
        )
    else:
        template = env.get_template("metric_atlas/helpers/queries/metrics_query.sql")

    non_null_filters = [x for x in filters if len(x["filter_values"]) > 0]

    rendered_template = template.render(
        schema=schema,
        table=table,
        date_field=date_field,
        time_grain=time_grain,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        periods_per_year=periods_per_year[time_grain],
        filter_count=len(non_null_filters),
        filters=non_null_filters,
        is_mid_period=is_mid_period,
        days_into_current_period=days_into_current_period,
    )

    return rendered_template


def generate_slice_query(
    schema,
    table,
    date_field,
    time_grain,
    start_date,
    end_date,
    metrics=[],
    dimensions=[],
    filters=[],
):
    periods_per_year = {"day": 365, "week": 52, "month": 12, "quarter": 4, "year": 1}

    template = env.get_template("metric_atlas/helpers/queries/slice_query.sql")

    non_null_filters = [x for x in filters if len(x["filter_values"]) > 0]

    rendered_template = template.render(
        schema=schema,
        table=table,
        date_field=date_field,
        time_grain=time_grain,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        periods_per_year=periods_per_year[time_grain],
        filter_count=len(non_null_filters),
        filters=non_null_filters,
        dimensions=dimensions,
    )

    return rendered_template


@st.cache_resource(show_spinner=False)
def snowflake_connection():
    conn = snowflake.connector.connect(
        **st.secrets["snowflake"], client_session_keep_alive=True
    )

    return conn


@st.cache_data(ttl=600, show_spinner=False)
def run_query(query, data_frame=True):
    configuration = Config()

    if configuration.enable_sample_data_mode:
        connection = duckdb.connect("db/sample_data.db")

        if data_frame is True:
            data = connection.sql(query).df()
        else:
            data = connection.sql(query).fetchall()

    else:
        connection = snowflake_connection()

        cur = connection.cursor(snowflake.connector.DictCursor)

        try:
            if data_frame is True:
                data = cur.execute(query).fetch_pandas_all()
            else:
                data = cur.execute(query).fetchall()
        finally:
            cur.close()

    return data


def generate_options_query(schema, table, filters):
    template = env.get_template("metric_atlas/helpers/queries/options_query.sql")

    rendered_template = template.render(schema=schema, table=table, filters=filters)

    return rendered_template
