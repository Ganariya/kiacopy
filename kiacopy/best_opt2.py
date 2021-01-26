from collections import defaultdict
from typing import DefaultDict, Tuple, Final

from networkx import Graph
from kiacopy.solution import Solution
from kiacopy.grapher import Grapher

INF: Final[float] = 1e20


def best_opt2(graph: Graph, solution: Solution, grapher: Grapher) -> None:
    """best-opt2を実行する

    Parameters
    ----------
    graph:Graph
    solution:Solution
    grapher: Grapher

    Returns
    -------
    None
    """
    N: Final[int] = len(graph.nodes)

    for circuit in solution:
        nodes = circuit.nodes

        # 移動元ノードのidx=i
        for i in range(N):
            best_cost: float = INF
            best_j: int = -1

            # もしi番目のノードからの移動が2回以上使用されていたら
            if grapher.dp[nodes[i]][nodes[(i + 1) % N]] > 1:

                # 他の順番であるj番目のノードを調べる
                for j in range(N):
                    if i == j:
                        continue
                    ii = min(i, j)
                    jj = max(i, j)
                    a = nodes[ii]
                    b = nodes[(ii + 1) % N]
                    c = nodes[jj]
                    d = nodes[(jj + 1) % N]

                    # 交換可能であれば
                    if not grapher.is_used((a, c)) and not grapher.is_used((b, d)):
                        # if grapher.dp[a][c] == 0 and grapher.dp[b][d] == 0:
                        # if edge_count[a, c] == 0 and edge_count[b, d] == 0:
                        dist = grapher.nwei((a, c)) + grapher.nwei((b, d)) - grapher.nwei((a, b)) - grapher.nwei((c, d))
                        # dist = origin.edges[a, c]['weight'] + origin.edges[b, d]['weight'] - origin.edges[a, b]['weight'] - origin.edges[c, d]['weight']
                        if dist < best_cost:
                            best_cost = dist
                            best_j = j

            # 交換可能なものがあれば
            if best_j != -1:
                ii = min(i, best_j)
                jj = max(i, best_j)
                a = nodes[ii]
                b = nodes[(ii + 1) % N]
                c = nodes[jj]
                d = nodes[(jj + 1) % N]
                if not grapher.is_used((a, c)) and not grapher.is_used((b, d)):
                    grapher.unuse((a, b))
                    grapher.unuse((c, d))
                    grapher.use((a, c))
                    grapher.use((b, d))
                    nodes[ii + 1: jj + 1] = reversed(nodes[ii + 1: jj + 1])
                    circuit.path = []
                    circuit.cost = 0
                    for k in range(N):
                        circuit.path.append((nodes[k], nodes[(k + 1) % N]))
                        circuit.cost += grapher.nwei((nodes[k], nodes[(k + 1) % N]))
