from typing import List
from dataclasses import dataclass
from metric_atlas.helpers.models.MetricDimension import MetricDimension
from metric_atlas.helpers.models.Person import Person


@dataclass
class Metric:
    name: str
    type: str
    category: str
    schema: str
    model: str
    description: str
    sql: str
    timestamp: str
    business_owner: Person
    data_team_owner: Person
    filters: List[str]
    is_pre_aggregated: bool = None
    time_grains: List[str] = None
    dimensions: List[MetricDimension] = None
    label: str = None
    is_inverted: bool = False
    is_cumulative_metric: bool = False
    external_package_metric: bool = False

    def __post_init__(self):
        if self.label is None:
            self.label = self.name
