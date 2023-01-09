"""Main module that contains SimulationOptimization class definition

.. module:: sim_opt.py
   :synopsis: DWSIM simulation optimization class

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: sim_opt.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np
import time

class SimulationOptimization():
    """Class that defines DWSIM simulation optimization objects.

        :ivar path2sim: Absolute path to a DWSIM simulation (.dwxmz)
        :ivar path2dwsim: Absolute path to the DWSIM installation
        :ivar savepath: Absolute path to save the DWSIM simulation (.dwxmz)
        :ivar verbose: Boolean that controls display messages during simulation calculation
        :ivar x_val: Last simulated degrees of freedom values
        :ivar f_val: Last simulated objective functions values
        :ivar g_val: Last simulated constraints values
        :ivar dof: Lambda function that assign the degrees of freedom of the DWSIM process simulation to be handled by the optimization solver
        :ivar f: Lambda function that returns a numpy.array with objective functions values after converging the simulation
        :ivar g: Lambda function that returns a numpy.array with constraints values after converging the simulation
        :ivar n_dof: Number of degrees of freedom (size of optimization problem)
        :ivar n_f: Number of objective functions (still unsupported for n_f>1, *i.e.* multi-objective problem)
        :ivar n_g: Number of constraints
        :ivar force_convergence: Boolean that controls if multiple simulation runs is allowed. It may be usefull for simulations that include python scripts. It is not recomended for those that take a long time to converge.
    """
    def __init__(self,
                path2sim,
                path2dwsim = "",
                savepath = "",
                verbose = True,
                force_convergence=True):  # pragma: no cover
        self.path2sim = path2sim
        self.path2dwsim = path2dwsim
        if savepath=="":
            self.savepath = path2sim
        else:
            self.savepath = savepath
        self.x_val = np.array([])
        self.f_val = np.array([])
        self.g_val = np.array([])
        self.f = np.array([], dtype=object)
        self.n_f = self.f.size
        self.g = np.array([], dtype=object)
        self.n_g = self.g.size
        self.dof = np.array([], dtype=object)
        self.n_dof = self.dof.size
        self.verbose = verbose
        self.force_convergence = force_convergence


    def add_refs(self):
        """This method add reference in the proggraming environment to the DWSIM dlls, so they can be imported.
        """
        import pythoncom
        pythoncom.CoInitialize()

        import clr

        clr.AddReference(self.path2dwsim + "CapeOpen.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Automation.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Interfaces.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.GlobalSettings.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.SharedClasses.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Thermodynamics.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.UnitOperations.dll")
        clr.AddReference(self.path2dwsim + "System.Buffers.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.Inspector.dll")
        clr.AddReference(self.path2dwsim + "DWSIM.MathOps.dll")
        clr.AddReference(self.path2dwsim + "TcpComm.dll")
        clr.AddReference(self.path2dwsim + "Microsoft.ServiceBus.dll")
        clr.AddReference(self.path2dwsim + "System.Buffers.dll")
        clr.AddReference(self.path2dwsim + "SkiaSharp.dll")
        clr.AddReference(self.path2dwsim + "OxyPlot")

        print("added refs")

    def connect(self, interf):
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

    def add_dof(self, dof_new, description=[None,None,None,None]):
        """Append a new degree of freedom to the SimulationOptimization object

        Args:
            dof_new (lambda function): Lambda function that assign the appended degrees of freedom of the DWSIM process simulation
        """
        if self.dof.size==0:
            self.dof = np.append(self.dof, np.append( dof_new, description ) )
        else:
            self.dof = np.block( [ [self.dof],  [np.append( dof_new, description)] ] )
        self.n_dof += 1# int(self.dof.size)
        # self.dof.reshape((self.n_dof,2))

    def add_fobj(self, func, description=[None,None,None,None]):
        """Append a new objective function to the SimulationOptimization object

        Args:
            func (lambda function): Lambda function that returns a numpy.array with objective function value after converging the simulation
        """
        if self.f.size==0:
            self.f = np.append(self.f, np.append( func, description ) )
        else:
            self.f = np.block( [ [self.f],  [np.append( func, description)] ] )
        self.n_f += 1

    def add_constraint(self, g_func, description=[None,None,None,None]):
        """Append a new constraint to the SimulationOptimization object

        Args:
            g_func (lambda function): Lambda function that returns a numpy.array with constraint value after converging the simulation
        """
        if self.g.size==0:
            self.g = np.append(self.g, np.append( g_func, description ) )
        else:
            self.g = np.block( [ [self.g],  [np.append( g_func, description)] ] )
        self.n_g += 1

    def converge_simulation(self, x):
        """Converge the simulation with degrees of freedom values of ``x``

        Args:
            x (numpy.array): Array of degrees of freedom values to be simulated
        """
        if self.verbose:
            print(f"opt_functions calculation at x = {x}")
        if x.size != self.n_dof:
            print(f"Size of x {x.size} is diferent from n_dof = {self.n_dof}. DO you know what your doing? Only {x.size} values of dof will be assigned.")
        for i in range(self.n_dof):
            self.dof[i][0](x[i])
        # first calculation
        # self.interface.SaveFlowsheet(self.flowsheet,self.savepath,True) # -> trial savingg to debug
        error = self.interface.CalculateFlowsheet2(self.flowsheet)
        time.sleep(0.1)
        # second calculation
        if self.force_convergence:
            error = self.interface.CalculateFlowsheet2(self.flowsheet)
            time.sleep(0.1)
            res_old = np.array([self.f[0]()])
            for i in range(self.n_g):
                if self.n_g > 1:
                    res_old = np.append(res_old, np.asarray(self.g[i][0]()))
                else:
                    res_old = np.append(res_old, np.asarray(self.g[0]()))

            # third+ calculation
            for conv_ite in range(3):
                error = self.interface.CalculateFlowsheet2(self.flowsheet)
                time.sleep(0.1)
                res_new = np.array([self.f[0]()])
                for i in range(self.n_g):
                    if self.n_g > 1:
                        res_new = np.append(res_new, np.asarray(self.g[i][0]()))
                    else:
                        res_new = np.append(res_new, np.asarray(self.g[0]()))
                try:
                    variation = np.linalg.norm(res_new-res_old)
                except:
                    variation = 1
                if variation > 1e-6:
                    res_old = res_new
                else:
                    if self.verbose:
                        print(f"               Simulation converged in {conv_ite+3} iterations")
                    if len(error)>0:
                        print(f"{error} at x = {x}")
                    return

        # fifth calculation, in case of error
        if len(error)>0:
            error = self.interface.CalculateFlowsheet2(self.flowsheet)
            time.sleep(0.05)
            if self.verbose:
                print("               Simulation converged in 5 iterations or failed to converge...")

        if len(error)>0:
            print(f"{error} at x = {x}")

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
            self.f_val = np.zeros(self.n_f)
            self.g_val = np.zeros(self.n_g)
            if self.n_f>1:
                for i, ff in enumerate(self.f):
                    self.f_val[i] = ff[0]()
            elif self.n_f==0:
                self.f_val = None
            else:
                self.f_val = np.array([self.f[0]()])

            if self.n_g>1:
                for i, gg in enumerate(self.g):
                    self.g_val[i] = gg[0]()
            elif self.n_g==0:
                self.f_val = None
            else:
                self.g_val = np.array([self.g[0]()])
        if self.verbose:
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
            fpen += np.asarray(self.f_val)[i]
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

    def PSO(self, x0, xlb, xub, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], verbose=True, printing=True):
        # Global optimization with PSO
        from sko.PSO import PSO

        if pen_method=='barrier':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        elif pen_method=='quad':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        elif pen_method=='exp':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        else:
            raise Exception(f"Penalization method {pen_method} not found.")

        if pop==[]:
            pop = 2*self.n_dof
        if max_ite==[]:
            max_ite = 5*self.n_dof

        result_pso = PSO(func= f_pen, n_dim=self.n_dof, pop=pop, max_iter=max_ite, lb=xlb, ub=xub, verbose=verbose)
        result_pso.record_mode = True
        if self.n_f > 1:
            raise Exception("Multi-objective optimization not supported (yet)")
        elif self.n_f < 1:
            raise Exception("Invalid number of objective functions")
        else:
            print("Starting global optimization")
            result_pso.run()

        if printing==True:
            import matplotlib.pyplot as plt

            print(self.f[0](result_pso.gbest_x))
            for i in self.n_g:
                print(self.g[i][0](result_pso.gbest_x))
            print(result_pso.gbest_x)

            plt.plot(result_pso.gbest_y_hist)
            plt.show()

        return result_pso

    def GA(self, x0, xlb, xub, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], prob_mut=[], verbose=True, printing=True):
        # Global optimization with PSO
        from sko.GA import GA

        if pen_method=='barrier':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        elif pen_method=='quad':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        elif pen_method=='exp':
            f_pen = lambda x: self.fpen_barrier(x, pen=pen_factor)
        else:
            raise Exception(f"Penalization method {pen_method} not found.")

        if pop==[]:
            pop = 2*self.n_dof
        if max_ite==[]:
            max_ite = 5*self.n_dof
        if prob_mut==[]:
            prob_mut = 1

        result_GA = GA(func= f_pen, n_dim=self.n_dof, pop=pop, max_iter=max_ite, prob_mut=prob_mut, lb=xlb, ub=xub, verbose=verbose)
        result_GA.record_mode = True
        if self.n_f > 1:
            raise Exception("Multi-objective optimization not supported (yet)")
        elif self.n_f < 1:
            raise Exception("Invalid number of objective functions")
        else:
            print("Starting global optimization")
            result_GA.run()

        if printing==True:
            import matplotlib.pyplot as plt

            print(self.f[0](result_GA.gbest_x))
            for i in self.n_g:
                print(self.g[i][0](result_GA.gbest_x))
            print(result_GA.gbest_x)

            plt.plot(result_GA.gbest_y_hist)
            plt.show()

        return result_GA