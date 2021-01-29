import math
from typing import List, Set, Tuple, Literal
from kiacopy.circuit import Circuit

COST_KIND = Literal["weighted", "avg", "sd", "sum", "variance"]


class Solution(List[Circuit]):
    """1つの解.

    1つの解はK本の巡回路からなる
    リストを継承しており`s[i]`でi個目の巡回路Circuitを参照可能
    プロパティでavg, sdなどを返す
    プロパティでavg, sdなどを返す
    """

    def __init__(self, gamma: float, theta: float, inf: float, cost_kind: COST_KIND) -> None:
        super().__init__()
        self.gamma: float = gamma
        self.theta: float = theta
        self.inf: float = inf
        self.cost_kind: COST_KIND = cost_kind

    def __repr__(self) -> str:
        text = f"K={len(self)}, avg={self.avg}, sd={self.sd}, variance={self.variance}, sum={self.sum}, cost_kind={self.cost_kind}, cost={self.cost} \n"
        text += "  ".join([str(s.cost) for s in self])
        text += "\n"
        return text

    @property
    def cost(self) -> float:
        return getattr(self, self.cost_kind)

    @property
    def weighted(self) -> float:
        avg = self.avg
        sd = self.sd ** self.theta
        return avg + self.gamma * sd

    @property
    def sd(self) -> float:
        return math.sqrt(self.variance)

    @property
    def variance(self) -> float:
        avg = self.avg
        variance: float = sum([(s.cost - avg) ** 2 for s in self]) / len(self)
        return variance

    @property
    def sum(self) -> float:
        return sum([s.cost for s in self])

    @property
    def avg(self) -> float:
        return self.sum / len(self)

    @property
    def duplicate(self) -> int:
        edge_set: Set[Tuple[int, int]] = set()
        dup: int = 0
        for circuit in self:
            for e in circuit:
                x, y = min(e), max(e)
                a = (x, y)
                if a in edge_set:
                    dup += 1
                else:
                    edge_set.add(a)
        return dup
