from dataclasses import dataclass


@dataclass
class MetricDimension:
    name: str
    label: str = None

    def __post_init__(self):
        if self.label is None:
            self.label = self.name
