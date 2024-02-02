import streamlit as st
from streamlit_extras import app_logo
import metric_atlas.helpers.helpers as helpers
import metric_atlas.helpers.metrics.standard_metrics as metrics_helpers
import metric_atlas.helpers.charts.charts as chart_helpers
import metric_atlas.helpers.queries.queries as query_helpers
import metric_atlas.helpers.queries.query_params as query_param_helpers
import metric_atlas.helpers.formatters as format_helpers
import pandas as pd
from streamlit_pandas_profiling import st_profile_report


def generate_page():
    # Get and build URL params
    query_params = st.experimental_get_query_params()
    session_state = st.session_state

    # Streamlit configs
    st.set_page_config(layout="wide")

    app_logo.add_logo(
        "https://drive.google.com/uc?id=1wdIbZ6_nrCe2YK-G9pLj1q28LUBJU-9b"
    )

    # Callback
    def callback_state(key=None):
        """
        Callback function for handling changed in side bar selections.
        Params: key, the key value of the changed input
        Returns: Logs changed input key.
        """
        key = key

    # Get Metric Definition
    metric_categories = helpers.get_metric_categories()

    # Set Values from URL Params if Session State is Not Set
    if session_state == {}:
        param_values = query_param_helpers.get_param_values(query_params)

        # Category
        if param_values.get("category") is not None:
            st.session_state.category = param_values["category"]

        # Metric
        if param_values.get("metric") is not None:
            st.session_state.metric = param_values["metric"]

        # Time Grain
        if param_values.get("time_grain") is not None:
            st.session_state.time_grain = param_values["time_grain"]

        # Time Period
        if param_values.get("time_period") is not None:
            st.session_state.time_period = param_values["time_period"]

        # Slice By
        if param_values.get("slice_by") is not None:
            st.session_state.slice_by = param_values["slice_by"]

        # Filters
        if param_values.get("filters") is not None:
            for filter in param_values["filters"]:
                st.session_state[filter["name"]] = filter["value"]

    # Category Selectbox
    category = st.sidebar.selectbox(
        "Metric Category:",
        metric_categories,
        format_func=format_helpers.get_label,
        on_change=callback_state,
        key="category",
        args=("category",),
    )

    metrics = helpers.get_metric_definition(
        category.get("name"), category.get("sources")
    )

    # Metric Selectbox
    metric = st.sidebar.selectbox(
        "Metric:",
        metrics,
        format_func=format_helpers.get_label,
        on_change=callback_state,
        key="metric",
        args=("metric",),
    )

    # Time Grain Selectbox
    time_grain = st.sidebar.selectbox(
        "Time Grain:",
        metric.time_grains,
        format_func=format_helpers.init_cap,
        on_change=callback_state,
        key="time_grain",
        args=("time_grain",),
    )

    standard_time_period_options = helpers.standard_periods(time_grain)

    # Time Period Selectbox
    standard_time_periods = st.sidebar.selectbox(
        "Time Period:",
        standard_time_period_options,
        format_func=format_helpers.get_label,
        on_change=callback_state,
        key="time_period",
        args=("time_period",),
    )

    # Sorted Dimensions for Metric
    if metric.dimensions is not None:
        dimensions = sorted(metric.dimensions, key=lambda d: d.label)
    else:
        dimensions = []

    start_date = st.sidebar.date_input(
        "Start Date",
        standard_time_periods.get("start_date"),
        on_change=callback_state,
        key="start_date",
        args=("start_date",),
    )

    end_date = st.sidebar.date_input(
        "End Date",
        standard_time_periods.get("end_date"),
        on_change=callback_state,
        key="end_date",
        args=("end_date",),
    )

    st.sidebar.write("### Slice By")

    # Slice By Selectbox
    dimension = st.sidebar.selectbox(
        "Slice By:",
        dimensions,
        format_func=format_helpers.get_label,
        on_change=callback_state,
        key="slice_by",
        args=("slice_by",),
    )

    # Get Filter Options
    st.sidebar.write("### Filters")
    if len(metric.filters) > 1:
        option_query = query_helpers.generate_options_query(
            metric.schema, metric.model, metric.filters
        )
        raw_options = query_helpers.run_query(option_query)
        sorted_filters = sorted(metric.filters, key=lambda d: d["label"])

        filters = []

        for filter in sorted_filters:
            filtered_data = raw_options[raw_options["dimension"] == filter["name"]]
            filter_options = filtered_data["select_option"].tolist()

            # Remove items from session state if they are not in the filter options
            if st.session_state.get(filter["name"]) is not None:
                for value in st.session_state[filter["name"]]:
                    if value not in filter_options:
                        st.session_state[filter["name"]].remove(value)

            filters.append(
                {
                    "field": filter["name"],
                    "label": filter["label"],
                    "filter_values": st.sidebar.multiselect(
                        filter["label"],
                        filter_options,
                        on_change=callback_state,
                        key=filter["name"],
                    ),
                }
            )

    else:
        filters = []

    # Get Metric Data
    end_of_period = helpers.period_start_end_date(end_date, time_grain)

    is_mid_period = False if end_of_period[1] == end_date else True

    # Get Metric Data
    query = query_helpers.generate_query(
        metric.schema,
        metric.model,
        metric.timestamp,
        time_grain,
        start_date,
        end_date,
        metrics=[metric],
        filters=filters,
        is_mid_period=is_mid_period,
    )

    data = query_helpers.run_query(query)

    st.header(metric.label)

    (
        def_col1,
        def_col2,
    ) = st.columns(2)

    with def_col1:
        tab1, tab2 = st.tabs(["Business Definition", "Technical Definition"])

        with tab1:
            if metric.description:
                # st.write("**Business Description:**")
                st.write(f"**Business Description:** {metric.description}")
                # st.write("**Data Description:**")
                st.write(
                    f"**Business Owner:** [{getattr(metric.business_owner, 'name', '')}](mailto:{getattr(metric.business_owner, 'email', '')})"
                )

        with tab2:
            st.write(
                f"This metric is based on the model ``{metric.model}`` in the schema ``{metric.schema}``. The formula for this metric is ``{metric.sql}`` and it is grouped over time using ``{metric.timestamp}``."
            )
            st.write(
                f"**Data Team Owner:** [{getattr(metric.data_team_owner, 'name', '')}](mailto:{getattr(metric.data_team_owner, 'email', '')})"
            )

    with def_col2:
        # List of Applied Filter
        st.write("##### Filters")
        filter_count = 0
        for filter in filters:
            if len(filter["filter_values"]) > 0:
                st.write(f"**{filter['label']}:** {', '.join(filter['filter_values'])}")
                filter_count += 1

        if filter_count == 0:
            st.write("No filters applied")

    st.write("***")

    # Line Chart
    line_chart = chart_helpers.create_line_chart(data, metric, time_grain)
    st.plotly_chart(line_chart, use_container_width=True)

    # Metrics
    standard_metrics = metrics_helpers.create_standard_metrics(data, metric)

    tab_names = [f"Completed {time_grain.capitalize()} Metrics"]

    if standard_metrics["current_ptd"]:
        tab_names.append(f"{time_grain.capitalize()}-to-Date Metrics")

    tabs = st.tabs(tab_names)

    # Completed Period Tab
    with tabs[0]:
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            f"Latest Complete {time_grain.capitalize()}",
            helpers.format_number(standard_metrics["current_period"], metric.type),
            help=f"The metric value for the most recent completed {time_grain}.",
        )

        col2.metric(
            f"Previous Complete {time_grain.capitalize()}",
            helpers.format_number(standard_metrics["previous_period"], metric.type),
            help=f"The metric value for the previous completed {time_grain}.",
        )
        col2.metric(
            f"{time_grain.capitalize()}-over-{time_grain.capitalize()} Change",
            helpers.format_number(
                standard_metrics["period_over_period_change"],
                metric.type,
                include_plus=True,
            ),
            delta=helpers.format_number(
                standard_metrics.get("period_over_period_percent_change"),
                "percentage",
                include_plus=True,
            ),
            help=f"The amount and percent change from the previous {time_grain}.",
        )

        col3.metric(
            f"Trailing Six {time_grain.capitalize()}s",
            helpers.format_number(
                standard_metrics["trailing_six_periods"], metric.type
            ),
            help=f"The metric value six completed {time_grain}s ago.",
        )
        col3.metric(
            f"Trailing Six {time_grain.capitalize()}s Change",
            helpers.format_number(
                standard_metrics["trailing_six_periods_change"],
                metric.type,
                include_plus=True,
            ),
            delta=helpers.format_number(
                standard_metrics.get("trailing_six_periods_percent_change"),
                "percentage",
                include_plus=True,
            ),
            help=f"The amount and percent change from six {time_grain}s ago.",
        )

        col4.metric(
            "Previous Year",
            helpers.format_number(standard_metrics["last_year"], metric.type),
            help="The metric value last year.",
        )
        col4.metric(
            "Year-over-Year Change",
            helpers.format_number(
                standard_metrics["year_over_year_change"],
                metric.type,
                include_plus=True,
            ),
            delta=helpers.format_number(
                standard_metrics.get("year_over_year_percent_change"),
                "percentage",
                include_plus=True,
            ),
            help="The amount and percent change from the previous year.",
        )

        col5.metric(
            f"Three {time_grain.capitalize()} Moving Average ",
            helpers.format_number(standard_metrics["moving_average"], metric.type),
            help=f"The moving average of the metric for the last three completed {time_grain}s.",
        )
        col5.metric(
            f"Three {time_grain.capitalize()} Moving Average Change",
            helpers.format_number(
                standard_metrics["moving_average_change"],
                metric.type,
                include_plus=True,
            ),
            delta=helpers.format_number(
                standard_metrics.get("moving_average_percent_change"),
                "percentage",
                include_plus=True,
            ),
            help=f"The amount and percent change from the three {time_grain} moving average.",
        )

    # Month to Date Tab
    if len(tab_names) == 2:
        with tabs[1]:
            if metric.is_pre_aggregated is True:
                st.write(
                    f">This metric is based on pre-aggregated data and cannot be compared to the same point in the previous period. The current {time_grain}-to-date value is being compared to previous completed {time_grain}s."
                )
            else:
                st.write(
                    f">These metrics are calculated using the current {time_grain}-to-date value compared the same point in previous {time_grain}s."
                )

            col1, col2, col3, col4, col5 = st.columns(5)

            col1.metric(
                f"{time_grain.capitalize()}-to-date",
                helpers.format_number(standard_metrics["current_ptd"], metric.type),
                help=f"The metric value for the {time_grain}-to-date.",
            )

            col2.metric(
                f"Previous {time_grain.capitalize()}-to-date",
                helpers.format_number(
                    standard_metrics["previous_period_ptd"], metric.type
                ),
                help=f"The metric value at the same point in the previous {time_grain}.",
            )
            col2.metric(
                f"{time_grain.capitalize()}-over-{time_grain.capitalize()} Change",
                helpers.format_number(
                    standard_metrics["period_over_period_change_ptd"],
                    metric.type,
                    include_plus=True,
                ),
                delta=helpers.format_number(
                    standard_metrics["period_over_period_percent_change_ptd"],
                    "percentage",
                    include_plus=True,
                ),
                help=f"The amount and percent change at the same point in the previous {time_grain}.",
            )

            col3.metric(
                f"Trailing Six {time_grain.capitalize()}-to-date",
                helpers.format_number(
                    standard_metrics["trailing_six_periods_ptd"], metric.type
                ),
                help=f"The metric value at the same point six {time_grain}s ago.",
            )
            col3.metric(
                f"Trailing Six {time_grain.capitalize()}s Change",
                helpers.format_number(
                    standard_metrics["trailing_six_periods_change_ptd"],
                    metric.type,
                    include_plus=True,
                ),
                delta=helpers.format_number(
                    standard_metrics["trailing_six_periods_percent_change_ptd"],
                    "percentage",
                    include_plus=True,
                ),
                help=f"The amount and percent change at the same point six {time_grain}s ago.",
            )

            col4.metric(
                "Previous Year",
                helpers.format_number(standard_metrics["last_year_ptd"], metric.type),
                help="The metric value at the same point in this period last year.",
            )
            col4.metric(
                "Year-over-Year Change",
                helpers.format_number(
                    standard_metrics["year_over_year_change_ptd"],
                    metric.type,
                    include_plus=True,
                ),
                delta=helpers.format_number(
                    standard_metrics["year_over_year_percent_change_ptd"],
                    "percentage",
                    include_plus=True,
                ),
                help="The amount and percent change at the same point in this period in last year.",
            )

            col5.metric(
                f"Three {time_grain.capitalize()} Moving Average ",
                helpers.format_number(
                    standard_metrics["moving_average_ptd"], metric.type
                ),
                help=f"The moving average of the metric at the same point in the previous three {time_grain}s.",
            )
            col5.metric(
                f"Three {time_grain.capitalize()} Moving Average Change",
                helpers.format_number(
                    standard_metrics["moving_average_change_ptd"],
                    metric.type,
                    include_plus=True,
                ),
                delta=helpers.format_number(
                    standard_metrics["moving_average_percent_change_ptd"],
                    "percentage",
                    include_plus=True,
                ),
                help=f"The amount and percent change of the moving average at the same point in the previous three {time_grain}s.",
            )

    # Metric Table
    pivot_data, raw_data = st.tabs(["Metrics Data", "Raw Data"])
    table_data = data
    table_data.fillna(0, inplace=True)

    format_options = helpers.table_format(table_data, metric)

    with pivot_data:
        pivot_metrics = pd.pivot_table(
            format_options.get("table_data"),
            columns="Time Period",
            dropna=False,
            aggfunc=lambda x: " ".join(str(v) for v in x),
        )
        csv_pivot_data = pivot_metrics.to_csv().encode("utf-8")

        st.download_button(
            "Download Data as CSV",
            csv_pivot_data,
            f"{metric.name}_metrics_pivot.csv",
            "text/csv",
            key="download-pivot-csv",
        )

        st.dataframe(pivot_metrics)

    with raw_data:
        csv_raw_data = format_options.get("table_data").to_csv().encode("utf-8")

        st.download_button(
            "Download Data as CSV",
            csv_raw_data,
            f"{metric.name}_metrics_raw.csv",
            "text/csv",
            key="download-raw-csv",
        )

        st.dataframe(format_options.get("table_data"))

    if len(metric.dimensions) >= 1:
        # Sliced Data
        st.header(f"{metric.label} by {dimension.label}")

        slice_query = query_helpers.generate_slice_query(
            metric.schema,
            metric.model,
            metric.timestamp,
            time_grain,
            start_date,
            end_date,
            metrics=[metric],
            dimensions=[dimension],
            filters=filters,
        )

        slice_data = query_helpers.run_query(slice_query)

        # Slice Chart
        slice_line_chart = chart_helpers.create_slice_chart(
            "line", slice_data, metric, time_grain, dimension=dimension
        )

        slice_bar_chart = chart_helpers.create_slice_chart(
            "bar", slice_data, metric, time_grain, dimension=dimension
        )

        slice_by_line_chart, slice_by_bar_chart = st.tabs(["Line Chart", "Bar Chart"])

        # Slice Charts
        with slice_by_line_chart:
            st.plotly_chart(slice_line_chart, use_container_width=True)

        with slice_by_bar_chart:
            st.plotly_chart(slice_bar_chart, use_container_width=True)

        slice_by_metrics_data, slice_by_raw_data, profiled_data = st.tabs(
            ["Metrics Data", "Raw Data", "Dimension Profiling"]
        )

        # Slice Table
        with slice_by_metrics_data:
            slice_pivot_metrics = (
                slice_data.pivot(
                    index=dimension.label,
                    columns="Time Period",
                    values=metric.label,
                )
            ).fillna(0)

            formatted_data = helpers.slice_by_table_format(
                "metrics", slice_pivot_metrics, metric
            )

            csv_slice_data_pivot = slice_pivot_metrics.to_csv().encode("utf-8")

            st.download_button(
                "Download Data as CSV",
                csv_slice_data_pivot,
                f"{metric.name}_slice_pivot.csv",
                "text/csv",
                key="download-slice-pivot-csv",
            )

            st.dataframe(formatted_data)

        with slice_by_raw_data:
            csv_slice_data = slice_data.to_csv().encode("utf-8")

            st.download_button(
                "Download Data as CSV",
                csv_slice_data,
                f"{metric.name}_slice_metrics.csv",
                "text/csv",
                key="download-slice-raw_csv",
            )

            slice_raw_data_formatted = helpers.slice_by_table_format(
                "raw", slice_data, metric
            )

            st.dataframe(slice_raw_data_formatted)

        with profiled_data:
            dim_name = dimension.label
            pr = slice_data[[dim_name]].profile_report()
            st_profile_report(pr)
    else:
        st.write("There are no dimensions to slice by for this metric.")

    query_param_helpers.set_query_params_from_state(st.session_state, filters)
