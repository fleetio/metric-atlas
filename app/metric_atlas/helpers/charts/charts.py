import plotly.express as px
import plotly.graph_objects as go


def create_line_chart(
    data_frame,
    metric,
    time_grain,
    legend=True,
    title=True,
    grid=True,
    y2=True,
    show_previous_year=True,
):
    time_period = data_frame["Period Started On"]
    current_period = data_frame[metric.label]
    previous_period = data_frame[f"{metric.label} Previous Period"]
    six_periods = data_frame[f"{metric.label} Trailing Six Periods"]
    previous_year = data_frame[f"{metric.label} Previous Year"]
    previous_year_change = data_frame[f"{metric.label} Previous Year % Change"]
    previous_period_change = data_frame[f"{metric.label} Previous Period % Change"]
    six_periods_change = data_frame[f"{metric.label} Trailing Six Periods % Change"]
    moving_average = data_frame[f"{metric.label} Three Period Moving Average"]
    moving_average_change = data_frame[
        f"{metric.label} Three Period Moving Average % Change"
    ]

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
            mode="lines+markers+text",
            yaxis="y1",
            line=dict(color="#3498db", width=3),
        )
    )

    if show_previous_year is True:
        trace_visibility = None
    else:
        trace_visibility = "legendonly"

    # Previous Year
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=previous_year,
            name=f"{metric.label} Previous Year",
            visible=trace_visibility,
            mode="lines",
            yaxis="y1",
            line=dict(color="#bdc3c7", width=3, dash="dash"),
        )
    )

    # Previous Year % Change
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=previous_year_change,
            name=f"{metric.label} Previous Year % Change",
            visible="legendonly",
            yaxis="y2",
            line=dict(color="#bdc3c7", width=1, dash="dot"),
        )
    )

    # Previous Period
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=previous_period,
            name=f"{metric.label} Previous Period",
            mode="lines",
            visible="legendonly",
            yaxis="y1",
            line=dict(color="#bdc3c7", width=3, dash="dash"),
        )
    )

    # Previous Period % Change
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=previous_period_change,
            name=f"{metric.label} Previous Period % Change",
            visible="legendonly",
            yaxis="y2",
            line=dict(color="#bdc3c7", width=1, dash="dot"),
        )
    )

    # Six Periods Ago
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=six_periods,
            name=f"{metric.label} Trailing Six Periods",
            mode="lines",
            visible="legendonly",
            yaxis="y1",
            line=dict(color="#bdc3c7", width=3, dash="dash"),
        )
    )

    # Six Periods % Change
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=six_periods_change,
            name=f"{metric.label} Trailing Six Periods % Change",
            visible="legendonly",
            yaxis="y2",
            line=dict(color="#bdc3c7", width=1, dash="dot"),
        )
    )

    # Three Period Moving Average
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=moving_average,
            name=f"{metric.label} Three Period Moving Average",
            mode="lines",
            visible="legendonly",
            yaxis="y1",
            line=dict(color="#bdc3c7", width=3, dash="dash"),
        )
    )

    # Three Period Moving Average % Change
    line_chart.add_trace(
        go.Scatter(
            x=time_period,
            y=moving_average_change,
            name=f"{metric.label} Three Period Moving Average % Change",
            visible="legendonly",
            yaxis="y2",
            line=dict(color="#bdc3c7", width=1, dash="dot"),
        )
    )

    # Formatting
    line_chart.update_layout(
        margin=dict(l=0, r=0, t=25, b=0),
        xaxis_title=time_grain.capitalize(),
        yaxis=dict(title=metric.label),
        yaxis2=dict(
            title="% Change",
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
        ),
        plot_bgcolor="white",
        hovermode="x unified",
    )

    line_chart.update_traces(textposition="top left")

    if legend is False:
        line_chart.update_layout(showlegend=False)
    if title is True:
        line_chart.update_layout(title=metric.label)
    if y2 is False:
        line_chart.update_layout(yaxis2=dict(visible=False))
    if grid is False:
        line_chart.update_layout(
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            yaxis2=dict(showgrid=False),
        )

    return line_chart


def create_slice_chart(chart_type, data_frame, metric, time_grain, dimension):
    if chart_type == "line":
        line_chart = px.line(
            data_frame,
            x="Period Started On",
            y=metric.label,
            color=dimension.label,
            title="Long-Form Input",
        )

        line_chart.update_layout(
            autotypenumbers="convert types",
            title=metric.label,
            xaxis_title=time_grain.capitalize(),
            yaxis_title=metric.label,
            plot_bgcolor="white",
            hovermode="x unified",
        )
    elif chart_type == "bar":
        line_chart = px.bar(
            data_frame,
            x="Period Started On",
            y=metric.label,
            color=dimension.label,
            title="Long-Form Input",
        )

        line_chart.update_layout(
            autotypenumbers="convert types",
            title=metric.label,
            xaxis_title=time_grain.capitalize(),
            yaxis_title=metric.label,
            plot_bgcolor="white",
            hovermode="x unified",
        )

    return line_chart
