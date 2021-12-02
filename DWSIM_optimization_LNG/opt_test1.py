from pyDWSIMconnect import PyDWSIMconnect
from simulation import Simulation
import numpy as np
import time
from fobj import *
from scipy import optimize


sim_smr = Simulation(path2sim="C:\\Users\\lfsfr\\Desktop\\pyDWSIMopt\\sim\\SMR_1exp.dwxmz")

PyDWSIMconnect(sim_smr)

x0=[0.00118444444444444, 2.3e5, 48e5]
args=(sim_smr,fobj3n)
xtol=0.0001
ftol=0.0001
maxiter=300 # +- 5 seconds per iteration
def cb(x):
    global iteration
    iteration += 1
    sumW, mita = fobj3n(sim_smr, x)
    print(iteration, x, sumW, mita)

print("starting optimization")
iteration = 0
result = optimize.fmin(fpen,x0,args,xtol,ftol,maxiter,full_output=True, disp=True, retall=True, callback=cb)
