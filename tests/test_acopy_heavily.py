import os

import acopy
import kiacopy
import tsplib95
from logging import getLogger, StreamHandler, DEBUG, INFO
from kiacopy.parameter import Parameter

logger = getLogger()
logger.addHandler(StreamHandler())
logger.setLevel(INFO)

graph_name: str = 'bays29.tsp'
problem = tsplib95.load_problem(graph_name)
G = problem.get_graph()

solver = acopy.Solver()
colony = acopy.Colony()

solver.solve(G, colony, limit=100)

config_path = os.path.join(os.path.dirname(__file__), 'config', 'heavily.yaml')
parameter: Parameter = Parameter.create(config_path)

solver = kiacopy.Solver(parameter=parameter)
recorder = kiacopy.plugins.StatsRecorder('results')
plotter = kiacopy.utils.plot.Plotter(stats=recorder.stats)
drawer = kiacopy.plugins.DrawGraph(problem=problem, is_each=True, is_label=True)
converter = kiacopy.plugins.ConvertStateToJson(save_path='results')
solver.add_plugins(recorder, drawer, converter)

colony = kiacopy.Colony()
solver.solve(G, colony, problem, graph_name)

plotter.plot()
