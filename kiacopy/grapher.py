import sys
from typing import Final, Tuple, List

from networkx import Graph
from logging import getLogger

logger = getLogger(__name__)


class Grapher:

    def __init__(self, graph: Graph):
        self.graph: Final[Graph] = graph
        self.N: Final[int] = graph.number_of_nodes()
        self.dp: List[List[int]] = [[0] * (self.N + 1) for _ in range(self.N + 1)]

    def __str__(self) -> str:
        ret = ""
        for i in range(self.N + 1):
            for j in range(self.N + 1):
                if self.dp[i][j] > 1:
                    ret += f'{i}-{j}({self.dp[i][j]}), '
        return ret

    def use(self, t: Tuple[int, int], is_log=False) -> None:
        x, y = Grapher.minmax(t)
        if is_log:
            logger.info(f'[use-PREV] {x}-{y}({self.dp[x][y]})')
        self.dp[x][y] += 1
        if is_log:
            logger.info(f'[use-AFTER] {x}-{y}({self.dp[x][y]})')

    def unuse(self, t: Tuple[int, int], is_log=False) -> None:
        x, y = Grapher.minmax(t)
        if is_log:
            logger.info(f'[unuse-PREV] {x}-{y}({self.dp[x][y]})')
        self.dp[x][y] -= 1
        if is_log:
            logger.info(f'[unuse-AFTER] {x}-{y}({self.dp[x][y]})')

    def is_used(self, t: Tuple[int, int]) -> bool:
        x, y = Grapher.minmax(t)
        return self.dp[x][y] > 0

    def phe(self, t: Tuple[int, int]) -> float:
        x, y = Grapher.minmax(t)
        if self.is_used(t):
            return 0
        else:
            return self.graph.edges[x, y]['pheromone']

    def wei(self, t: Tuple[int, int]) -> float:
        x, y = Grapher.minmax(t)
        if self.is_used(t):
            return sys.float_info.max
        return self.graph.edges[x, y]['weight']

    def nwei(self, t: Tuple[int, int]) -> float:
        x, y = Grapher.minmax(t)
        return self.graph.edges[x, y].get('weight', 1)

    @staticmethod
    def minmax(t: Tuple[int, int]) -> Tuple[int, int]:
        x, y = min(t), max(t)
        return x, y
