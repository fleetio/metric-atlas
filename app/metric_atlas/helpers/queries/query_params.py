import streamlit as st
import metric_atlas.helpers.helpers as helpers


def set_query_params_from_state(session_state, filters):
    filter_values = [filter for filter in filters if len(filter["filter_values"]) > 0]

    empty_dict = {}

    # Set URL Params for Page
    url_params_dict = {
        "category": session_state.get("metric", {"is_empty": True}).category,
        "metric": session_state.get("metric", {"is_empty": True}).name,
        "time_grain": session_state.get("time_grain"),
        "time_period": session_state.get("time_period", empty_dict).get("name"),
    }

    if session_state.get("slice_by") is not None:
        url_params_dict["slice_by"] = session_state.get("slice_by").name

    for filter in filter_values:
        url_params_dict[filter["field"]] = filter["filter_values"]

    st.experimental_set_query_params(**url_params_dict)


def get_param_values(query_params):
    if query_params.get("category") is None or query_params.get("metric") is None:
        print("Category is not set, setting default values...")
        params = {}
    else:
        metric_categories = helpers.get_metric_categories()
        metric_category = query_params.get("category")[0]
        metric_definition = helpers.get_metric_definition(metric_category)

        # Category
        try:
            category = [x for x in metric_categories if x["name"] == metric_category][0]
        except Exception as error:
            category = None
            print(error)

        # Metric
        try:
            metric = [
                x for x in metric_definition if x.name == query_params.get("metric")[0]
            ][0]
        except Exception as error:
            category = None
            print(error)

        # Time Period
        try:
            standard_time_period_options = helpers.standard_periods(
                query_params.get("time_grain")[0]
            )
            time_period = [
                x
                for x in standard_time_period_options
                if x["name"] == query_params.get("time_period")[0]
            ][0]
        except Exception as error:
            time_period = None
            print(error)

        # Slice By
        try:
            slice_by = [
                x
                for x in metric.dimensions
                if x.name == query_params.get("slice_by")[0]
            ][0]
        except Exception as error:
            slice_by = None
            print(error)

        # Get and Set Filter Params
        standard_params = [
            "category",
            "metric",
            "time_grain",
            "time_period",
            "slice_by",
        ]
        filter_params = []
        for param in query_params:
            if param not in standard_params:
                filter_params.append({"name": param, "value": query_params.get(param)})

        params = {
            "category": category,
            "metric": metric,
            "time_grain": query_params.get("time_grain", ["month"])[0],
            "time_period": time_period,
            "slice_by": slice_by,
            "filters": filter_params,
        }

    return params
