
WITH options AS (
{% for field in filters %}
    SELECT DISTINCT
        '{{field.name}}' AS dimension
        , COALESCE({{field.name}},'n/a') AS select_option
    FROM
        {{schema}}.{{table}}
{% if not loop.last %}
   UNION ALL
{% endif %}

{% endfor %}
)

SELECT
    *
FROM
    options
ORDER BY dimension ASC, select_option ASC
