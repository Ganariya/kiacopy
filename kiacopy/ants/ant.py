# -*- coding: utf-8 -*-
import sys
import itertools
import bisect
import random
import copy
from typing import List, Tuple, Set, Dict, Optional

from networkx import Graph
from networkx.classes.reportviews import EdgeView
from kiacopy.utils import positive
from kiacopy.circuit import Circuit


class Ant:
    def __init__(self, alpha: float = 1, beta: float = 3, **kwargs):
        self.alpha: float = alpha
        self.beta: float = beta
        self.is_res: bool = False
        self.inf: Optional[float] = None
        self.theta: Optional[float] = None
        self.circuit: Optional[Circuit] = None
        self.unvisited: Optional[List[int]] = None

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        self._alpha = positive(value)

    @property
    def beta(self) -> float:
        return self._beta

    @beta.setter
    def beta(self, value: float):
        self._beta = positive(value)

    def __repr__(self) -> str:
        return f'Ant(alpha={self.alpha}, beta={self.beta})'

    def init_solution(self, graph: Graph, inf: float, is_res: bool, theta: float, start: int = 1) -> None:
        self.circuit: Circuit = Circuit(graph, start, ant=self)
        self.init_unvisited_nodes(graph)
        self.inf = inf
        self.is_res = is_res
        self.theta = theta

    def init_unvisited_nodes(self, graph: Graph) -> None:
        self.unvisited: List[int] = []
        for node in graph[self.circuit.current]:
            if node not in self.circuit:
                self.unvisited.append(node)

    def move(self, graph: Graph) -> None:
        node: int = self.choose_destination(graph)
        current: int = self.circuit.current
        self.circuit.add_node(node)
        self.unvisited.remove(node)
        self.erase(graph, current, node)

    def erase(self, graph: Graph, now: int, to: int) -> None:
        graph.edges[now, to]['pheromone'] = 0
        graph.edges[to, now]['pheromone'] = 0
        graph.edges[now, to]['weight'] = self.inf
        graph.edges[to, now]['weight'] = self.inf

    def choose_destination(self, graph: Graph) -> int:
        if len(self.unvisited) == 1:
            return self.unvisited[0]
        scores: List[float] = self.get_scores(graph)
        return self.choose_node(scores)

    def get_scores(self, graph: Graph) -> List[float]:
        scores: List[float] = []
        for node in self.unvisited:
            edge: EdgeView = graph.edges[self.circuit.current, node]
            score: float = self.score_edge(edge)
            if self.is_res:
                score /= self.score_residual(graph, node)
            scores.append(score)
        return scores

    def choose_node(self, scores: List[float]) -> int:
        choices: List[int] = self.unvisited
        total: float = sum(scores)
        cumdist: List[float] = list(itertools.accumulate(scores)) + [total]
        index: int = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]

    def score_edge(self, edge: EdgeView) -> float:
        weight = edge.get('weight', 1)
        if weight == 0:
            return sys.float_info.max
        pre = 1 / weight
        post = edge['pheromone']
        return post ** self.alpha * pre ** self.beta

    def score_residual(self, graph: Graph, to: int) -> float:
        cands: Set[int] = set(copy.deepcopy(self.unvisited))
        cands.remove(to)
        bad: List[int] = []
        for cand in cands:
            if graph.edges[to, cand]['weight'] >= self.inf - 1e5:
                bad.append(cand)
        for x in bad:
            cands.remove(x)
        return max(1.0, len(cands) ** self.theta)
