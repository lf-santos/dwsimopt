"""Main module that contains SimulationOptimization class definition

.. module:: sim_opt
   :synopsis: DWSIM simulation optimization class

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: sim_opt
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np
import time

class SimulationOptimization():
    """Class that defines DWSIM simulation optimization objects.

        :ivar path2sim: Absolute path to a DWSIM simulation (.dwxmz)
        :ivar path2dwsim: Absolute path to the DWSIM installation
        :ivar x_val: Last simulated degrees of freedom values
        :ivar f_val: Last simulated objective functions values
        :ivar g_val: Last simulated constraints values
        :ivar dof: Lambda function that assign the degrees of freedom of the DWSIM process simulation to be handled by the optimization solver
        :ivar f: Lambda function that returns a numpy.array with objective functions values after converging the simulation
        :ivar g: Lambda function that returns a numpy.array with constraints values after converging the simulation
        :ivar n_dof: Number of degrees of freedom (size of optimization problem)
        :ivar n_f: Number of objective functions (still unsupported for n_f>1, *i.e.* multi-objective problem)
        :ivar n_g: Number of constraints
    """
    def __init__(self, path2sim, dof=np.array([]), path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"):  # pragma: no cover
        self.path2sim = path2sim
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
        """This method add reference in the proggraming environment to the DWSIM dlls, so they can be imported.
        """
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
        """This method uses the automation manager object to load the DWSIM flowsheet and store them into self.

        Args:
            interf (DWSIM.Automation.Automation2): Automation manager object with methods to load, save, and create DWSIM flowsheet simulations.
        """
        import sys

        if ~hasattr(self, 'flowsheet'):
            # load simulation
            flowsheet = interf.LoadFlowsheet(self.path2sim)

            # add DWSIM objects to Simulation object
            self.interface = interf
            self.flowsheet = flowsheet
            
            if flowsheet is not None:
                print("Simulation was loaded successfully")

    def add_dof(self, dof_new):
        """Append a new degree of freedom to the SimulationOptimization object

        Args:
            dof_new (lambda function): Lambda function that assign the appended degrees of freedom of the DWSIM process simulation
        """
        self.dof = np.append(self.dof, dof_new)
        self.n_dof = self.dof.size

    def add_fobj(self, func):
        """Append a new objective function to the SimulationOptimization object

        Args:
            func (lambda function): Lambda function that returns a numpy.array with objective function value after converging the simulation
        """
        self.f = np.append(self.f, func)
        self.n_f = self.f.size

    def add_constraint(self, g_func):
        """Append a new constraint to the SimulationOptimization object

        Args:
            g_func (lambda function): Lambda function that returns a numpy.array with constraint value after converging the simulation
        """
        self.g = np.append(self.g, g_func)
        self.n_g = self.g.size

    def converge_simulation(self, x):
        """Converge the simulation with degrees of freedom values of ``x``

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated
        """
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
        """Assign degrees of freedom values to the simulation if norm > 1e-10. Converge the simulation and return an array with objectives and constraints values.

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated

        Returns:
            numpy.array: Array of objectives and constraints values calculated at ``x``
        """
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
        """Calculates a penalized objective function using barrier method and considering ``f`` and ``g``.

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated.
            pen (float, optional): Penalization parameter. Defaults to 1000.

        Returns:
            float: Penalized objective function.
        """
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*max(0, self.g_val[i])
        return fpen

    def fpen_quad(self, x, pen=1000):
        """Calculates a penalized objective function using quadratic penalization method and considering ``f`` and ``g``.

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated.
            pen (float, optional): Penalization parameter. Defaults to 1000.

        Returns:
            float: Penalized objective function.
        """
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*max(0, self.g_val[i])**2
        return fpen

    def fpen_exp(self, x, pen=1000):
        """Calculates a penalized objective function using exponential penalization method and considering ``f`` and ``g``.

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated.
            pen (float, optional): Penalization parameter. Defaults to 1000.

        Returns:
            float: Penalized objective function.
        """
        self.calculate_optProblem(x)
        fpen = 0
        for i in range(self.n_f):
            fpen += self.f_val[i]
        for i in range(self.n_g):
            fpen += pen*exp(max(0, self.g_val[i]))
        return fpen