from __future__ import annotations

import functools
import sys

from typing import TYPE_CHECKING
from typing import Optional, List, Set, Tuple

if TYPE_CHECKING:
    from networkx import Graph
    from kiacopy.ants import Ant
    from kiacopy.grapher import Grapher


@functools.total_ordering
class Circuit:

    def __init__(self, graph: Graph, start: int, grapher: Grapher, ant: Optional[Ant] = None):
        """init.

        Notes
        -----
        アリ1体1体が閉路を持つ
        init時にノードと集合にstart頂点を追加する
        """
        self.graph: Graph = graph
        self.start: int = start
        self.ant: Optional[Ant] = ant
        self.current: int = start
        self.cost: float = 0
        self.path: List[Tuple[int, int]] = []
        self.nodes: List[int] = [start]
        self.grapher: Grapher = grapher
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
        """1から始まるたどったパスノード列を一つの文字列にして返す

        Parameters
        ----------
        sep:str
        monospace:bool

        Returns
        -------
        str
        """
        nodes: List[str] = [str(n) for n in self.get_id()]
        if monospace:
            size: int = max([len(n) for n in nodes])
            nodes: List[str] = [n.rjust(size) for n in nodes]
        return sep.join(nodes)

    def get_id(self) -> Tuple[int, ...]:
        """ある閉路の最も小さいノードIDから始まる巡回路列にする.

        Returns
        -------
        tuple of int
            最も小さい番号ノードから始まった巡回路列

        Examples
        --------
        (4, 1, 3, 2) -> (1, 3, 2, 4)
        """
        first: int = min(self.nodes)
        index: int = self.nodes.index(first)
        return tuple(self.nodes[index:] + self.nodes[:index])

    def add_node(self, node: int) -> None:
        """訪問したノードを記録する

        ノード配列と集合にノードを追加するのみ

        Notes
        -----
        実際にパスやコストなどを計算するのは`_add_node`

        Parameters
        ----------
        node: int
            訪問したノード
        """
        self.nodes.append(node)
        self.visited.add(node)
        self._add_node(node)

    def close(self) -> None:
        """パスを閉じるらしい. """
        self._add_node(self.start)

    def reconstruct(self) -> None:
        """ノード列からパス列を構築する."""
        n: int = len(self.nodes)
        self.path: List[Tuple[int, int]] = []
        for i in range(n):
            self.path.append((self.nodes[i], self.nodes[(i + 1) % n]))

    def _add_node(self, to_node: int) -> None:
        """新しい通過ノードによるパスを実際に追加する.

        Parameters
        ----------
        to_node: int

        Returns
        -------
        None
        """
        t = self.current, to_node
        self.path.append(t)
        self.cost += self.grapher.nwei(t)
        self.current = to_node

    def trace(self, q: float, rho: float = 0) -> None:
        amount = q / self.cost
        for edge in self.path:
            self.graph.edges[edge]['pheromone'] += amount
            self.graph.edges[edge]['pheromone'] *= 1 - rho
            if not self.graph.edges[edge]['pheromone']:
                self.graph.edges[edge]['pheromone'] = sys.float_info.min
