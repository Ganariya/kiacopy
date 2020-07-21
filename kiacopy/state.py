class State:

    def __init__(self, graph, ants, limit, gen_size, colony, rho, q, top, problem, gamma, theta, inf, sd_base):
        self.graph = graph
        self.ants = ants
        self.limit = limit
        self.gen_size = gen_size
        self.colony = colony
        self.rho = rho
        self.q = q
        self.top = top
        self.problem = problem
        self.gamma = gamma
        self.theta = theta
        self.inf = inf
        self.gamma = gamma
        self.sd_base = sd_base
        self.fail_indices = []
        self.fail_cnt = 0
        self.improve_cnt = 0
        self.success_cnt = 0
        self.solution = None
        self.solution_history = []
        self.circuits = None
        self.record = None
        self.previous_record = None
        self.is_new_record = False
        self._best = None

    @property
    def best(self):
        return self._best

    @best.setter
    def best(self, best):
        self.is_new_record = self.record is None or best < self.record
        if self.is_new_record:
            self.previous_record = self.record
            self.record = best
        self._best = best
