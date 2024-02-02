from dataclasses import dataclass


@dataclass
class Label:
    name: str
    label: str

    def __post_init__(self):
        if self.label is None:
            self.label = self.name
