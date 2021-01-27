import acopy
import kiacopy
import tsplib95
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger()
logger.addHandler(StreamHandler())
logger.setLevel(DEBUG)

problem = tsplib95.load_problem('bays29.tsp')
G = problem.get_graph()

solver = acopy.Solver()
colony = acopy.Colony()

solver.solve(G, colony, limit=100)

solver = kiacopy.Solver(R=3)
colony = kiacopy.Colony()
solver.solve(G, colony, gen_size=6, limit=300, is_best_opt=False, is_update=False)
