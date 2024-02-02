from dataclasses import dataclass, field


@dataclass
class MetricFilter:
    field: str
    label: str = None
    filter_values: list = field(default_factory=lambda: [])
