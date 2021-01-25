from collections import defaultdict
from typing import DefaultDict, Tuple, Final

from kiacopy.solution import Solution
from networkx import Graph


def best_opt2(graph: Graph, solution: Solution, origin: Graph, inf: float):
    edge_count: DefaultDict[Tuple[int, int], int] = defaultdict(int)
    for circuit in solution:
        for p in circuit:
            x: int = min(p[0], p[1])
            y: int = max(p[0], p[1])
            edge_count[(x, y)] += 1
            edge_count[(y, x)] += 1

    N: Final[int] = len(graph.nodes)
    for circuit in solution:
        nodes = circuit.nodes
        for i in range(0, N):
            best_cost: float = inf
            best_j: int = -1
            if edge_count[(nodes[i], nodes[(i + 1) % N])] > 1:
                for j in range(0, N):
                    if i == j:
                        continue
                    ii = min(i, j)
                    jj = max(i, j)
                    a = nodes[ii]
                    b = nodes[(ii + 1) % N]
                    c = nodes[jj]
                    d = nodes[(jj + 1) % N]

                    if edge_count[a, c] == 0 and edge_count[b, d] == 0:
                        dist = origin.edges[a, c]['weight'] + origin.edges[b, d]['weight'] - origin.edges[a, b]['weight'] - origin.edges[c, d]['weight']
                        if dist < best_cost:
                            best_cost = dist
                            best_j = j

            if best_j != -1:
                ii = min(i, best_j)
                jj = max(i, best_j)
                a = nodes[ii]
                b = nodes[(ii + 1) % N]
                c = nodes[jj]
                d = nodes[(jj + 1) % N]
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
                    for k in range(N):
                        circuit.path.append((nodes[k], nodes[(k + 1) % N]))
                        circuit.cost += origin.edges[(nodes[k], nodes[(k + 1) % N])]['weight']

                    if edge_count[a, b] == 0:
                        graph.edges[a, b]['weight'] = origin.edges[a, b]['weight']
                        graph.edges[b, a]['weight'] = origin.edges[b, a]['weight']
                    if edge_count[c, d] == 0:
                        graph.edges[c, d]['weight'] = origin.edges[c, d]['weight']
                        graph.edges[d, c]['weight'] = origin.edges[d, c]['weight']

                    graph.edges[a, c]['weight'] = inf
                    graph.edges[c, a]['weight'] = inf
                    graph.edges[b, d]['weight'] = inf
                    graph.edges[d, b]['weight'] = inf
