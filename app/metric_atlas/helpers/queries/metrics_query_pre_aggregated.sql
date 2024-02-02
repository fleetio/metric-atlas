WITH metric_source AS (
        
            SELECT
                period_id AS "Time Period"
                , period_started_on AS "Period Started On"
                , period_ended_on AS "Period Ended On"
                , CASE
                    WHEN "Period Started On" > CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE THEN 'Period Not Started'
                    WHEN CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE BETWEEN "Period Started On" AND "Period Ended On" THEN 'Mid Period' 
                    WHEN '{{end_date}}'::DATE BETWEEN "Period Started On" AND DATEADD('day', -1, "Period Ended On") THEN 'Mid Period' 
                    ELSE 'Completed Period' 
                END as "Period Type"
                , {{metrics[0].sql}} as metric
                , LAG(metric, 1, 0 ) OVER (ORDER BY "Period Started On") AS previous_period
                , metric - previous_period AS previous_period_change
                , DIV0(previous_period_change, previous_period) AS previous_period_pct_change

                , LAG(metric, 6, 0 ) OVER (ORDER BY "Period Started On") AS trailing_six_periods
                , metric - trailing_six_periods AS trailing_six_periods_change
                , DIV0(trailing_six_periods_change, trailing_six_periods) AS trailing_six_periods_pct_change

                , LAG(metric, {{periods_per_year}}, 0 ) OVER (ORDER BY "Period Started On") AS previous_year
                , metric - previous_year AS previous_year_change
                , DIV0(previous_year_change, previous_year) AS previous_year_pct_change

                -- Three Period Moving Average
                , AVG(metric) OVER (ORDER BY "Period Started On" ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS three_period_moving_average
                , metric - three_period_moving_average AS three_period_moving_average_change
                , DIV0(three_period_moving_average_change, three_period_moving_average) AS three_period_moving_average_pct_change
            FROM
                {{schema}}.{{table}}
            WHERE
                period_type = '{{time_grain}}'

        ),
        final_metrics  AS (

            SELECT
                metric_source."Time Period"
                , metric_source."Period Started On"
                , metric_source."Period Ended On"
                , metric_source."Period Type"
                , NULL AS "Days Into Period"
                , metric_source.metric AS "{{metrics[0].label}}"
                , metric_source.previous_period AS "{{metrics[0].label}} Previous Period"
                , metric_source.previous_period_change AS "{{metrics[0].label}} Previous Period Change"
                , metric_source.previous_period_pct_change AS "{{metrics[0].label}} Previous Period % Change"
                , metric_source.trailing_six_periods AS "{{metrics[0].label}} Trailing Six Periods"
                , metric_source.trailing_six_periods_change AS "{{metrics[0].label}} Trailing Six Periods Change"
                , metric_source.trailing_six_periods_pct_change AS "{{metrics[0].label}} Trailing Six Periods % Change"
                , metric_source.previous_year AS "{{metrics[0].label}} Previous Year"
                , metric_source.previous_year_change AS "{{metrics[0].label}} Previous Year Change"
                , metric_source.previous_year_pct_change AS "{{metrics[0].label}} Previous Year % Change"
                , metric_source.three_period_moving_average AS "{{metrics[0].label}} Three Period Moving Average"
                , metric_source.three_period_moving_average_change AS "{{metrics[0].label}} Three Period Moving Average Change"
                , metric_source.three_period_moving_average_pct_change AS "{{metrics[0].label}} Three Period Moving Average % Change"
            FROM
                metric_source
            WHERE
                metric_source."Period Started On" BETWEEN DATE_TRUNC('{{time_grain}}','{{start_date}}'::DATE) AND '{{end_date}}' 
        )

        SELECT
            *
        FROM
            final_metrics
        ORDER BY
            "Period Started On"
        DESC;