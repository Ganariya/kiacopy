from __future__ import annotations

import functools
import sys

from typing import TYPE_CHECKING
from typing import Optional, List, Set, Tuple

if TYPE_CHECKING:
    from networkx import Graph
    from kiacopy.ants import Ant


@functools.total_ordering
class Circuit:

    def __init__(self, graph: Graph, start: int, ant: Optional[Ant] = None):
        self.graph: Graph = graph
        self.start: int = start
        self.ant: Optional[Ant] = ant
        self.current: int = start
        self.cost: float = 0
        self.path: List[Tuple[int, int]] = []
        self.nodes: List[int] = [start]
        self.visited: Set[int] = set(self.nodes)

    def __iter__(self):
        return iter(self.path)

    def __eq__(self, other) -> bool:
        return self.cost == other.cost

    def __lt__(self, other) -> bool:
        return self.cost < other.cost

    def __contains__(self, item) -> bool:
        return item in self.visited or item == self.current

    def __repr__(self) -> str:
        easy_id = self.get_easy_id(sep=',', monospace=False)
        return '{}\t{}'.format(self.cost, easy_id)

    def __hash__(self) -> int:
        return hash(self.get_id())

    def get_easy_id(self, sep=' ', monospace=True) -> str:
        nodes: List[str] = [str(n) for n in self.get_id()]
        if monospace:
            size: int = max([len(n) for n in nodes])
            nodes: List[str] = [n.rjust(size) for n in nodes]
        return sep.join(nodes)

    def get_id(self) -> Tuple[int, ...]:
        first: int = min(self.nodes)
        index: int = self.nodes.index(first)
        return tuple(self.nodes[index:] + self.nodes[:index])

    def add_node(self, node: int) -> None:
        """Record a node as visited.

        :param node: the node visited
        """
        self.nodes.append(node)
        self.visited.add(node)
        self._add_node(node)

    def close(self) -> None:
        """Close the tour so that the first and last nodes are the same."""
        self._add_node(self.start)

    def reconstruct(self) -> None:
        n: int = len(self.nodes)
        self.path: List[Tuple[int, int]] = []
        for i in range(n):
            self.path.append((self.nodes[i], self.nodes[(i + 1) % n]))

    def _add_node(self, node: int) -> None:
        edge = self.current, node
        data = self.graph.edges[edge]
        self.path.append(edge)
        self.cost += data['weight']
        self.current = node

    def trace(self, q: float, rho: float = 0) -> None:
        amount = q / self.cost
        for edge in self.path:
            self.graph.edges[edge]['pheromone'] += amount
            self.graph.edges[edge]['pheromone'] *= 1 - rho
            if not self.graph.edges[edge]['pheromone']:
                self.graph.edges[edge]['pheromone'] = sys.float_info.min
