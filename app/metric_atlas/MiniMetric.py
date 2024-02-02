from datetime import timedelta
from dataclasses import dataclass, field
from metric_atlas.helpers.models.Metric import Metric
import streamlit as st
from metric_atlas.helpers import helpers
from metric_atlas.helpers.queries import queries as query_helpers
import plotly.graph_objects as go


@dataclass
class MiniMetric:
    """
    A data class for a compact metric display including key metrics, charts, and a link to explore thge metric.
    """

    metric_category: str = None
    metric_name: str = None
    metric: Metric = None
    label: str = None
    time_grain: str = "month"
    time_period: str = "last_six_periods"
    show_incomplete_periods: bool = False
    filters: list = field(default_factory=lambda: [])

    def __post_init__(self):
        # Set Metric from Metric Category and Metric Name
        if self.metric is None:
            metrics = helpers.get_metric_definition(self.metric_category)
            metric_list = [
                metric for metric in metrics if metric.name == self.metric_name
            ]
            if len(metric_list) > 0:
                self.metric = metric_list[0]

        # Set Label
        if self.label is None and self.metric is not None:
            self.label = self.metric.label

    def get_data(self):
        """
        A method that returns the data for the metric.
        Args:
            self: The class instance.
        Returns:
            A dataframe for the metric.
        """
        time_periods = helpers.standard_periods(self.time_grain)
        time_period = [
            time_period
            for time_period in time_periods
            if time_period["name"] == self.time_period
        ][0]
        start_date = time_period["start_date"]
        end_date = time_period["end_date"]
        end_of_period = helpers.period_start_end_date(end_date, self.time_grain)

        if self.show_incomplete_periods or self.metric.is_cumulative_metric:
            query_end_date = time_period["end_date"]
        else:
            query_end_date = end_of_period[0] - timedelta(days=1)

        is_mid_period = False if end_of_period[1] == query_end_date else True

        # Filters
        filters = []
        for filter in self.filters:
            filter_dict = {
                "field": filter.field,
                "label": filter.label,
                "filter_values": filter.filter_values,
            }
            filters.append(filter_dict)

        # Get Metric Data
        query = query_helpers.generate_query(
            self.metric.schema,
            self.metric.model,
            self.metric.timestamp,
            self.time_grain,
            start_date,
            query_end_date,
            metrics=[self.metric],
            filters=filters,
            is_mid_period=is_mid_period,
        )

        data = query_helpers.run_query(query)

        return data

    def create_chart(self):
        metric = self.metric
        data_frame = self.get_data()
        time_grain = self.time_grain

        time_period = data_frame["Period Started On"]
        current_period = data_frame[metric.label]

        line_chart = go.Figure()

        # Format Labels
        if metric.type == "currency":
            label_format = "%{y:$,.2f}"
        elif metric.type == "percentage":
            label_format = "%{y:.2%}"
        else:
            label_format = "%{y:,}"

        # Current Period Metric
        line_chart.add_trace(
            go.Scatter(
                x=time_period,
                y=current_period,
                name=metric.label,
                texttemplate=label_format,
                mode="lines+text",
                yaxis="y1",
                line=dict(color="#3498db", width=3),
            )
        )

        # Formatting
        line_chart.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=25, b=0),
            xaxis=dict(title=time_grain.capitalize(), showgrid=False),
            yaxis=dict(title=metric.label, showgrid=False),
            plot_bgcolor="white",
            hovermode="x unified",
            showlegend=False,
        )

        line_chart.update_traces(textposition="top left")

        return line_chart

    def render(self):
        """
        A method that renders the mini metric.
        Args:
            self: The class instance.
        Returns:
            st.container() with the mini metric display.
        """

        mini_metric = st.container()

        if self.metric is not None:
            data = self.get_data()

            # Line Chart
            line_chart = self.create_chart()

            # Standard Metrics
            current_value = data[self.metric.label].iloc[0] or 0
            previous_value = data[self.metric.label].iloc[1] or 0
            delta = current_value - previous_value
            delta_pct = delta / previous_value if previous_value != 0 else 0

            current_period = helpers.format_number(
                current_value,
                self.metric.type,
                include_plus=False,
                is_inverted=self.metric.is_inverted,
            )

            delta_amount = helpers.format_number(
                delta,
                self.metric.type,
                include_plus=True,
                is_inverted=self.metric.is_inverted,
            )

            delta_pct_change = helpers.format_number(
                delta_pct,
                "percentage",
                include_plus=True,
                is_inverted=self.metric.is_inverted,
            )

            # Set Filter Params
            if self.filters != []:
                for filter in self.filters:
                    filter_params = []
                    for filter_value in filter.filter_values:
                        filter_param = f"{filter.field}={filter_value}"
                        filter_params.append(filter_param)
                    filter_params = "&".join(filter_params)
                    filter_params = f"&{filter_params}"
            else:
                filter_params = ""

            # URL
            url = f"/Metrics_Explorer?category={self.metric.category}&metric={self.metric.name}&time_grain={self.time_grain}&time_period={self.time_period}{filter_params}"

            # Button Styling
            button_css = """
                display: block;
                width: 100%;
                border: 1px solid #888;
                border-radius: 5px;
                color: #000;
                background-color: #fff;
                padding: 7px;
                font-size: 1em;
                cursor: pointer;
                text-align: center;
            """

            # Trend Color
            if self.metric.is_inverted is True:
                trend_color = "inverse"
            else:
                trend_color = "normal"

            # Period Comparison Label
            comparison_label_abbrev = (
                f"{self.time_grain[0].capitalize()}o{self.time_grain[0].capitalize()}"
            )

            with mini_metric:
                col1, col2 = st.columns([2, 1])

                col2.write(
                    f"""
                <a style='text-decoration: none; margin:0px;' href='{url}'><button style="{button_css}">Explore Metric</button></a>
                """,
                    unsafe_allow_html=True,
                )

                col1.metric(
                    self.label,
                    current_period,
                    delta=f"{delta_amount} | {delta_pct_change} {comparison_label_abbrev}",
                    help=f"{self.metric.description}",
                    delta_color=trend_color,
                )

                st.plotly_chart(line_chart, use_container_width=True)
                st.markdown("***")
        else:
            mini_metric.markdown("##### Unable to display this metric.")

        return mini_metric
