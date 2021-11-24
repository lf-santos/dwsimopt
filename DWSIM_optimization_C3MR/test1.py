from pyDWSIMconnect import pyDWSIMconnect
from Simulation import Simulation
import numpy as np
import time
from fobj import fobj

# def main():

sim_smr = Simulation(path2sim="C:\\Users\\lfsfr\\Desktop\\pyDWSIMopt\\sim\\SMR_1exp.dwxmz")

pyDWSIMconnect(sim_smr)

sim_smr.decision_variables = [
    ("MR-1", "Nitrogen-MassFlow", "kg/h"),
    ("MR-1", "Methane-MassFlow", "kg/h"),
    ("MR-1", "Ethane-MassFlow", "kg/h"),
    ("MR-1", "Propane-MassFlow", "kg/h"),
    ("VALV-01", "Outlet Pressure", "bar"),
    ("MR-1", "Pressure", "bar"),
]

sumW, mita = fobj(sim_smr)
print(sumW, mita)

mr1_flow = np.linspace(0.8*0.00118444444444444, 1.5*0.00118444444444444, num=8)

for i in mr1_flow:
    # setting values to simulation
    # calculate the flowsheet (run the simulation)
    print("Running simulation with m_MR = ", i, " kg/s, please wait...")
    sumW, mita = fobj(sim_smr,i)
    errors = sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
    # time.sleep(1)
    t0 = time.time()
    while (not sim_smr.flowsheet.Solved and time.time()-t0<1):
        print("Simulation status: ", sim_smr.flowsheet.Solved)
        time.sleep(0.1)
    # check for errors during the last run
    if not sim_smr.flowsheet.Solved:
        print("Error solving flowsheet: ", sim_smr.flowsheet.ErrorMessage)
    # display results
    print("For m_MR = ",i," results:\nsum(W): ", sumW, " kW, MITA: ",mita," °C\n")





# if __name__ == "__main__":
#     main()