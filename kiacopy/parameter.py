from __future__ import annotations
from typing import Union, Optional

import yaml
from pydantic import BaseModel

from kiacopy.solution import COST_KIND

Accepted = Union[str, float, int, bool, COST_KIND, None]


class Parameter(BaseModel):
    # ACO
    rho: float = 0.03
    q: float = 1.0
    gamma: float = 1.0
    theta: float = 2.0
    inf: float = 1e50
    R: int = 0
    limit: int
    gen_size: int
    top: Optional[int] = None
    cost_kind: COST_KIND

    # Colony
    alpha: float = 1
    beta: float = 3
    random: float = 0
    sensitive: float = 0
    q_0: float = 0.2
    tau_0: float = 0.01

    # is
    is_best_opt: bool
    is_res: bool
    is_update: bool
    is_multiple: bool

    @staticmethod
    def create(yaml_path: str) -> Parameter:
        with open(yaml_path, 'r') as f:
            data = yaml.load(f)
            return Parameter(**data)

# class Parameter:
#
#     def __init__(self, yaml_path: str):
#         self.yaml_path: str = yaml_path
#         with open(yaml_path, 'r') as f:
#             self.yaml: dict[str, Accepted] = yaml.load(f)
#
#     def __getitem__(self, key: str) -> Accepted:
#         return self.yaml[key]
