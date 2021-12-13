import numpy as np
import time

class SimulationOptimization():

    def __init__(self, path2sim, dof=np.array([]), path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):
        self.path = path2sim
        self.path2dwsim = path2dwsim
        self.x_val = np.array([])
        self.f_val = np.array([])
        self.g_val = np.array([])
        self.f = np.array([])
        self.n_f = self.f.size
        self.g = np.array([])
        self.n_g = self.g.size
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

    def add_fobj(self, func):
        self.f = np.append(self.f, func)
        self.n_f = self.f.size

    def add_constraint(self, g_func):
        self.g = np.append(self.g, g_func)
        self.n_g = self.g.size

    def converge_simulation(self, x):
        # print(f"opt_functions calculation at x = {x}")
        if x.size != self.n_dof:
            print(f"Size of x {x.size} is diferent from n_dof = {self.n_dof}. DO you know what your doing?")
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

    def calculate_optProblem(self, x):
        try: 
            delta_x = np.linalg.norm(self.x_val - np.asarray(x))
        except:
            delta_x = 1
        if delta_x > 1e-10:
            self.converge_simulation(x)
            self.x_val = np.array(x)
            self.f_val = np.zeros(self.f.size)
            self.g_val = np.zeros(self.g.size)
            for i in range(self.n_f):
                self.f_val[i] = self.f[i]()
            for i in range(self.n_g):
                self.g_val[i] = self.g[i]()
        print(f"f = {self.f_val}, g = {self.g_val} at x = {x}")
        return np.append(self.f_val, self.g_val)

    def fpen_barrier(self,x,pen=1000):
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*max(0, self.g_val[i])
        return fpen

    def fpen_quad(self, x, pen=1000):
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*max(0, self.g_val[i])**2
        return fpen

    def fpen_exp(self, x, pen=1000):
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*exp(max(0, self.g_val[i]))
        return fpen