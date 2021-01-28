import time

from typing import Optional, List

from networkx import Graph
from tsplib95.models import Problem
from kiacopy.ants import Ant
from kiacopy.colony import Colony
from kiacopy.solution import Solution


class State:
    """状態を保存する."""

    def __init__(self, graph: Graph, ants: List[Ant], limit: int, gen_size: Optional[int], colony: Colony, rho: float, q: float,
                 top: Optional[int], problem: Optional[Problem], gamma: float, theta: float, inf: float, R: int, is_update: bool, is_res: bool, is_best_opt: bool, is_multiple: bool) -> None:
        self.graph: Graph = graph
        self.ants: List[Ant] = ants
        self.limit: int = limit
        self.gen_size: Optional[int] = gen_size
        self.colony: Colony = colony
        self.rho: float = rho
        self.q: float = q
        self.top: Optional[int] = top
        self.problem: Optional[Problem] = problem
        self.gamma: float = gamma
        self.theta: float = theta
        self.inf: float = inf
        self.R: int = R
        self.is_update: bool = is_update
        self.is_res: bool = is_res
        self.is_best_opt: bool = is_best_opt
        self.is_multiple: bool = is_multiple
        self.fail_indices: List[int] = []
        self.fail_cnt: int = 0
        self.improve_indices: List[int] = []
        self.improve_cnt: int = 0
        self.success_indices: List[int] = []
        self.success_cnt: int = 0
        self.duplicate_indicates: List[int] = []
        self.start_time: float = time.perf_counter()
        self.is_new_record = False
        self.end_time: Optional[float] = None
        self.elapsed: Optional[float] = None
        self.solution: Optional[Solution] = None
        self.best_solution: Optional[Solution] = None
        self.solution_history: List[Solution] = []
        self.circuits = None
        self.record = None
        self.previous_record = None
        self._best = None

    @property
    def best(self):
        return self._best

    @best.setter
    def best(self, best):
        self.is_new_record = self.record is None or best < self.record
        if self.is_new_record:
            self.previous_record = self.record
            self.record = best
        self._best = best
