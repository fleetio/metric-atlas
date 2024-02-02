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
                date_id BETWEEN (SELECT MIN({{date_field}}) FROM {{schema}}.{{table}}) AND CONVERT_TIMEZONE('America/Chicago', CURRENT_TIMESTAMP)::DATE

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

            {% for dimension in dimensions %}
                , {{dimension.name}} AS "{{dimension.label}}"
            {% endfor %}

            -- Metrics
            {% for metric in metrics %}
                , {{metric.sql}} as "{{metric.label}}"

            {% endfor %}
        
        FROM
            date_spine
        LEFT JOIN
            metric_source ON metric_source.metric_date::DATE = date_spine.date_id
        GROUP BY
            "Time Period"
            , "Period Started On"
            , "Period Ended On"
            {% for dimension in dimensions %}
                , "{{dimension.label}}"
            {% endfor %}
        ORDER BY
            1 DESC
        )

        SELECT
            *
        FROM
            final_metrics
        WHERE
            "Period Started On" BETWEEN '{{start_date}}' AND '{{end_date}}'
