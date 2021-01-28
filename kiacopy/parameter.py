from __future__ import annotations
from typing import Union

import yaml

Accepted = Union[str, float, int, bool, None]


class Parameter:

    def __init__(self, yaml_path: str):
        self.yaml_path: str = yaml_path
        with open(yaml_path, 'r') as f:
            self.yaml: dict[str, Accepted] = yaml.load(f)

    def __getitem__(self, key: str) -> Accepted:
        return self.yaml[key]
