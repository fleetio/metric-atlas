def create_standard_metrics(data_frame, metric):
    """
    Creates standard metrics from dataframe and metric definition
    param: data_frame - The data frame returned from the metrics query.
    param: metric - The definition of the metric.
    returns: Dicitionary of metrics.
    """

    # Rows that are Mid Period
    mid_period = data_frame[data_frame["Period Type"] == "Mid Period"]

    # Rows that are Completed
    completed_periods = data_frame[data_frame["Period Type"] == "Completed Period"]

    raw_metrics = {}

    if mid_period.shape[0] > 0:
        raw_metrics["current_ptd"] = mid_period[metric.label].iloc[0]
        raw_metrics["previous_period_ptd"] = mid_period[
            f"{metric.label} Previous Period"
        ].iloc[0]
        raw_metrics["trailing_six_periods_ptd"] = mid_period[
            f"{metric.label} Trailing Six Periods"
        ].iloc[0]
        raw_metrics["last_year_ptd"] = mid_period[f"{metric.label} Previous Year"].iloc[
            0
        ]
        raw_metrics["moving_average_ptd"] = mid_period[
            f"{metric.label} Three Period Moving Average"
        ].iloc[0]
        raw_metrics["period_over_period_change_ptd"] = mid_period[
            f"{metric.label} Previous Period Change"
        ].iloc[0]
        raw_metrics["year_over_year_change_ptd"] = mid_period[
            f"{metric.label} Previous Year Change"
        ].iloc[0]
        raw_metrics["trailing_six_periods_change_ptd"] = mid_period[
            f"{metric.label} Trailing Six Periods Change"
        ].iloc[0]
        raw_metrics["moving_average_change_ptd"] = mid_period[
            f"{metric.label} Three Period Moving Average Change"
        ].iloc[0]

        # Percent Change Metrics
        period_over_period_pct_change_ptd = mid_period[
            f"{metric.label} Previous Period % Change"
        ].iloc[0]
        year_over_year_pct_change_ptd = mid_period[
            f"{metric.label} Previous Year % Change"
        ].iloc[0]
        trailing_six_periods_pct_change_ptd = mid_period[
            f"{metric.label} Trailing Six Periods % Change"
        ].iloc[0]
        moving_average_pct_change_ptd = mid_period[
            f"{metric.label} Three Period Moving Average % Change"
        ].iloc[0]

    if completed_periods.shape[0] > 0:
        # Metric Values and Amount of Change
        raw_metrics["current_period"] = completed_periods[metric.label].iloc[0]
        raw_metrics["previous_period"] = completed_periods[
            f"{metric.label} Previous Period"
        ].iloc[0]
        raw_metrics["trailing_six_periods"] = completed_periods[
            f"{metric.label} Trailing Six Periods"
        ].iloc[0]
        raw_metrics["last_year"] = completed_periods[
            f"{metric.label} Previous Year"
        ].iloc[0]
        raw_metrics["moving_average"] = completed_periods[
            f"{metric.label} Three Period Moving Average"
        ].iloc[0]
        raw_metrics["period_over_period_change"] = completed_periods[
            f"{metric.label} Previous Period Change"
        ].iloc[0]
        raw_metrics["year_over_year_change"] = completed_periods[
            f"{metric.label} Previous Year Change"
        ].iloc[0]
        raw_metrics["trailing_six_periods_change"] = completed_periods[
            f"{metric.label} Trailing Six Periods Change"
        ].iloc[0]
        raw_metrics["moving_average_change"] = completed_periods[
            f"{metric.label} Three Period Moving Average Change"
        ].iloc[0]

        # Percent Change Metrics
        period_over_period_pct_change = completed_periods[
            f"{metric.label} Previous Period % Change"
        ].iloc[0]
        year_over_year_pct_change = completed_periods[
            f"{metric.label} Previous Year % Change"
        ].iloc[0]
        trailing_six_periods_pct_change = completed_periods[
            f"{metric.label} Trailing Six Periods % Change"
        ].iloc[0]
        moving_average_pct_change = completed_periods[
            f"{metric.label} Three Period Moving Average % Change"
        ].iloc[0]

    # Format Metrics
    formatted_metrics = {}

    for item in raw_metrics:
        float_metric = float(raw_metrics[item])
        # formatted_metrics[item] = helpers.format_number(float_metric, metric.type)
        formatted_metrics[item] = float_metric

    metrics = {
        # Metric Values and Amount of Change
        "current_ptd": formatted_metrics.get("current_ptd"),
        "previous_period_ptd": formatted_metrics.get("previous_period_ptd"),
        "trailing_six_periods_ptd": formatted_metrics.get("trailing_six_periods_ptd"),
        "last_year_ptd": formatted_metrics.get("last_year_ptd"),
        "period_over_period_change_ptd": formatted_metrics.get(
            "period_over_period_change_ptd"
        ),
        "trailing_six_periods_change_ptd": formatted_metrics.get(
            "trailing_six_periods_change_ptd"
        ),
        "year_over_year_change_ptd": formatted_metrics.get("year_over_year_change_ptd"),
        "moving_average_ptd": formatted_metrics.get("moving_average_ptd"),
        "moving_average_change_ptd": formatted_metrics.get("moving_average_change_ptd"),
        # Metric Values and Amount of Change
        "current_period": formatted_metrics.get("current_period"),
        "previous_period": formatted_metrics.get("previous_period"),
        "trailing_six_periods": formatted_metrics.get("trailing_six_periods"),
        "last_year": formatted_metrics.get("last_year"),
        "period_over_period_change": formatted_metrics.get("period_over_period_change"),
        "trailing_six_periods_change": formatted_metrics.get(
            "trailing_six_periods_change"
        ),
        "year_over_year_change": formatted_metrics.get("year_over_year_change"),
        "moving_average": formatted_metrics.get("moving_average"),
        "moving_average_change": formatted_metrics.get("moving_average_change"),
    }
    if completed_periods.shape[0] > 0:
        # Percent Change Metrics
        metrics["period_over_period_percent_change"] = period_over_period_pct_change
        metrics["trailing_six_periods_percent_change"] = trailing_six_periods_pct_change
        metrics["year_over_year_percent_change"] = year_over_year_pct_change
        metrics["moving_average_percent_change"] = moving_average_pct_change

    if mid_period.shape[0] > 0:
        # Percent Change Metrics
        metrics[
            "period_over_period_percent_change_ptd"
        ] = period_over_period_pct_change_ptd
        metrics[
            "trailing_six_periods_percent_change_ptd"
        ] = trailing_six_periods_pct_change_ptd
        metrics["year_over_year_percent_change_ptd"] = year_over_year_pct_change_ptd
        metrics["moving_average_percent_change_ptd"] = moving_average_pct_change_ptd

    return metrics
