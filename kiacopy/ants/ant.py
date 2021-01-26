# -*- coding: utf-8 -*-
import itertools
import bisect
import random
import copy
from typing import List, Tuple, Set, Dict, Optional

from networkx import Graph
from kiacopy.utils import positive
from kiacopy.circuit import Circuit
from kiacopy.grapher import Grapher


class Ant:
    """アリクラス."""

    def __init__(self, alpha: float = 1, beta: float = 3, **kwargs):
        self.alpha: float = alpha
        self.beta: float = beta
        self.is_res: bool = False
        self.inf: Optional[float] = None
        self.theta: Optional[float] = None
        self.circuit: Optional[Circuit] = None
        self.unvisited: Optional[List[int]] = None
        self.grapher: Optional[Grapher] = None

    @property
    def alpha(self) -> float:
        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        self._alpha = positive(value)

    @property
    def beta(self) -> float:
        return self._beta

    @beta.setter
    def beta(self, value: float):
        self._beta = positive(value)

    def __repr__(self) -> str:
        return f'Ant(alpha={self.alpha}, beta={self.beta})'

    def init_solution(self, graph: Graph, inf: float, is_res: bool, theta: float, grapher: Grapher, start: int = 1) -> None:
        """解を作るために初期化する.

        Parameters
        ----------
        graph:Graph
        inf:float
        is_res:bool
        theta:float
        start:int
            スタート頂点
        grapher: Grapher
            グラフをオーバーラップする

        Returns
        -------
        None
        """

        # start頂点をスタートとする閉路を初期化する
        self.circuit: Circuit = Circuit(graph, start, grapher, ant=self)
        self._init_unvisited_nodes(graph)
        self.inf = inf
        self.is_res = is_res
        self.theta = theta
        self.grapher = grapher

    def _init_unvisited_nodes(self, graph: Graph) -> None:
        """初期化時に　訪問していないスタート頂点以外のノードをリストに追加する"""
        self.unvisited: List[int] = []
        for node in graph[self.circuit.current]:
            if node not in self.circuit:
                self.unvisited.append(node)

    def move(self) -> None:
        """アリを次の頂点に移動させる.

        Notes
        -----
        solverクラスのfind_solutionにおいて呼び出される
        """
        next_node: int = self._choose_destination()
        current: int = self.circuit.current
        self.circuit.add_node(next_node)
        self.unvisited.remove(next_node)
        self.erase(current, next_node)

    def erase(self, now: int, to: int) -> None:
        """(now, to)のエッジの利用情報を登録する"""
        self.grapher.use((now, to))

    def _choose_destination(self) -> int:
        """次の移動先頂点を決定する.

        次の候補先のスコアを計算し (get_scores)
        とあるアルゴリズムで1頂点選ぶ (choose_node)

        Returns
        ------
        int
            次の移動先である頂点を返す
        """
        if len(self.unvisited) == 1:
            return self.unvisited[0]
        scores: List[float] = self._get_scores()
        return self._choose_node(scores)

    def _get_scores(self) -> List[float]:
        """今の頂点から移動できる移動先のスコアを計算する.

        Returns
        -------
        list of float
            移動先のスコアのリスト
        """
        scores: List[float] = []
        for to_node in self.unvisited:
            score: float = self._score_edge(self.circuit.current, to_node)
            if self.is_res:
                score /= self._score_residual(to_node)
            scores.append(score)
        return scores

    def _choose_node(self, scores: List[float]) -> int:
        """計算済みスコアを元に移動先頂点を1つ返す

        スコア値に比例した乱数で選択する

        Parameters
        ----------
        scores: list of float
            今の頂点の移動先の計算済みスコア

        Returns
        -------
        int
            移動先頂点

        Notes
        -----
        継承クラスで別の選択アルゴリズムが指定される
        """
        choices: List[int] = self.unvisited
        total: float = sum(scores)
        cumdist: List[float] = list(itertools.accumulate(scores)) + [total]
        index: int = bisect.bisect(cumdist, random.random() * total)
        return choices[min(index, len(choices) - 1)]

    def _score_edge(self, now: int, to: int) -> float:
        """ある1つの移動先頂点候補の1辺のスコアを返す.

        Parameters
        ----------
        now:int
        to:int

        Returns
        -------
        float
            1辺のスコア

        """
        weight: float = self.grapher.wei((now, to))
        pre: float = 1 / weight
        post = self.grapher.phe((now, to))
        return post ** self.alpha * pre ** self.beta

    def _score_residual(self, to: int) -> float:
        """toからの移動残余度を計算する

        今の頂点をv
        次の頂点候補をto
        toからの移動先をtotoとする。

        このとき、totoの数が小さければ小さいほどよいというのが結論。
        この値が小さい方が良い

        Parameters
        ----------
        graph: Graph
        to: int

        Returns
        -------
        float
            toに移動する場合の移動残余度
            toから移動できる超点数
        """

        # toから移動できるかなという候補群
        cands: Set[int] = set(copy.deepcopy(self.unvisited))
        cands.remove(to)

        # (to, toto)のエッジがすでに利用されているのであれば　totoの頂点はもう可能性がないのでbadに入れる
        bad: List[int] = []
        for cand in cands:
            if self.grapher.is_used((to, cand)):
                bad.append(cand)

        # badのだめなやつはもう移動できないので、候補から取り除く
        for x in bad:
            cands.remove(x)

        return max(1.0, len(cands) ** self.theta)
