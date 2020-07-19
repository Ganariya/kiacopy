# -*- coding: utf-8 -*-
import sys
import itertools
import bisect
import random
import copy

from ..utils import positive
from ..circuit import Circuit


class Ant:
    def __init__(self, alpha=1, beta=3, **kwargs):
        self.alpha = alpha
        self.beta = beta
        self.is_res = False
        self.inf = None
        self.theta = None
        self.circuit = None
        self.unvisited = None

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = positive(value)

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = positive(value)

    def __repr__(self):
        return f'Ant(alpha={self.alpha}, beta={self.beta})'

    def init_solution(self, graph, inf, is_res, theta, start=1):
        self.circuit = Circuit(graph, start, ant=self)
        self.init_unvisited_nodes(graph)
        self.inf = inf
        self.is_res = is_res
        self.theta = theta

    def init_unvisited_nodes(self, graph):
        self.unvisited = []
        for node in graph[self.circuit.current]:
            if node not in self.circuit:
                self.unvisited.append(node)

    def move(self, graph):
        node = self.choose_destination(graph)
        current = self.circuit.current
        self.circuit.add_node(node)
        self.unvisited.remove(node)
        self.erase(graph, current, node)

    def erase(self, graph, now, to):
        graph.edges[now, to]['pheromone'] = 0
        graph.edges[to, now]['pheromone'] = 0
        graph.edges[now, to]['weight'] = self.inf
        graph.edges[to, now]['weight'] = self.inf

    def choose_destination(self, graph):
        if len(self.unvisited) == 1:
            return self.unvisited[0]
        scores = self.get_scores(graph)
        return self.choose_node(scores)

    def get_scores(self, graph):
        scores = []
        for node in self.unvisited:
            edge = graph.edges[self.circuit.current, node]
            score = self.score_edge(edge)
            if self.is_res:
                score /= self.score_residual(graph, node)
            scores.append(score)
        return scores

    def choose_node(self, scores):
        choices = self.unvisited
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        index = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]

    def score_edge(self, edge):
        weight = edge.get('weight', 1)
        if weight == 0:
            return sys.float_info.max
        pre = 1 / weight
        post = edge['pheromone']
        return post ** self.alpha * pre ** self.beta

    def score_residual(self, graph, to):
        cands = set(copy.deepcopy(self.unvisited))
        cands.remove(to)
        bad = []
        for cand in cands:
            if graph.edges[to, cand]['weight'] >= self.inf - 1e5:
                bad.append(cand)
        for x in bad:
            cands.remove(x)
        return max(1, len(cands) ** self.theta)
