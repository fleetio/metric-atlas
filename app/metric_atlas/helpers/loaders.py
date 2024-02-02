from typing import List
import yaml
from metric_atlas.helpers.models.Metric import Metric
from metric_atlas.helpers.models.MetricDimension import MetricDimension
from metric_atlas.helpers.models.Person import Person


def load_metric_from_yaml(yaml_file_path: str) -> List[Metric]:
    with open(yaml_file_path, "r") as f:
        metric_dicts = yaml.safe_load(f)

    metrics = []
    for metric_dict in metric_dicts.get("metrics"):
        dimensions = [
            MetricDimension(**dim) for dim in metric_dict.get("dimensions", [])
        ]
        business_owner = Person(
            **metric_dict.get("business_owner", {"name": "", "email": ""})
        )
        data_team_owner = Person(
            **metric_dict.get("data_team_owner", {"name": "", "email": ""})
        )
        metric = Metric(
            name=metric_dict.get("name", ""),
            type=metric_dict.get("type", ""),
            category=metric_dict.get("category", ""),
            schema=metric_dict.get("schema", ""),
            model=metric_dict.get("model", ""),
            description=metric_dict.get("description", ""),
            sql=metric_dict.get("sql", ""),
            timestamp=metric_dict.get("timestamp", ""),
            business_owner=business_owner,
            data_team_owner=data_team_owner,
            filters=metric_dict.get("filters", []),
            is_pre_aggregated=metric_dict.get("is_pre_aggregated"),
            time_grains=metric_dict.get("time_grains", []),
            dimensions=dimensions,
            label=metric_dict.get("label", None),
            external_package_metric=metric_dict.get("external_package_metric", False),
            is_cumulative_metric=metric_dict.get("is_cumulative", False),
            is_inverted=metric_dict.get("is_inverted", False),
        )
        metrics.append(metric)

    return metrics
