import itertools
import bisect
import random
import numpy as np
from typing import List

from kiacopy.ants.ant import Ant


class SensitiveAnt(Ant):

    def __init__(self, alpha: float = 1, beta: float = 3, q_0: float = 0.2):
        super().__init__(alpha, beta)
        self.q_0: float = q_0

    def choose_node(self, scores: List[float]) -> int:
        choices: List[int] = self.unvisited
        total: float = sum(scores)
        cumdist: List[float] = list(itertools.accumulate(scores)) + [total]
        q = random.random()
        if q < self.q_0:
            index: int = np.argmax(scores)
        else:
            index: int = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]
