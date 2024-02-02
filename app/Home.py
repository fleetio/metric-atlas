import streamlit as st
from streamlit.logger import get_logger
from streamlit_extras import app_logo
from metric_atlas.helpers.models.MiniMetric import MiniMetric
from metric_atlas.SidebarLinks import SidebarLinks
from metric_atlas.Config import Config
import metric_atlas.Formatters as Formatters

import metric_atlas.helpers.helpers as helpers

LOGGER = get_logger(__name__)

configuration = Config()

key_metrics = []
for metric in configuration.home_page_key_metrics:
    key_metrics.append(
        MiniMetric(
            metric_category=metric.get("category"),
            metric_name=metric.get("name"),
        )
    )


def run():
    st.experimental_set_query_params()
    st.set_page_config(page_title=configuration.name, layout="wide")
    app_logo.add_logo(
        configuration.logo_url,
    )

    with st.sidebar:
        SidebarLinks(configuration.sidebar_links).render()

    st.header(configuration.name)
    key_metrics_tab, how_to_tab = st.tabs(
        ["Key Metrics", "How to Use Metrics Explorer"]
    )

    with key_metrics_tab:
        select_col1, select_col2, select_col3 = st.columns(3)

        with select_col1:
            time_grain = st.selectbox(
                "Time Grain",
                ["day", "week", "month", "quarter", "year"],
                index=2,
                format_func=Formatters.init_cap,
                key="time_grain",
                args=("time_grain",),
            )

        with select_col2:
            standard_time_period_options = helpers.standard_periods(time_grain)
            time_period = st.selectbox(
                "Time Period",
                standard_time_period_options,
                format_func=Formatters.get_label,
                key="time_period",
                args=("time_period",),
            )

        with select_col3:
            show_incomplete_periods = st.selectbox(
                "Show Incomplete Periods?",
                [{"name": False, "label": "No"}, {"name": True, "label": "Yes"}],
                key="show_incomplete_periods",
                format_func=Formatters.get_label,
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
                            "name"
                        )
                        metric.render()
                if index == 1:
                    with col2:
                        metric.time_grain = time_grain
                        metric.time_period = time_period["name"]
                        metric.show_incomplete_periods = show_incomplete_periods.get(
                            "name"
                        )
                        metric.render()
                if index == 2:
                    with col3:
                        metric.time_grain = time_grain
                        metric.time_period = time_period["name"]
                        metric.show_incomplete_periods = show_incomplete_periods.get(
                            "name"
                        )
                        metric.render()

    with how_to_tab:
        st.write("### How to Use Metrics Explorer")
        st.markdown(
            """
        - The metrics explorer allows you to slice and filter company metrics over time in a consistent way.
        - Metrics are categorized into business domains. To explore Metrics you can jump to a specific domain using the links in the sidebar or use the Metrics Explorer to jump between metrics in any domain.
        - Metrics are visualized in a consistent format across domains and have a set of key comparisons like year-over-year, month-over-month, comparison to previous period, etc.
        - Metrics can be filtered to specific segments and can also be sliced by a particular dimension to view those slices on a single chart.
        - Each visualization has a table of data in a different formats that can be downloaded as a CSV for use in Google Sheets, Excel, Etc.
        - Please review the Loom's below to learn more about how to use Fleetio Metrics to navigate and work with metrics.
        """
        )

        how_to_navigating, how_to_explorer = st.tabs(
            ["Navigating and Finding Metrics", "Working with the Metrics Explorer"]
        )

        with how_to_navigating:
            st.markdown(
                f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0;">
                <iframe src="{configuration.how_to_videos[0].get("url")}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with how_to_explorer:
            st.markdown(
                f"""
                <div style="position: relative; padding-bottom: 56.25%; height: 0;">
                <iframe src="{configuration.how_to_videos[1].get("url")}" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    run()
