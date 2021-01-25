from logging import getLogger, NullHandler
from kiacopy.colony import Colony
from kiacopy.colony import Colony
from kiacopy.solver import Solver
from kiacopy.solverplugin import SolverPlugin
from kiacopy.solution import Solution
from kiacopy.ants.ant import Ant
from kiacopy.ants.randomant import RandomAnt
from kiacopy.ants.sensitiveant import SensitiveAnt
from kiacopy import plugins
from kiacopy import utils
from kiacopy import ants

__author__ = """ganariya"""
__email__ = 'ganariya2525@gmail.com'
__version__ = '0.1.0'

getLogger(__name__).addHandler(NullHandler())
