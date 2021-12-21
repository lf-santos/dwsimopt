import numpy as np
from scipy import optimize
from pprint import pprint

import os 
from pathlib import Path
try:
    dir_path = os.path.dirname(__file__) # This is your Project Root
except:
    dir_path = os.path.abspath(os.getcwd())
if dir_path.find('examples')>-1:
    dir_path = '\\'.join(dir_path.split('\\')[0:-2])
print(dir_path)

gop_solver = 'bb'

import sys
if 'dwsimopt.sim_opt' in sys.modules:  # Is the module in the register?
    del sys.modules['dwsimopt.sim_opt']  # If so, remove it.
    del SimulationOptimization
    print('hi')
from dwsimopt.sim_opt import SimulationOptimization

# Getting DWSIM path from system path
for k,v in enumerate(os.environ['path'].split(';')):
    if v.find('\DWSIM')>-1:
        path2dwsim = os.path.join(v, '')
if path2dwsim == None:
    path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"

# Loading DWSIM simulation into Python (Simulation object)
sim_smr = SimulationOptimization(dof=np.array([]), path2sim= os.path.join(dir_path, "examples\\SMR_LNG\\SMR.dwxmz"), 
                     path2dwsim = path2dwsim)
sim_smr.savepath = os.path.join(dir_path, "examples\\SMR_LNG\\SMR2.dwxmz")
sim_smr.add_refs()

# Instanciate automation manager object
from DWSIM.Automation import Automation2
if ('interf' not in locals()):    # create automation manager
    interf = Automation2()

# Connect simulation in sim.path2sim
sim_smr.connect(interf)

# Add dof
sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(7,x))
sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(0,x))
sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(1,x))
sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(2,x))
sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(5,x))
def set_property(x, obj):
    obj = x
sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("VALV-01").OutletPressure) )
sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4").POut) )
sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-08").OutletTemperature) )
# adding objective function (f_i):
sim_smr.add_fobj(lambda : sim_smr.flowsheet.GetFlowsheetSimulationObject("Sum_W").EnergyFlow)
# adding constraints (g_i <= 0):
sim_smr.add_constraint(np.array([
      lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'],
      lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'],
    #   lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction, # no phase separation in the cycle
    #   lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction, # no phase separation in the cycle
    #   lambda : 10*(1 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").Phases[1].Properties.massfraction), # phase separation before MSHE
]))

pprint(vars(sim_smr))

# Initial simulation optimization setup
# Initial guess of optimization
x0 = np.array( [0.25/3600, 0.70/3600, 1.0/3600, 1.10/3600, 1.80/3600, 2.50e5, 50.00e5, -60+273.15] )

# Testing for simulation at x0
sim_smr.calculate_optProblem(1.0*x0)
print(sim_smr.x_val,
      sim_smr.f_val,
      sim_smr.g_val)

# Test saving simulation at x0 in 'savepath'
sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet,sim_smr.savepath,True)

# Inspecting simulation object
pprint(vars(sim_smr))

# Setup for optimization
# convergence tolerances
xtol=0.01
ftol=0.01
maxiter=5 # +- 20 seconds per iteration

# decision variables bounds
bounds_raw = np.array( [0.5*np.asarray(x0), 1.5*np.asarray(x0)] )   # 50 % around base case
bounds_raw[0][-1] = 153     # precool temperature low limit manually
bounds_raw[1][-1] = 253     # precool temperature upper limit manually

# regularizer calculation
regularizer = np.zeros(x0.size)
import math
for i in range(len(regularizer)):
    regularizer[i] = 10**(-1*math.floor(math.log(x0[i],10))) # regularizer for magnitude order of 1e0

# bounds regularized
bounds_reg = regularizer*bounds_raw
bounds = optimize.Bounds(bounds_reg[0], bounds_reg[1])

# objective and constraints lambda definitions
f = lambda x: sim_smr.calculate_optProblem(np.asarray(x)/regularizer)[0:sim_smr.n_f]
g = lambda x: sim_smr.calculate_optProblem(np.asarray(x)/regularizer)[sim_smr.n_f:(sim_smr.n_f+sim_smr.n_g)]
nonlinear_constraint = optimize.NonlinearConstraint(g, -np.inf, 0, jac='2-point', hess=optimize.BFGS())

# if gop_solver == 'bb':
#     import black_box as bb

#     def fpen(x):
#         return sim_smr.fpen_barrier(x/regularizer, pen=10)

#     f_pen = lambda x: fpen_barrier(sim_smr,x/regularizer)

#     result = bb.search_min(f=fpen, 
#                             domain = bounds_reg.T,
#                             budget = 20,  # total number of function calls available
#                             batch = 1,  # number of calls that will be evaluated in parallel
#                             resfile = 'output.csv')  # text file where results will be savedin a single iteration.

#     pprint(result)
# elif gop_solver == 'pso':
#     # Global optimization with PSO
#     from sko.PSO import PSO

#     # f_pen = lambda x: fpen_barrier(sim_smr,x/regularizer)
#     result_pso = PSO(func= lambda x: sim_smr.fpen_barrier(x/regularizer), n_dim=sim_smr.n_dof, pop=2*sim_smr.n_dof, max_iter=40, lb=bounds_reg[0], ub=bounds_reg[1], verbose=True)
#     result_pso.record_mode = True
#     if sim_smr.n_f > 1:
#         print("Multi-objective optimization not supported (yet)")
#     elif sim_smr.n_f < 1:
#         print("Invalid number of objective functions")
#     else:
#         print("Starting global optimization")
#         result_pso.run()
#     # printing results of global optimization with Differential Evolution
#     xpso = np.array([6.17810197e-05, 2.74573937e-04, 3.91942260e-04, 3.15410796e-04,
#     2.66089439e-04, 1.96572335e+05, 4.53996283e+06, 2.45857440e+02])
#     xpso = result_pso.gbest_x/regularizer
#     print(sim_smr.calculate_optProblem(xpso))

#     # saving results of local optimization with Differential Evolution
#     sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet, sim_smr.savepath,True)

#     import matplotlib.pyplot as plt

#     print(f(result_pso.gbest_x))
#     print(g(result_pso.gbest_x))
#     sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet, sim_smr.savepath,True)
#     print(result_pso.gbest_x)
#     pprint(result_pso)

#     plt.plot(result_pso.gbest_y_hist)
#     plt.show()
# elif gop_solver == 'sbopt':
#     import sbopt

#     # f_pen = lambda x: fpen_barrier(sim_smr,x/regularizer)
#     optProb_sbo = sbopt.RbfOpt(  lambda x: sim_smr.fpen_barrier(x/regularizer, pen=10), 
#                                 bounds_reg.T,
#                                 initial_design='latin',
#                                 initial_design_ndata=20)
#     result = optProb_sbo.minimize(max_iter=100,  # maximum number of iterations
#                             # (default)
#                             n_same_best=50,  # number of iterations to run
#                             # without improving best function value (default)
#                             eps=1e-6,  # minimum distance a new design point
#                             # may be from an existing design point (default)
#                             verbose=1,  # number of iterations to go for
#                             # printing the status (default)
#                             initialize=True,  # boolean, wether or not to
#                             # perform the initial sampling (default)
#                             strategy='local_best',  # str, which minimize strategy
#                             # to use. strategy='local_best' (default) adds only
#                             # one design point per iteration, where this selection
#                             # first looks at the best local optimizer result. 
#                             # strategy='all_local' adds the results from each of
#                             # the local optima in a single iteration.
#                             )
#     print('Best design variables:', result[0])
#     print('Best function value:', result[1])
#     print('Convergence by max iteration:', result[2])
#     print('Convergence by n_same_best:', result[3])