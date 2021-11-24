"""Creates references to the DWSIM dlls
~
Args:
    dwsimpath (str, optional): path to DWSIM installation folder. Defaults to "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM6\\".
"""
import pythoncom
pythoncom.CoInitialize()

import clr

from os import system as System
from System.IO import Directory, Path, File
from System import String, Environment

def pyDWSIMrefs(dwsimpath = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):
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