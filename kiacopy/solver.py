import time
import copy

from typing import Optional, List, DefaultDict, Tuple, Final
from collections import OrderedDict, defaultdict
from logging import getLogger

from networkx import Graph
from tsplib95.models import Problem
from kiacopy import utils
from kiacopy.grapher import Grapher
from kiacopy.ants import Ant
from kiacopy.state import State
from kiacopy.solution import Solution, COST_KIND
from kiacopy.colony import Colony
from kiacopy.solverplugin import SolverPlugin
from kiacopy.best_opt2 import best_opt2
from kiacopy.parameter import Parameter

logger = getLogger(__name__)


class Solver:
    """Solver class.

    API呼び出しのインターフェース
    共通化できるパラメータはinit時に呼び出す
    """

    def __init__(self, parameter: Parameter, plugins=None) -> None:
        self.rho: float = parameter.rho
        self.q: float = parameter.q
        self.top: Optional[int] = parameter.top
        self.gamma: float = parameter.gamma
        self.theta: float = parameter.theta
        self.inf: float = parameter.inf
        self.limit: int = parameter.limit
        self.gen_size: int = parameter.gen_size
        self.R: Final[int] = parameter.R
        self.cost_kind: COST_KIND = parameter.cost_kind
        self.is_best_opt: bool = parameter.is_best_opt
        self.is_res: bool = parameter.is_res
        self.is_update: bool = parameter.is_update
        self.is_multiple: bool = parameter.is_multiple
        self.parameter: Parameter = parameter
        self.plugins: OrderedDict = OrderedDict()
        self.state: Optional[State] = None
        if plugins:
            self.add_plugins(*plugins)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}(rho={self.rho}, q={self.q}, gamma={self.gamma} theta={self.theta}'
                f'top={self.top}, R={self.R}), limit={self.limit}')

    def solve(self, graph: Graph, colony: Colony, problem: Problem, graph_name: str) -> Solution:
        best = None
        for solution in self.optimize(graph, colony, problem, graph_name):
            best = solution
        return best

    def optimize(self, graph: Graph, colony: Colony, problem: Problem, graph_name: str) -> Solution:
        ants: List[Ant] = colony.get_ants(self.gen_size)
        bar_str: Final[str] = "----------------"
        prev_cost: float = self.inf
        state: State = State(graph=copy.deepcopy(graph), ants=ants, limit=self.limit, gen_size=self.gen_size,
                             colony=colony, rho=self.rho, q=self.q, top=self.top, problem=problem, gamma=self.gamma,
                             theta=self.theta, inf=self.inf, R=self.R, is_update=self.is_update, is_res=self.is_res, is_best_opt=self.is_best_opt, is_multiple=self.is_multiple)

        self._call_plugins('start', state=state)
        logger.info(f"{bar_str} optimize begin {bar_str}")

        for iterate_index in utils.looper(self.limit):

            grapher: Grapher = Grapher(graph)
            solution: Solution = self.find_solution(graph, state.ants, grapher, is_res=self.is_res)

            self._call_plugins('before', state=state)

            if self.is_best_opt:
                self.best_opt2(graph, solution, grapher)
            if self.is_update:
                self.pheromone_update(solution, state, graph)

            duplicate: int = max(0, solution.duplicate - self.R)
            if duplicate == 0:
                state.success_cnt += 1
                state.success_indices.append(iterate_index)
            else:
                state.fail_cnt += 1
                state.fail_indices.append(iterate_index)

            if prev_cost > solution.cost:
                prev_cost: float = solution.cost
                state.improve_cnt += 1
                state.improve_indices.append(iterate_index)
                state.best_solution = solution
                logger.info(f'[Better Solution] {iterate_index}-cycle: {solution}')
                yield solution

            state.solution_history.append(solution)
            state.solution = solution
            state.ants = ants
            state.circuits = list(solution)
            state.graph = copy.deepcopy(graph)
            state.duplicate_indicates.append(duplicate)

            self._call_plugins('iteration', state=state)

            if (iterate_index + 1) % 100 == 0:
                logger.info(f"{bar_str} {iterate_index + 1} times passed {bar_str}")

        state.end_time = time.perf_counter()
        state.elapsed = state.end_time - state.start_time
        self.state = state
        self._call_plugins('finish', state=state)

        logger.info(f"{bar_str} result {bar_str}")
        logger.info(f"[GRAPH_NAME] {graph_name} ")
        logger.info(f"[NUM_OF_ANTS] {self.gen_size} ")
        logger.info(f"[TIME] {state.elapsed} ")
        logger.info(f"[UPDATE] update:{self.is_update} 2-best:{self.is_best_opt} res:{self.is_res}")
        logger.info(f"[PARAMETERS] gamma:{state.gamma} theta:{state.theta} rho:{state.rho} limit:{self.limit}")
        logger.info(f"[COUNT] Improve:{state.improve_cnt} Failure:{state.fail_cnt} Success:{state.success_cnt}")
        if state.best_solution is not None:
            logger.info(f"[BEST_SOLUTION] solution:{state.best_solution}")
            for idx, circuit in enumerate(state.best_solution):
                logger.info(f"circuit-{idx} {circuit}")
        logger.info(f"{bar_str} end {bar_str}")

    def find_solution(self, graph: Graph, ants: List[Ant], grapher: Grapher, is_res: bool) -> Solution:
        """ソリューションを1つ構築する.

        ソリューション = K個の閉路

        # for ant in ants:
        #     for i in range(len(graph.nodes) - 1):
        #         ant.move(graph)

        Notes
        -----
        アリはすでに用意されており初期解のみ初期化する
        """
        for ant in ants:
            ant.init_solution(graph, inf=self.inf, is_res=is_res, theta=self.theta, grapher=grapher)
        # sdの場合
        for i in range(len(graph.nodes) - 1):
            for ant in ants:
                ant.move()
            ants.sort(key=lambda x: x.circuit.cost, reverse=False)

        # sumの場合
        # for ant in ants:
        #     for i in range(len(graph.nodes) - 1):
        #         ant.move()
        for ant in ants:
            ant.circuit.close()
            ant.erase(ant.circuit.nodes[-1], ant.circuit.nodes[0])
        solution: Solution = Solution(self.gamma, self.theta, self.inf, self.cost_kind)
        for ant in ants:
            solution.append(ant.circuit)
        return solution

    def pheromone_update(self, solution: Solution, state: State, graph: Graph) -> None:
        dup: int = max(0, solution.duplicate - self.R)
        next_pheromones: DefaultDict[Tuple[int, int], float] = defaultdict(float)
        for circuit in solution:
            for edge in circuit:
                r = Grapher.minmax(edge)
                next_pheromones[r] += self.q / ((solution.cost + circuit.cost) * (2 ** dup))
        for edge in state.graph.edges:
            p = graph.edges[edge]['pheromone']
            graph.edges[edge]['pheromone'] = (1 - self.rho) * p + next_pheromones[edge]

    def best_opt2(self, graph: Graph, solution: Solution, grapher: Grapher) -> None:
        best_opt2(graph, solution, grapher)

    def add_plugin(self, plugin: SolverPlugin) -> None:
        self.add_plugins(plugin)

    def add_plugins(self, *plugins):
        for plugin in plugins:
            plugin.initialize(self)
            self.plugins[plugin.__class__.__qualname__] = plugin

    def get_plugins(self):
        return self.plugins.values()

    def _call_plugins(self, hook: str, **kwargs) -> bool:
        should_stop = False
        for plugin in self.get_plugins():
            try:
                plugin(hook, **kwargs)
            except StopIteration:
                should_stop = True
        return should_stop
