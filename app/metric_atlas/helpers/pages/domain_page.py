import streamlit as st
from streamlit_extras import app_logo
import metric_atlas.helpers.formatters as format_helpers
import metric_atlas.helpers.helpers as helpers
from metric_atlas.helpers.models.HelpfulLinks import HelpfulLinks
from metric_atlas.helpers.models.MetricList import MetricList
import metric_atlas.Config as config
from metric_atlas.helpers.models.MiniMetric import MiniMetric


def generate_domain_page(domain):
    # Get rid of Existing URL Params
    st.experimental_set_query_params()

    # Streamlit configs
    st.set_page_config(layout="wide")

    app_logo.add_logo(
        "https://drive.google.com/uc?id=1wdIbZ6_nrCe2YK-G9pLj1q28LUBJU-9b"
    )

    configuration = config.config()

    metric_category = [
        m for m in configuration.metric_categories if m.get("name") == domain
    ]

    key_metrics = []
    for metric in metric_category[0].get("key_metrics"):
        key_metrics.append(
            MiniMetric(
                metric_category=metric.get("category"),
                metric_name=metric.get("name"),
            )
        )

    with st.sidebar:
        HelpfulLinks().render()

    # Content
    st.header(domain.capitalize())
    st.subheader

    key_metrics_tab, metric_list_tab = st.tabs(
        ["Key Metrics", f"All {domain.capitalize()} Metrics"]
    )

    with key_metrics_tab:
        select_col1, select_col2, select_col3 = st.columns(3)

        with select_col1:
            time_grain = st.selectbox(
                "Time Grain",
                ["day", "week", "month", "quarter", "year"],
                index=2,
                format_func=format_helpers.init_cap,
                key="time_grain",
                args=("time_grain",),
            )

        with select_col2:
            standard_time_period_options = helpers.standard_periods(time_grain)
            time_period = st.selectbox(
                "Time Period",
                standard_time_period_options,
                format_func=format_helpers.get_label,
                key="time_period",
                args=("time_period",),
            )

        with select_col3:
            show_incomplete_periods = st.selectbox(
                "Show Incomplete Periods?",
                [{"name": False, "label": "No"}, {"name": True, "label": "Yes"}],
                key="show_incomplete_periods",
                format_func=format_helpers.get_label,
                args=("show_incomplete_periods",),
            )

        st.markdown("***")

        col1, col2, col3 = st.columns(3)

        for i in range(0, len(key_metrics), 3):
            chunk = key_metrics[i : i + 3]
            for index, metric in enumerate(chunk):
                if index == 0:
                    with col1:
                        metric.time_grain = time_grain
                        metric.time_period = time_period["name"]
                        metric.show_incomplete_periods = show_incomplete_periods.get(
                            "name", False
                        )
                        metric.render()
                if index == 1:
                    with col2:
                        metric.time_grain = time_grain
                        metric.time_period = time_period["name"]
                        metric.show_incomplete_periods = show_incomplete_periods.get(
                            "name", False
                        )
                        metric.render()
                if index == 2:
                    with col3:
                        metric.time_grain = time_grain
                        metric.time_period = time_period["name"]
                        metric.show_incomplete_periods = show_incomplete_periods.get(
                            "name", False
                        )
                        metric.render()

    with metric_list_tab:
        MetricList(domain).render()
