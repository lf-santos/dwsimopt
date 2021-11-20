## C#-related libraries
import pythoncom
pythoncom.CoInitialize()

import clr

from os import system as System
from System.IO import Directory, Path, File
from System import String, Environment

dwsimpath = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM6\\"

clr.AddReference(dwsimpath + "CapeOpen.dll")
clr.AddReference(dwsimpath + "DWSIM.Automation.dll")
clr.AddReference(dwsimpath + "DWSIM.Interfaces.dll")
clr.AddReference(dwsimpath + "DWSIM.GlobalSettings.dll")
clr.AddReference(dwsimpath + "DWSIM.SharedClasses.dll")
clr.AddReference(dwsimpath + "DWSIM.Thermodynamics.dll")
clr.AddReference(dwsimpath + "DWSIM.UnitOperations.dll")

clr.AddReference(dwsimpath + "DWSIM.Inspector.dll")
clr.AddReference(dwsimpath + "DWSIM.MathOps.dll")
clr.AddReference(dwsimpath + "TcpComm.dll")
clr.AddReference(dwsimpath + "Microsoft.ServiceBus.dll")

# importing DWSIM classes from clr references
from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings

from os import getcwd
pathLocal = getcwd()
Directory.SetCurrentDirectory(dwsimpath)

# math related importing
import numpy as np
import time

# create automation manager
interf = Automation2()
sim = interf.LoadFlowsheet(pathLocal + "\DWSIM_automation_Cavett\CavettProblem.dwxml")

# use CAPE-OPEN interfaces to manipulate objects
feed = sim.GetFlowsheetSimulationObject("2")
vap_out = sim.GetFlowsheetSimulationObject("8")
liq_out = sim.GetFlowsheetSimulationObject("18")

# mass flow rate values in kg/s
flows = [170.0, 180.0, 190.0, 200.0] 
flowData = np.zeros(4)

for i in range(len(flows)):
    # setting values to simulation
    feed.SetMassFlow(flows[i])
    # calculate the flowsheet (run the simulation)
    print("Running simulation with F = ", flows[i], " kg/s, please wait...")
    interf.CalculateFlowsheet2(sim)
    # time.sleep(1)
    t0 = time.time()
    while (not sim.Solved and time.time()-t0<1):
        print("Simulation status: ", sim.Solved)
        time.sleep(0.1)
    # check for errors during the last run
    if not sim.Solved:
        print("Error solving flowsheet: ", sim.ErrorMessage)
    # get vapor outlet mass flow value
    vflow = vap_out.GetMassFlow()
    # get liquid outlet mass flow value
    lflow = liq_out.GetMassFlow()
    # display results
    print("Simulation run # ",i," results:\nFeed: ", flows[i], ", Vapor: ",vflow,", Liquid: ",lflow," kg/s\nMass balance error: ", (flows[i] - vflow - lflow)," kg/s\n")

# Saving the file
# interf.SaveFlowsheet2(sim, sim.FilePath)