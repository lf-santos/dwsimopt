
class Simulation():

    def __init__(self, path2sim, path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):
        self.path = path2sim
        self.path2dwsim = path2dwsim
        self.x = None
        self.f = None
        self.g = None
        self.fobj = None
    
    def Add_refs(self):
        import pythoncom
        pythoncom.CoInitialize()

        import clr

        from os import system as System
        from System.IO import Directory, Path, File
        from System import String, Environment

        clr.AddReference(self.path2dwsim + "CapeOpen.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Automation.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Interfaces.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.GlobalSettings.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.SharedClasses.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Thermodynamics.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.UnitOperations.dll")

        clr.AddReference(self.path2dwsim + "DWSIM.Inspector.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.MathOps.dll")
        clr.AddReference(self.path2dwsim + "TcpComm.dll")
        clr.AddReference(self.path2dwsim + "Microsoft.ServiceBus.dll")
        print("added refs")

    def Connect(self, interf):  
        import sys

        if ~hasattr(self, 'flowsheet'):
            # load simulation
            flowsheet = interf.LoadFlowsheet(self.path)

            # add DWSIM objects to Simulation object
            self.interface = interf
            self.flowsheet = flowsheet
            
            if flowsheet is not None:
                print("Simulation was loaded successfully")

class SimulationGeneric(Simulation):

    def __init__(self, path2sim, dof, path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):
        super().__init__(path2sim=path2sim,path2dwsim=path2dwsim)
        self.dof = dof
        print(hasattr(self, 'flowsheet'))
        if ~hasattr(self, 'flowsheet'):
            self.Add_refs()
            self.Connect()


