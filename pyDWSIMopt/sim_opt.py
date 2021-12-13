import numpy as np

class SimulationOptimization():

    def __init__(self, path2sim, dof=np.array([]), path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):
        self.path = path2sim
        self.path2dwsim = path2dwsim
        self.x = None
        self.f = None
        self.g = None
        self.fobj = []
        self.n_fobj = self.fobj.size
        self.constraints = []
        self.n_constraints = self.constraints.size
        self.dof = dof
        self.n_dof = self.dof.size
    
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
        clr.AddReference(self.path2dwsim + "System.Buffers.dll")
        clr.AddReference(self.path2dwsim + "SkiaSharp.dll")
        
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

    def add_dof(self, dof_new):
        self.dof = np.append(self.dof, dof_new)
        self.n_dof = self.dof.size

    def add_fobj(self, f):
        self.fobj = np.append(self.fobj, f)
        self.n_fobj = self.fobj.size

    def add_constraint(self, g):
        self.constraints = np.append(self.constraints, g)
        self.n_constraints = self.constraints.size

    def converge_simulation(self, x):
        print(f"opt_functions calculation at x = {x}")
        for i in range(self.n_dof):
            self.dof[i](x[i])
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.05)
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.05)
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.05)
        if bool(error):
            print(f"{error[0]} at x = {x}")

    def fpen_barrier(sim,x):
        f, g = sim.fobj(x)
        return f + 1000*max(0,g)

    def fpen_quad(sim, x):
        f, g = sim.fobj(x)
        return f + 1000*max(0,g)**2

    def fpen_exp(sim, x):
        f, g = sim.fobj(x)
        return f + 1000*exp(max(0,g))