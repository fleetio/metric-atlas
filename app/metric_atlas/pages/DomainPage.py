import streamlit as st
from streamlit_extras import app_logo
import metric_atlas.Formatters as Formatters
from metric_atlas.SidebarLinks import SidebarLinks
from metric_atlas.MetricList import MetricList
from metric_atlas.Config import Config
from metric_atlas.MiniMetric import MiniMetric
from dataclasses import dataclass

# To Replace
import metric_atlas.helpers.helpers as helpers


@dataclass
class DomainPage:
    domain: str
    domain_label: str = None
    domain_description: str = None
    key_metrics: list[MiniMetric] = None

    def __post_init__(self):
        configuration = Config()
        domain_config = [
            m for m in configuration.metric_categories if m.get("name") == self.domain
        ]

        self.domain_label = domain_config[0].get("label")
        self.domain_description = domain_config[0].get("description")
        key_metrics = []
        for metric in domain_config[0].get("key_metrics"):
            key_metrics.append(
                MiniMetric(
                    metric_category=metric.get("category"),
                    metric_name=metric.get("name"),
                )
            )
        self.key_metrics = key_metrics

    def render(self):
        configuration = Config()

        # Get rid of Existing URL Params
        st.experimental_set_query_params()

        # Streamlit configs
        st.set_page_config(layout="wide")

        app_logo.add_logo(configuration.logo_url)

        with st.sidebar:
            SidebarLinks(configuration.sidebar_links).render()

        # Content
        st.header(self.domain_label)
        st.write(self.domain_description)

        key_metrics_tab, metric_list_tab = st.tabs(
            [f"Key {self.domain_label} Metrics", f"All {self.domain_label} Metrics"]
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

            for i in range(0, len(self.key_metrics), 3):
                chunk = self.key_metrics[i : i + 3]
                for index, metric in enumerate(chunk):
                    if index == 0:
                        with col1:
                            metric.time_grain = time_grain
                            metric.time_period = time_period["name"]
                            metric.show_incomplete_periods = (
                                show_incomplete_periods.get("name", False)
                            )
                            metric.render()
                    if index == 1:
                        with col2:
                            metric.time_grain = time_grain
                            metric.time_period = time_period["name"]
                            metric.show_incomplete_periods = (
                                show_incomplete_periods.get("name", False)
                            )
                            metric.render()
                    if index == 2:
                        with col3:
                            metric.time_grain = time_grain
                            metric.time_period = time_period["name"]
                            metric.show_incomplete_periods = (
                                show_incomplete_periods.get("name", False)
                            )
                            metric.render()

        with metric_list_tab:
            MetricList(self.domain).render()
