from dataclasses import dataclass
from metric_atlas.helpers.models.Metric import Metric
from metric_atlas.helpers import helpers
import streamlit as st


@dataclass
class MetricList:
    """
    A dataclass to list the metrics in a given domain.
    """

    domain: str
    metrics: list[Metric] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = helpers.get_metric_definition(self.domain)

    def render(self):
        """
        A method that displays metrics within a domain.
        Args:
            self: The class instance.
        Returns:
            A st.container() component for metrics within a domain.
        """

        container = st.container()

        for metric in self.metrics:
            st.markdown(
                f"""
            <a href="/Metrics_Explorer?category={metric.category}&metric={metric.name}">{metric.label}</a> - {metric.description}
            """,
                unsafe_allow_html=True,
            )

        return container
