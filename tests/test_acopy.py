import acopy
import kiacopy
import tsplib95

problem = tsplib95.load_problem('bays29.tsp')
G = problem.get_graph()

solver = acopy.Solver()
colony = acopy.Colony()

solver.solve(G, colony, limit=100)

solver = kiacopy.Solver()
colony = kiacopy.Colony()
solver.solve(G, colony, gen_size=2, limit=100)
