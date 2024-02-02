WITH metric_source AS (
        
            SELECT
                {{date_field}} as metric_date
                , *
            FROM
                {{schema}}.{{table}}
            {% if filter_count > 0 %}
            WHERE
                {% for filter in filters %}
                    {{filter.field}} IN (
                            {%- for item in filter.filter_values -%}
                                '{{item}}'
                                {%- if not loop.last -%}
                                ,
                                {%- endif -%}
                            {%- endfor -%}
                    )
                {% if not loop.last %}
                AND
                {% endif %}
                {% endfor %}
            {% endif %}
        
        ), date_spine AS (
        
            SELECT
                *
            FROM
                core.calendar
            WHERE
                date_id BETWEEN (SELECT MIN({{date_field}}) FROM {{schema}}.{{table}}) AND '{{end_date}}'::DATE


        ), period_to_date AS (

            SELECT
            {% if time_grain ==  "day" -%}

                date_spine.date_id::text AS "Time Period"
                , date_spine.date_id AS "Period Started On"
                , date_spine.date_id AS "Period Ended On"

            {%- elif time_grain ==  "week" -%}

                date_spine.week_with_year::text AS "Time Period"
                , date_spine.week_started_on AS "Period Started On"
                , date_spine.week_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "month" -%}

                date_spine.month_with_year::text AS "Time Period"
                , date_spine.month_started_on AS "Period Started On"
                , date_spine.month_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "quarter" -%}
                
                date_spine.quarter_with_year::text AS "Time Period"
                , date_spine.quarter_started_on AS "Period Started On"
                , date_spine.quarter_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "year" -%}

                date_spine.day_year::text AS "Time Period"
                , date_spine.year_started_on AS "Period Started On"
                , date_spine.year_ended_on AS "Period Ended On"

            {% endif %}

                , CASE
                    WHEN "Period Started On" > CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE THEN 'Period Not Started'
                    WHEN CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE BETWEEN "Period Started On" AND "Period Ended On" THEN 'Mid Period' 
                    WHEN '{{end_date}}'::DATE BETWEEN "Period Started On" 
                    AND "Period Ended On" - INTERVAL 1 DAY THEN 'Mid Period'
                    --AND DATEADD('day', -1, "Period Ended On") THEN 'Mid Period' 
                    ELSE 'Completed Period' 
                END as "Period Type"
                , {{days_into_current_period}} AS days_into_period 

            -- Metrics
                , {{metrics[0].sql}} AS metric

        FROM
            date_spine
        LEFT JOIN
            metric_source ON metric_source.metric_date::DATE = date_spine.date_id
        WHERE
            {% if time_grain ==  "day" -%}

                date_spine.day_of_year <= {{days_into_current_period}}

            {%- elif time_grain ==  "week" -%}

                date_spine.day_of_week_number <= {{days_into_current_period}}

            {%- elif time_grain ==  "month" -%}

                date_spine.day_of_month <= {{days_into_current_period}}

            {%- elif time_grain ==  "quarter" -%}
                
                date_spine.day_of_quarter <= {{days_into_current_period}}

            {%- elif time_grain ==  "year" -%}

                date_spine.day_of_year <= {{days_into_current_period}}

            {% endif %}
        GROUP BY
            "Time Period"
            , "Period Started On"
            , "Period Ended On"
        ORDER BY
            1 DESC

        ), final_metrics AS (
        
        SELECT
            {% if time_grain ==  "day" -%}

                date_spine.date_id::text AS "Time Period"
                , date_spine.date_id AS "Period Started On"
                , date_spine.date_id AS "Period Ended On"

            {%- elif time_grain ==  "week" -%}

                date_spine.week_with_year::text AS "Time Period"
                , date_spine.week_started_on AS "Period Started On"
                , date_spine.week_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "month" -%}

                date_spine.month_with_year::text AS "Time Period"
                , date_spine.month_started_on AS "Period Started On"
                , date_spine.month_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "quarter" -%}
                
                date_spine.quarter_with_year::text AS "Time Period"
                , date_spine.quarter_started_on AS "Period Started On"
                , date_spine.quarter_ended_on AS "Period Ended On"

            {%- elif time_grain ==  "year" -%}

                date_spine.day_year::text AS "Time Period"
                , date_spine.year_started_on AS "Period Started On"
                , date_spine.year_ended_on AS "Period Ended On"

            {% endif %}

                , CASE
                    WHEN "Period Started On" > CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE THEN 'Period Not Started'
                    WHEN CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE BETWEEN "Period Started On" AND "Period Ended On" THEN 'Mid Period' 
                    WHEN '{{end_date}}'::DATE BETWEEN "Period Started On" 
                    AND "Period Ended On" - INTERVAL 1 DAY THEN 'Mid Period' 
                    --AND DATEADD('day', -1, "Period Ended On") THEN 'Mid Period' 
                    ELSE 'Completed Period' 
                END as "Period Type"

                -- Metrics
                , {{metrics[0].sql}} as metric


        FROM
            date_spine
        LEFT JOIN
            metric_source ON metric_source.metric_date::DATE = date_spine.date_id
        GROUP BY
            "Time Period"
            , "Period Started On"
            , "Period Ended On"
        ORDER BY
            1 DESC
        ), 

        final_metrics_agg AS (

                SELECT 
                *
                , LAG(metric, 1, 0 ) OVER (ORDER BY "Period Started On") AS previous_period
                , metric - previous_period AS previous_period_change
                , DIV0(previous_period_change, previous_period) AS previous_period_pct_change

                , LAG(metric, 6, 0 ) OVER (ORDER BY "Period Started On") AS trailing_six_periods
                , metric - trailing_six_periods AS trailing_six_periods_change
                , DIV0(trailing_six_periods_change, trailing_six_periods) AS trailing_six_periods_pct_change

                , LAG (metric, {{periods_per_year}}, 0 ) OVER (ORDER BY "Period Started On") AS previous_year
                , metric - previous_year AS previous_year_change
                , DIV0(previous_year_change, previous_year) AS previous_year_pct_change

                -- Three Period Moving Average
                , AVG(metric) OVER (ORDER BY "Period Started On" ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS three_period_moving_average
                , metric - three_period_moving_average AS three_period_moving_average_change
                , DIV0(three_period_moving_average_change, three_period_moving_average) AS three_period_moving_average_pct_change

                FROM

                final_metrics

        ),
        period_to_date_metrics_agg  AS (

                SELECT 
                *
                , LAG(metric, 1, 0 ) OVER (ORDER BY "Period Started On") AS previous_period
                , metric - previous_period AS previous_period_change
                , DIV0(previous_period_change, previous_period) AS previous_period_pct_change

                , LAG(metric, 6, 0 ) OVER (ORDER BY "Period Started On") AS trailing_six_periods
                , metric - trailing_six_periods AS trailing_six_periods_change
                , DIV0(trailing_six_periods_change, trailing_six_periods) AS trailing_six_periods_pct_change

                , LAG (metric, {{periods_per_year}}, 0 ) OVER (ORDER BY "Period Started On") AS previous_year
                , metric - previous_year AS previous_year_change
                , DIV0(previous_year_change, previous_year) AS previous_year_pct_change

                -- Three Period Moving Average
                , AVG(metric) OVER (ORDER BY "Period Started On" ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS three_period_moving_average
                , metric - three_period_moving_average AS three_period_moving_average_change
                , DIV0(three_period_moving_average_change, three_period_moving_average) AS three_period_moving_average_pct_change

                FROM

                period_to_date

        ),
        unioned_metrics AS (
        
        SELECT
            period_to_date."Time Period"
            , period_to_date."Period Started On"
            , period_to_date."Period Ended On"
            , period_to_date."Period Type"
            , period_to_date.days_into_period AS "Days Into Period"
            , period_to_date.metric AS "{{metrics[0].label}}"
            , period_to_date.previous_period AS "{{metrics[0].label}} Previous Period"
            , period_to_date.previous_period_change AS "{{metrics[0].label}} Previous Period Change"
            , period_to_date.previous_period_pct_change AS "{{metrics[0].label}} Previous Period % Change"
            , period_to_date.trailing_six_periods AS "{{metrics[0].label}} Trailing Six Periods"
            , period_to_date.trailing_six_periods_change AS "{{metrics[0].label}} Trailing Six Periods Change"
            , period_to_date.trailing_six_periods_pct_change AS "{{metrics[0].label}} Trailing Six Periods % Change"
            , period_to_date.previous_year AS "{{metrics[0].label}} Previous Year"
            , period_to_date.previous_year_change AS "{{metrics[0].label}} Previous Year Change"
            , period_to_date.previous_year_pct_change AS "{{metrics[0].label}} Previous Year % Change"
            , period_to_date.three_period_moving_average AS "{{metrics[0].label}} Three Period Moving Average"
            , period_to_date.three_period_moving_average_change AS "{{metrics[0].label}} Three Period Moving Average Change"
            , period_to_date.three_period_moving_average_pct_change AS "{{metrics[0].label}} Three Period Moving Average % Change"
        FROM
            period_to_date_metrics_agg AS period_to_date
        WHERE
            period_to_date."Period Type" = 'Mid Period' AND 
            period_to_date."Period Started On" BETWEEN DATE_TRUNC('{{time_grain}}','{{start_date}}'::DATE) AND  '{{end_date}}'

        UNION ALL

        SELECT
            final_metrics."Time Period"
            , final_metrics."Period Started On"
            , final_metrics."Period Ended On"
            , final_metrics."Period Type"
            , NULL AS "Days Into Period"
            , final_metrics.metric AS "{{metrics[0].label}}"
            , final_metrics.previous_period AS "{{metrics[0].label}} Previous Period"
            , final_metrics.previous_period_change AS "{{metrics[0].label}} Previous Period Change"
            , final_metrics.previous_period_pct_change AS "{{metrics[0].label}} Previous Period % Change"
            , final_metrics.trailing_six_periods AS "{{metrics[0].label}} Trailing Six Periods"
            , final_metrics.trailing_six_periods_change AS "{{metrics[0].label}} Trailing Six Periods Change"
            , final_metrics.trailing_six_periods_pct_change AS "{{metrics[0].label}} Trailing Six Periods % Change"
            , final_metrics.previous_year AS "{{metrics[0].label}} Previous Year"
            , final_metrics.previous_year_change AS "{{metrics[0].label}} Previous Year Change"
            , final_metrics.previous_year_pct_change AS "{{metrics[0].label}} Previous Year % Change"
            , final_metrics.three_period_moving_average AS "{{metrics[0].label}} Three Period Moving Average"
            , final_metrics.three_period_moving_average_change AS "{{metrics[0].label}} Three Period Moving Average Change"
            , final_metrics.three_period_moving_average_pct_change AS "{{metrics[0].label}} Three Period Moving Average % Change"
        FROM
            final_metrics_agg AS final_metrics
        WHERE
            final_metrics."Period Type" = 'Completed Period' AND 
            final_metrics."Period Started On" BETWEEN DATE_TRUNC('{{time_grain}}','{{start_date}}'::DATE) AND  '{{end_date}}'
            
        )

        SELECT
            *
        FROM
            unioned_metrics
        ORDER BY
            "Period Started On"
        DESC;