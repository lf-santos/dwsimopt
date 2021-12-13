import pythoncom
pythoncom.CoInitialize()

import clr

from os import system as System
from System.IO import Directory, Path, File
from System import String, Environment

path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"

clr.AddReference(path2dwsim + "CapeOpen.dll")
clr.AddReference(path2dwsim + "DWSIM.Automation.dll")
clr.AddReference(path2dwsim + "DWSIM.Interfaces.dll")
clr.AddReference(path2dwsim + "DWSIM.GlobalSettings.dll")
clr.AddReference(path2dwsim + "DWSIM.SharedClasses.dll")
clr.AddReference(path2dwsim + "DWSIM.Thermodynamics.dll")
clr.AddReference(path2dwsim + "DWSIM.UnitOperations.dll")

clr.AddReference(path2dwsim + "DWSIM.Inspector.dll")
clr.AddReference(path2dwsim + "DWSIM.MathOps.dll")
clr.AddReference(path2dwsim + "TcpComm.dll")
clr.AddReference(path2dwsim + "Microsoft.ServiceBus.dll")
clr.AddReference(path2dwsim + "System.Buffers.dll")
clr.AddReference(path2dwsim + "SkiaSharp.dll")
clr.AddReference(path2dwsim + "OxyPlot.dll")
clr.AddReference(path2dwsim + "OxyPlot.GtkSharp.dll")
clr.AddReference(path2dwsim + "OpenTK.dll")
clr.AddReference(path2dwsim + "OpenTK.GLControl.dll")

path2sim = "C:\\Users\\lfsfr\\Desktop\\pyDWSIMopt\\examples\\SMR_LNG\\SMR_2exp_phaseSep_MSHE_MITApy_generic.dwxmz"

from DWSIM.Automation import Automation2
interf = Automation2() # create automation manager

# load simulation
flowsheet = interf.LoadFlowsheet(path2sim)