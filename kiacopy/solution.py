import math


class Solution(list):

    def __init__(self, gamma, theta, inf, sd_base):
        super().__init__()
        self.gamma = gamma
        self.theta = theta
        self.inf = inf
        self.sd_base = sd_base

    def __repr__(self):
        text = f"K = {len(self)}, avg={self.avg}, sd={self.sd}, sum={self.sum}, cost={self.cost} \n"
        text += "  ".join([str(s.cost) for s in self])
        text += "\n"
        return text

    @property
    def cost(self):
        avg = self.avg
        sd = self.sd
        if sd < self.sd_base:
            sd = (sd ** self.theta)
        return avg + self.gamma * sd

    @property
    def sd(self):
        avg = self.avg
        sd = sum([(s.cost - avg) ** 2 for s in self]) / len(self)
        return math.sqrt(sd)

    @property
    def sum(self):
        return sum([s.cost for s in self])

    @property
    def avg(self):
        return self.sum / len(self)
