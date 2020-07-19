from .ants.ant import Ant
from .ants.randomant import RandomAnt
from .ants.sensitiveant import SensitiveAnt


class Colony:
    def __init__(self, alpha=1, beta=3, random=0, sensitive=0, q_0=0.2, tau_0=0.01, rho=0.03):
        self.alpha = alpha
        self.beta = beta
        self.random = random
        self.sensitive = sensitive
        self.q_0 = q_0
        self.tau_0 = tau_0
        self.rho = rho

    def __repr__(self):
        return (f'{self.__class__.__name__}(alpha={self.alpha}, '
                f'beta={self.beta})')

    def get_ants(self, count):
        ants = []
        num_of_random = int(count * self.random)
        num_of_sensitive = int(count * self.sensitive)
        num_of_normal = count - num_of_random - num_of_sensitive
        for __ in range(num_of_random):
            ants.append(RandomAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_sensitive):
            ants.append(SensitiveAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_normal):
            ants.append(Ant(alpha=self.alpha, beta=self.beta))
        return ants
