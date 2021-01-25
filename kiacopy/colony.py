from typing import List
from kiacopy.ants.ant import Ant
from kiacopy.ants.randomant import RandomAnt
from kiacopy.ants.sensitiveant import SensitiveAnt


class Colony:
    """コロニークラス.

    アリが利用する定数を保持する.
    アリの群体を生成する。
    """
    def __init__(self, alpha: float = 1, beta: float = 3, random: float = 0, sensitive: float = 0, q_0: float = 0.2, tau_0: float = 0.01, rho: float = 0.03) -> None:
        self.alpha: float = alpha
        self.beta: float = beta
        self.random: float = random
        self.sensitive: float = sensitive
        self.q_0: float = q_0
        self.tau_0: float = tau_0
        self.rho: float = rho

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(alpha={self.alpha}, '
                f'beta={self.beta})')

    def get_ants(self, count: int) -> List[Ant]:
        """アリの群体を生成する.

        Parameters
        ----------
        count:int
            生成するアリの個体数

        Returns
        -------
        list of int
            生成されたアリの群れのリスト

        Notes
        -----
        random, sensitiveなどの値を生成することで、他の挙動を行うアリを生成する
        残りが通常のアリになる
        """
        ants: List[Ant] = []
        num_of_random: int = int(count * self.random)
        num_of_sensitive: int = int(count * self.sensitive)
        num_of_normal: int = count - num_of_random - num_of_sensitive
        for __ in range(num_of_random):
            ants.append(RandomAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_sensitive):
            ants.append(SensitiveAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_normal):
            ants.append(Ant(alpha=self.alpha, beta=self.beta))
        return ants
