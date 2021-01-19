import math


class Solution(list):

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
