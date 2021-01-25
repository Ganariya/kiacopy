import math
from typing import List, Set, Tuple

from kiacopy.circuit import Circuit


class Solution(List[Circuit]):
    """1つの解.

    1つの解はK本の巡回路からなる
    リストを継承しており`s[i]`でi個目の巡回路Circuitを参照可能
    プロパティでavg, sdなどを返す
    プロパティでavg, sdなどを返す
    """

    def __init__(self, gamma: float, theta: float, inf: float, sd_base: float) -> None:
        super().__init__()
        self.gamma: float = gamma
        self.theta: float = theta
        self.inf: float = inf
        self.sd_base: float = sd_base

    def __repr__(self) -> str:
        text = f"K = {len(self)}, avg={self.avg}, sd={self.sd}, sum={self.sum}, cost={self.cost} \n"
        text += "  ".join([str(s.cost) for s in self])
        text += "\n"
        return text

    @property
    def cost(self) -> float:
        avg = self.avg
        sd = self.sd
        if sd < self.sd_base:
            sd = (sd ** self.theta)
        return avg + self.gamma * sd

    @property
    def sd(self) -> float:
        avg = self.avg
        sd: float = sum([(s.cost - avg) ** 2 for s in self]) / len(self)
        return math.sqrt(sd)

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
