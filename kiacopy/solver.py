import collections
import time
import copy

from .state import State
from . import utils
from .solution import Solution


class Solver:

    def __init__(self, rho=.03, q=1, gamma=1, theta=2, inf=1e100, sd_base=1e20, top=None, plugins=None):
        self.rho = rho
        self.q = q
        self.top = top
        self.gamma = gamma
        self.theta = theta
        self.inf = inf
        self.sd_base = sd_base
        self.plugins = collections.OrderedDict()
        self.state = None
        if plugins:
            self.add_plugins(*plugins)

    def __repr__(self):
        return (f'{self.__class__.__name__}(rho={self.rho}, q={self.q}, '
                f'top={self.top})')

    def solve(self, *args, **kwargs):
        best = None
        for solution in self.optimize(*args, **kwargs):
            best = solution
        return best

    def optimize(self, graph, colony, gen_size=None, limit=None, problem=None, is_update=False, is_best_opt=False, is_res=False, graph_name=''):

        gen_size = gen_size or len(graph.nodes)
        ants = colony.get_ants(gen_size)
        state = State(graph=copy.deepcopy(graph), ants=ants, limit=limit, gen_size=gen_size,
                      colony=colony, rho=self.rho, q=self.q, top=self.top, problem=problem, gamma=self.gamma, theta=self.theta, inf=self.inf, sd_base=self.sd_base, is_update=is_update, is_res=is_res, is_best_opt=is_best_opt)
        self._call_plugins('start', state=state)
        prev_cost = self.inf

        print("-----optimize begin-----\n")

        for iterate_index in utils.looper(limit):
            copy_graph = copy.deepcopy(graph)

            solution = self.find_solution(copy_graph, state.ants, is_res=is_res)

            self._call_plugins('before', state=state)

            if is_best_opt and solution.cost > self.sd_base:
                self.opt2(copy_graph, solution, graph)

            if solution.cost > self.sd_base:
                state.fail_cnt += 1
                state.fail_indices.append(iterate_index)
            else:
                state.success_cnt += 1
                state.success_indices.append(iterate_index)

            if is_update:
                self.pheromone_update(solution, state, graph)

            if prev_cost > solution.cost:
                prev_cost = solution.cost
                state.improve_cnt += 1
                state.improve_indices.append(iterate_index)
                state.best_solution = solution
                print(iterate_index, "cycle: ", solution, "\n")
                yield solution

            state.solution_history.append(solution)
            state.solution = solution
            state.ants = ants
            state.circuits = list(solution)

            state.graph = copy.deepcopy(graph)

            self._call_plugins('iteration', state=state)

            if (iterate_index + 1) % 100 == 0:
                print("-----", iterate_index + 1, "times passed-----\n\n")

        state.end_time = time.perf_counter()
        state.elapsed = state.end_time - state.start_time
        self.state = state
        self._call_plugins('finish', state=state)

        print("-----result start-----\n")
        print(f"graph:{graph_name}, K:{gen_size}, time:{state.elapsed}")
        print(f"update:{is_update}, 2-best:{is_best_opt}, res:{is_res}")
        print(f"gamma:{state.gamma}, theta:{state.theta}, rho:{state.rho}, q:{state.q}, limit:{limit}")
        print(f"Improve:{state.improve_cnt}, Fail:{state.fail_cnt}, Success:{state.success_cnt}")
        if state.best_solution is not None:
            print(f"avg:{state.best_solution.avg}, sd:{state.best_solution.sd}, sum:{state.best_solution.sum}, cost:{state.best_solution.cost}")
            for circuit in state.best_solution: print(circuit)
            print()
        print("-----result end-----\n\n")

    def find_solution(self, graph, ants, is_res):
        for ant in ants:
            ant.init_solution(graph, inf=self.inf, is_res=is_res, theta=self.theta)
        # for ant in ants:
        #     for i in range(len(graph.nodes) - 1):
        #         ant.move(graph)
        for i in range(len(graph.nodes) - 1):
            for ant in ants:
                ant.move(graph)
            ants.sort(key=lambda x: x.circuit.cost, reverse=True)
        for ant in ants:
            ant.circuit.close()
            ant.erase(graph, ant.circuit.nodes[-1], ant.circuit.nodes[0])
        solution = Solution(self.gamma, self.theta, self.inf, self.sd_base)
        for ant in ants:
            solution.append(ant.circuit)
        return solution

    def pheromone_update(self, solution, state, graph):
        if solution.cost < self.sd_base:
            next_pheromones = collections.defaultdict(float)
            for circuit in solution:
                for edge in circuit:
                    next_pheromones[edge] += self.q / solution.cost
            for edge in state.graph.edges:
                p = graph.edges[edge]['pheromone']
                graph.edges[edge]['pheromone'] = (1 - self.rho) * p + next_pheromones[edge]

    def opt2(self, graph, solution, origin):
        edge_count = collections.defaultdict(int)
        for circuit in solution:
            for p in circuit:
                x = min(p[0], p[1])
                y = max(p[0], p[1])
                edge_count[(x, y)] += 1
                edge_count[(y, x)] += 1

        n = len(graph.nodes)
        for circuit in solution:
            nodes = circuit.nodes
            for i in range(0, n):
                best_cost = self.inf
                best_j = -1
                if edge_count[(nodes[i], nodes[(i + 1) % n])] > 1:
                    for j in range(0, n):
                        if i == j: continue

                        ii = min(i, j)
                        jj = max(i, j)
                        a = nodes[ii]
                        b = nodes[(ii + 1) % n]
                        c = nodes[jj]
                        d = nodes[(jj + 1) % n]

                        if edge_count[a, c] == 0 and edge_count[b, d] == 0:
                            dist = origin.edges[a, c]['weight'] + origin.edges[b, d]['weight'] - origin.edges[a, b]['weight'] - origin.edges[c, d]['weight']
                            if dist < best_cost:
                                best_cost = dist
                                best_j = j

                if best_j != -1:
                    ii = min(i, best_j)
                    jj = max(i, best_j)
                    a = nodes[ii]
                    b = nodes[(ii + 1) % n]
                    c = nodes[jj]
                    d = nodes[(jj + 1) % n]
                    if edge_count[a, c] == 0 and edge_count[b, d] == 0:
                        edge_count[a, b] -= 1
                        edge_count[b, a] -= 1
                        edge_count[c, d] -= 1
                        edge_count[d, c] -= 1
                        edge_count[a, c] += 1
                        edge_count[c, a] += 1
                        edge_count[b, d] += 1
                        edge_count[d, b] += 1
                        nodes[ii + 1: jj + 1] = reversed(nodes[ii + 1: jj + 1])
                        circuit.path = []
                        circuit.cost = 0
                        for k in range(n):
                            circuit.path.append((nodes[k], nodes[(k + 1) % n]))
                            circuit.cost += origin.edges[(nodes[k], nodes[(k + 1) % n])]['weight']

                        if edge_count[a, b] == 0:
                            graph.edges[a, b]['weight'] = origin.edges[a, b]['weight']
                            graph.edges[b, a]['weight'] = origin.edges[b, a]['weight']
                        if edge_count[c, d] == 0:
                            graph.edges[c, d]['weight'] = origin.edges[c, d]['weight']
                            graph.edges[d, c]['weight'] = origin.edges[d, c]['weight']

                        graph.edges[a, c]['weight'] = self.inf
                        graph.edges[c, a]['weight'] = self.inf
                        graph.edges[b, d]['weight'] = self.inf
                        graph.edges[d, b]['weight'] = self.inf

    def add_plugin(self, plugin):
        self.add_plugins(plugin)

    def add_plugins(self, *plugins):
        for plugin in plugins:
            plugin.initialize(self)
            self.plugins[plugin.__class__.__qualname__] = plugin

    def get_plugins(self):
        return self.plugins.values()

    def _call_plugins(self, hook, **kwargs):
        should_stop = False
        for plugin in self.get_plugins():
            try:
                plugin(hook, **kwargs)
            except StopIteration:
                should_stop = True
        return should_stop
