from pyDWSIMconnect import pyDWSIMconnect
from Simulation import Simulation
import numpy as np
import time
from fobj import *
from scipy import optimize


sim_smr = Simulation(path2sim="C:\\Users\\lfsfr\\Desktop\\pyDWSIMopt\\sim\\SMR_1exp.dwxmz")

pyDWSIMconnect(sim_smr)

x0=[0.00118444444444444, 2.3e5, 48e5]
args=(sim_smr)
xtol=0.01
ftol=0.01
maxiter=5 # +- 5 seconds per iteration
def cb(x, optRes, *args):
    global iteration, regularizer
    iteration += 1
    x = np.asarray(x)/regularizer
    sumW, mita = fobj3n(sim_smr, x)
    print(iteration, x, sumW, mita)
    # global iteration
    # iteration += 1
    # print(iteration, optRes.x, optRes.fun)

print("starting optimization")
iteration = 0
regularizer = np.array([1e3, 1e-5, 1e-6])
bounds_raw = np.array( [[0.0010, 2e5, 30e5],[0.002, 5e5, 60e5]] )
bounds_reg = regularizer*bounds_raw
bounds = optimize.Bounds(bounds_reg[0], bounds_reg[1])
g = lambda x: fobj3n(sim_smr,np.asarray(x)/regularizer)[1]
nonlinear_constraint = optimize.NonlinearConstraint(g, 3, np.inf, jac='2-point', hess=optimize.BFGS())
f = lambda x: fobj3n(sim_smr,np.asarray(x)/regularizer)[0]
result = optimize.minimize(f,np.asarray(x0)*regularizer, method='trust-constr', jac='2-point', hess=optimize.SR1(),
               constraints=[nonlinear_constraint], options={'verbose': 3, 'xtol': xtol, 'maxiter': maxiter}, 
               bounds=bounds, callback=None)
# result = optimize.minimize(f,np.asarray(x0)*regularizer, method='COBYLA', jac='2-point', hess=optimize.SR1(),
#                constraints=[nonlinear_constraint], options={'verbose': 1}, bounds=bounds, callback=cb)