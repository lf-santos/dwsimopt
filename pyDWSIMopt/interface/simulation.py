
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

    def Connect(self):  
        from DWSIM.Automation import Automation2

        if hasattr(self, 'flowsheet') != True:
            # create automation manager
            interf = Automation2()

            # load simulation
            flowsheet = interf.LoadFlowsheet(self.path)

            # add DWSIM objects to Simulation object
            self.interface = interf
            self.flowsheet = flowsheet
            
            if flowsheet is not None:
                print("Simulation was loaded successfully")

