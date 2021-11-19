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

from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
from DWSIM.Thermodynamics import Streams, PropertyPackages
from DWSIM.UnitOperations import UnitOperations
from DWSIM.Automation import Automation2
from DWSIM.GlobalSettings import Settings

from os import getcwd
pathLocal = getcwd()
Directory.SetCurrentDirectory(dwsimpath)

# create automation manager

interf = Automation2()

sim = interf.LoadFlowsheet(pathLocal + "\DWSIM_automation_MATLAB\CavettProblem.dwxml")

# use CAPE-OPEN interfaces to manipulate objects
feed = sim.GetFlowsheetSimulationObject("2")
vap_out = sim.GetFlowsheetSimulationObject("8")
liq_out = sim.GetFlowsheetSimulationObject("18")

