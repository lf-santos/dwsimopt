import numpy as np
from scipy import optimize
from pprint import pprint

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
os.chdir(dir_path)
os.chdir("../")
print(os.getcwd())

from pyDWSIMopt.interface.simulation import Simulation
from pyDWSIMopt.opt_problem import *