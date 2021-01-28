import os

import acopy
import kiacopy
import tsplib95
import yaml
from logging import getLogger, StreamHandler, DEBUG
from kiacopy.parameter import Parameter

logger = getLogger()
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

graph_name: str = 'bays29.tsp'
problem = tsplib95.load_problem(graph_name)
G = problem.get_graph()

solver = acopy.Solver()
colony = acopy.Colony()

solver.solve(G, colony, limit=20)

config_path = os.path.join(os.path.dirname(__file__), 'config', 'normal.yaml')
parameter: Parameter = Parameter(yaml_path=config_path)

solver = kiacopy.Solver(parameter=parameter)
colony = kiacopy.Colony()
solver.solve(G, colony, problem, graph_name)
