# -*- coding: utf-8 -*-
import collections
import random
import time
import os
import json

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

from .solverplugin import SolverPlugin


class Printout(SolverPlugin):
    _ROW = '{:<10} {:<20} {}'

    def initialize(self, solver):
        super().initialize(solver)
        self.iteration = 0

    def on_start(self, state):
        self.iteration = 0
        print(f'Using {state.gen_size} ants from {state.colony}')
        print(f'Performing {state.limit} iterations:')
        print(self._ROW.format('Iteration', 'Cost', 'Solution'))

    def on_iteration(self, state):
        self.iteration += 1
        line = self._ROW.format(self.iteration, state.best.cost,
                                state.best.get_easy_id())
        print(line, end='\n' if state.is_new_record else '\r')

    def on_finish(self, state):
        print('Done' + ' ' * (32 + 2 * len(state.graph)))


class InitialEdgePheromone(SolverPlugin):

    def __init__(self, q=1):
        super().__init__()
        self.q = q

    def on_start(self, state):
        for edge in state.graph.edges:
            if state.graph.edges[edge]['weight'] == 0:
                state.graph.edges[edge]['weight'] = 1e100
            state.graph.edges[edge]['pheromone'] = self.q / state.graph.edges[edge]['weight']


class InitialNeighborPheromone(SolverPlugin):

    def __init__(self, graph, start=1):
        super().__init__()
        self.start = start
        self.nodes = [self.start]
        self.cost = 0
        self.tau_0 = 0

        n = len(graph)
        current = self.start

        unvisited = [x for x in graph.nodes() if x != self.start]
        while unvisited:
            costs = [graph.edges[current, x]['weight'] for x in unvisited]
            index = np.argmin(costs)
            self.cost += np.min(costs)
            current = unvisited[index]
            del unvisited[index]
        self.cost += graph.edges[current, self.start]['weight']
        self.tau_0 = 1 / (n * self.cost)
        for u, v in graph.edges:
            graph.edges[u, v].setdefault('pheromone', self.tau_0)


class EliteTracer(SolverPlugin):

    def __init__(self, factor=1):
        super().__init__(factor=factor)
        self.factor = factor

    def on_iteration(self, state):
        state.best.trace(self.solver.q * self.factor)


class MaxMinPheromoneRestrict(SolverPlugin):

    def __init__(self, p_best=0.05, save_path='.', leading=''):
        super().__init__()
        self.p_best = p_best
        self.save_path = save_path
        self.leading = leading
        self.tau_maxs = []
        self.tau_mins = []
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

    def on_iteration(self, state):
        record_cost = state.record.cost
        rho = state.rho
        n = state.graph.number_of_nodes()

        tau_max = (1 / rho) * (1 / record_cost)
        tau_min = (tau_max * (1 - self.p_best ** (1 / n))) / ((n / 2 - 1) * (self.p_best ** (1 / n)))

        for edge in state.graph.edges():
            p = state.graph.edges[edge]['pheromone']
            p = min(tau_max, max(tau_min, p))
            state.graph.edges[edge]['pheromone'] = p

        self.tau_maxs.append(tau_max)
        self.tau_mins.append(tau_min)

    def draw(self, state):
        fig = plt.figure(dpi=200)
        x = list(range(len(self.tau_maxs)))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x, self.tau_mins, label='min')
        ax.plot(x, self.tau_maxs, label='max')
        ax.set_title('MaxMin Pheromone')
        ax.legend()
        fig.show()
        fig.savefig(os.path.join(self.save_path, self.leading + '_maxmin_pheromone.png'))

    def on_finish(self, state):
        super().on_finish(state)
        self.draw(state)


class Opt2Swap(SolverPlugin):
    def __init__(self, opt2=10):
        super().__init__()
        self.opt2 = opt2
        self.swaps = 0

    def on_before(self, state):
        solutions = state.solutions
        graph = state.graph
        n = len(graph.nodes)

        for s in solutions:
            while True:
                x, y = random.randint(0, n - 1), random.randint(0, n - 1)
                if x > y:
                    x, y = y, x
                if x != y:
                    break
            dist_a = graph.edges[s.nodes[x], s.nodes[x + 1]]['weight']
            dist_b = graph.edges[s.nodes[y], s.nodes[(y + 1) % n]]['weight']
            dist_c = graph.edges[s.nodes[x], s.nodes[y]]['weight']
            dist_d = graph.edges[s.nodes[x + 1], s.nodes[(y + 1) % n]]['weight']
            if dist_a + dist_b > dist_c + dist_d:
                s.nodes[x + 1: y + 1] = reversed(s.nodes[x + 1: y + 1])
                s.cost += dist_c + dist_d - dist_a - dist_b
                s.reconstruct()
                self.swaps += 1


class ConvertStateToJson(SolverPlugin):
    def __init__(self, save_path='json_data', leading='', name='data'):
        super().__init__()
        self.file_name = os.path.join(save_path, f'{name}_{leading}.json')
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

    def convert(self, state):
        result = {}
        result['graph_size'] = len(state.graph)
        result['graph_name'] = state.problem.name
        result['limit'] = state.limit
        result['gen_size'] = state.gen_size
        result['rho'] = state.rho
        result['q'] = state.q
        result['top'] = state.top
        result['gamma'] = state.gamma
        result['theta'] = state.theta
        result['inf'] = state.inf
        result['sd_base'] = state.sd_base
        result['elapsed'] = state.elapsed
        result['is_update'] = state.is_update
        result['is_res'] = state.is_res
        result['is_best_opt'] = state.is_best_opt
        result['fail_indices'] = state.fail_indices
        result['fail_cnt'] = state.fail_cnt
        result['improve_indices'] = state.improve_indices
        result['improve_cnt'] = state.improve_cnt
        result['success_indices'] = state.success_indices
        result['success_cnt'] = state.success_cnt
        result['history'] = []

        for i in range(len(state.solution_history)):

            his = {}
            his['avg'] = state.solution_history[i].avg
            his['cost'] = state.solution_history[i].cost
            his['sd'] = state.solution_history[i].cost
            his['sum'] = state.solution_history[i].sum

            his['circuits'] = []
            for circuit in state.solution_history[i]:
                pro = {}
                pro['cost'] = circuit.cost
                pro['nodes'] = circuit.nodes
                pro['path'] = circuit.path
                pro['alpha'] = circuit.ant.alpha
                pro['beta'] = circuit.ant.beta
                his['circuits'].append(pro)

            result['history'].append(his)

        return result

    def on_finish(self, state):
        result = self.convert(state)
        with open(self.file_name, mode='w') as f:
            json.dump(result, f, ensure_ascii=False)


class PeriodicActionPlugin(SolverPlugin):
    def __init__(self, period=50):
        super().__init__(period=period)
        self.period = period
        self.index = None

    def initialize(self, solver):
        super().initialize(solver)
        self.index = 0

    def on_iteration(self, state):
        self.index = (self.index + 1) % self.period
        if not self.index:
            self.action(state)

    def action(self, state):
        pass


class PeriodicReset(PeriodicActionPlugin):

    def __init__(self, period=50):
        super().__init__(period=period)

    def action(self, state):
        for edge in state.graph.edges:
            state.graph.edges[edge]['pheromone'] = 0


class PheromoneFlip(PeriodicActionPlugin):

    def __init__(self, period=50):
        super().__init__(period=period)

    def action(self, state):
        data = []
        for edge in state.graph.edges.values():
            datum = edge['pheromone'], edge
            data.append(datum)
        levels, edges = zip(*data)
        for edge, level in zip(edges, reversed(levels)):
            edge['pheromone'] = level


class Timer(SolverPlugin):

    def initialize(self, solver):
        super().initialize(solver)
        self.start_time = None
        self.finish = None
        self.duration = None

    def on_start(self, state):
        self.start_time = time.time()

    def on_finish(self, state):
        self.finish = time.time()
        self.duration = self.finish - self.start_time
        self.time_per_iter = self.duration / state.limit

    def get_report(self):
        return '\n'.join([
            f'Total time: {self.duration} seconds',
            f'Avg iteration time: {self.time_per_iter} seconds',
        ])


class Darwin(SolverPlugin):

    def __init__(self, sigma=.1):
        super().__init__(sigma=sigma)
        self.sigma = sigma

    def on_start(self, state):
        size = len(state.ants)
        self.alpha = sum(ant.alpha for ant in state.ants) / size
        self.beta = sum(ant.beta for ant in state.ants) / size

    def on_iteration(self, state):
        alpha = (self.alpha + state.best.ant.alpha) / 2
        beta = (self.beta + state.best.ant.beta) / 2
        for ant in state.ants:
            ant.alpha = random.gauss(alpha, self.sigma)
            ant.beta = random.gauss(beta, self.sigma)


class EarlyTerminationPlugin(SolverPlugin):
    def on_iteration(self, state):
        if self.should_terminate(state):
            raise StopIteration()

    def should_terminate(self, state):
        raise NotImplementedError()


class Threshold(EarlyTerminationPlugin):

    def __init__(self, threshold):
        super().__init__(threshold=threshold)
        self.threshold = threshold

    def should_terminate(self, state):
        return state.record.cost <= self.threshold


class TimeLimit(EarlyTerminationPlugin):

    def __init__(self, seconds):
        super().__init__(seconds=seconds)
        self.limit = seconds

    def on_start(self, state):
        self.start_time = time.time()

    def should_terminate(self, state):
        duration = time.time() - self.start_time
        return duration >= self.limit


class DrawGraph(SolverPlugin):
    def __init__(self, problem, save_path='.', leading='', is_iteration=False, is_finish=True, is_save=False, is_label=False, is_each=False, is_consecutive=False):
        super().__init__()
        self.pos = problem.display_data or problem.node_coords
        self.save_path = save_path
        self.leading = leading
        self.is_iteration = is_iteration
        self.is_finish = is_finish
        self.is_save = is_save
        self.is_label = is_label
        self.is_each = is_each
        self.is_consecutive = is_consecutive
        if not os.path.isdir(save_path):
            os.mkdir(save_path)

    def on_iteration(self, state):
        if self.is_iteration:
            self.draw(state)

    def on_finish(self, state):
        if self.is_save:
            self.save(state)
        if self.is_finish:
            self.draw(state)

    def draw(self, state):
        self.draw_all(state)
        if self.is_each:
            self.draw_each(state)
        if self.is_consecutive:
            self.draw_consecutive(state)

    def draw_all(self, state):
        plt.figure(dpi=200)
        _, ax = plt.subplots()
        nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)

        colors = ["red", "blue", "green", "pink", "orange", "yellow", "brown", "purple", "gray", "gold", "silver"]

        for i in range(len(state.best_solution)):
            nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.best_solution[i].path, arrows=True, edge_color=colors[i])

        # for circuit in state.best_solution:
        #     r,g,b = random.random(), random.random(), random.random()
        #     nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=circuit.path, arrows=True, edge_color=(r, g, b))

        if self.is_label:
            labels = {x: str(x) for x in state.graph.nodes}
            nx.draw_networkx_labels(state.graph, pos=self.pos, labels=labels, font_color='white')
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.title("all paths")
        plt.show()

    def draw_each(self, state):
        colors = ["red", "blue", "green", "pink", "orange", "yellow", "brown", "purple", "gray", "gold", "silver"]

        for i in range(len(state.best_solution)):
            plt.figure(dpi=200)
            _, ax = plt.subplots()
            nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)
            nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.best_solution[i].path, arrows=True, edge_color=colors[i])
            if self.is_label:
                labels = {x: str(x) for x in state.graph.nodes}
                nx.draw_networkx_labels(state.graph, pos=self.pos, labels=labels, font_color='white')
            ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
            plt.title(f"each path: {i + 1} {state.best_solution[i].cost}")
            plt.show()

    def draw_consecutive(self, state):
        colors = ["red", "blue", "green", "pink", "orange", "yellow", "brown", "purple", "gray", "gold", "silver"]
        N = len(state.graph)

        for i in range(N):
            plt.figure(dpi=200)
            _, ax = plt.subplots()
            nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)
            for j in range(len(state.best_solution)):
                nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.best_solution[j].path[0:i + 1], arrows=True, edge_color=colors[j])

            if self.is_label:
                labels = {x: str(x) for x in state.graph.nodes}
                nx.draw_networkx_labels(state.graph, pos=self.pos, labels=labels, font_color='white')
            ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
            plt.title(f"consecutive paths: {i + 1}")
            plt.show()

    def save(self, state):
        plt.figure(dpi=200)
        _, ax = plt.subplots()
        nx.draw_networkx_nodes(state.graph, pos=self.pos, ax=ax)
        nx.draw_networkx_edges(state.graph, pos=self.pos, edgelist=state.record.path, arrows=False)
        if self.is_label:
            labels = {x: str(x) for x in state.graph.nodes}
            nx.draw_networkx_labels(state.graph, pos=self.pos, labels=labels, font_color='white')
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        plt.savefig(os.path.join(self.save_path, self.leading + '_graph_record.png'))


class StatsRecorder(SolverPlugin):

    def __init__(self, save_path=".", file_name="stats"):
        super().__init__()
        self.stats = collections.defaultdict(list)
        self.data = {'circuits': set()}
        self.save_path = save_path
        self.file_name = os.path.join(save_path, file_name + ".json")

    def on_start(self, state):
        levels = [edge['pheromone'] for edge in state.graph.edges.values()]
        num_edges = len(levels)
        total_pheromone = sum(levels)

        stats = {
            'pheromone_levels': levels,
            'total_pheromone': total_pheromone,
            'edge_pheromone': {
                'min': min(levels),
                'max': max(levels),
                'avg': total_pheromone / num_edges,
            },
            'circuits': {
                'min_circuit': None,
                'max_circuit': None,
            },
            'solution': {
                'average_cost': None,
                'sum_cost': None,
                'sd_cost': None,
                'weighted_cost': None
            },
            'average': {
                'average_cost': None,
            },
            'sum': {
                'sum_cost': None,
            },
            'sd': {
                'sd_cost': None,
            },
            'weighted': {
                'weighted_cost': None
            },
            'unique_solutions': {
                'total': len(self.data['circuits']),
                'iteration': 0,
                'new': 0,
            }
        }
        self.pump(stats)

    def on_iteration(self, state):
        levels = [edge['pheromone'] for edge in state.graph.edges.values()]
        distances = [(circuit.cost if circuit.cost <= 1e30 else None) for circuit in state.circuits]

        circuits = set()
        for circuit in state.circuits:
            if circuit.cost <= 1e30:
                circuits.add(circuit)
        solutions_seen = self.data['circuits']

        old_count = len(solutions_seen)
        solutions_seen.update(circuits)
        num_new_solutions = len(solutions_seen) - old_count

        num_edges = len(levels)
        total_pheromone = sum(levels)

        stats = {
            'pheromone_levels': levels,
            'total_pheromone': total_pheromone,
            'edge_pheromone': {
                'min': min(levels),
                'max': max(levels),
                'avg': total_pheromone / num_edges,
            },
            'circuits': {
                'min_circuit': min(distances) if (None not in distances) else None,
                'max_circuit': max(distances) if (None not in distances) else None,
                'diff_circuit': max(distances) - min(distances) if (None not in distances) else None
            },
            'solution': {
                'average_cost': state.solution.avg if state.solution.avg <= 1e30 else None,
                'sum_cost': state.solution.sum if state.solution.sum <= 1e30 else None,
                'sd_cost': state.solution.sd if state.solution.sd <= 1e30 else None,
                'weighted_cost': state.solution.cost if state.solution.cost <= 1e30 else None,
            },
            'average': {
                'average_cost': state.solution.avg if state.solution.avg <= 1e30 else None,
            },
            'sum': {
                'sum_cost': state.solution.sum if state.solution.sum <= 1e30 else None,
            },
            'sd': {
                'sd_cost': state.solution.sd if state.solution.sd <= 1e30 else None,
            },
            'weighted': {
                'weighted_cost': state.solution.cost if state.solution.cost <= 1e30 else None,
            },
            'unique_solutions': {
                'total': len(self.data['circuits']),
                'iteration': len(circuits),
                'new': num_new_solutions,
            }
        }
        self.pump(stats)

    def pump(self, stats):
        for stat, data in stats.items():
            self.stats[stat].append(data)

    def save(self):
        if not os.path.isdir(self.save_path):
            os.mkdir(self.save_path)
        with open(self.file_name, 'w') as f:
            json.dump(self.stats, f, ensure_ascii=False)
