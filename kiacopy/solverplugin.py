class SolverPlugin:
    """Solver plugin.

    Solver plugins can be added to any solver to customize its behavior.
    Plugins are initialized once when added, once before the first solver
    iteration, once after each solver iteration has completed, and once after
    all iterations have completed.

    Implementing each hook is optional.
    """

    #: unique name
    name = 'plugin'

    def __init__(self, **kwargs):
        self._params = kwargs

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in self._params.items())
        return f'<{self.__class__.__qualname__}({params})>'

    def __call__(self, hook, **kwargs):
        return getattr(self, f'on_{hook}')(**kwargs)

    def initialize(self, solver):
        """Perform actions when being added to a solver.

        Though technically not required, this method should be probably be
        idempotent since the same plugin could be added to the same solver
        multiple times (perhaps even by mistake).

        :param solver: the solver to which the plugin is being added
        :type solver: :class:`acopy.solvers.Solver`
        """
        self.solver = solver

    def on_start(self, state):
        """Perform actions before the first iteration.

        :param state: solver state
        :type state: :class:`acopy.solvers.State`
        """
        pass

    def on_before(self, state):
        """Perform actions before the global update

        :param state: solver state
        :type state: :class:`acopy.solvers.State`
        """

    def on_iteration(self, state):
        """Perform actions after each iteration.

        :param state: solver state
        :type state: :class:`acopy.solvers.State`
        """
        pass

    def on_finish(self, state):
        """Perform actions once all iterations have completed.

        :param state: solver state
        :type state: :class:`acopy.solvers.State`
        """
        pass
