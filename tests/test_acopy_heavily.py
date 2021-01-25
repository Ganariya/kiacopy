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

solver = kiacopy.Solver()
colony = kiacopy.Colony()
solver.solve(G, colony, gen_size=5, limit=500, is_best_opt=True, is_update=True)
