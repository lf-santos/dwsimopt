"""Main module that contains OptimiSim class definition

.. module:: solve_sim_opt.py
   :synopsis: Class to solve DWSIM simulation optimization problems

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: solve_sim_opt.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np
import time
from dwsimopt.sim_opt import SimulationOptimization

class OptimiSim(SimulationOptimization):
    """Class that solves the DWSIM simulation optimization problem.

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
        :ivar init_dwsim: Boolean that controls if DWSIM is initialized automatically with `OptimiSim` class
    """
    def __init__(self, 
                path2sim, 
                path2dwsim = "", 
                savepath = "", 
                verbose = True, 
                force_convergence=True,
                init_dwsim=True):
        super().__init__(path2sim,
                path2dwsim = path2dwsim, 
                savepath = savepath, 
                verbose = verbose, 
                force_convergence=force_convergence)  # pragma: no cover

        if init_dwsim == True:
            import os
            if path2dwsim == "":
                for k,v in enumerate(os.environ['path'].split(';')):
                    if v.find('\DWSIM')>-1:
                        path2dwsim = os.path.join(v, '')
                if path2dwsim == []:
                    path2dwsim = input(r"Please, input the path to your DWSIM installation, usually C:\Users\UserName\AppData\Local\DWSIM7")   #insert manuall
                    if path2dwsim[-1] not in '\/':
                        path2dwsim += r'/'
            self.path2dwsim = path2dwsim
            self.add_refs()

            from DWSIM.Automation import Automation2

            if ('interf' not in globals()):     # create automation manager
                global interf
                interf = Automation2()
                self.interf = interf
            self.connect(interf)                # connect to simulation

    def PSO(self, x0, xlb, xub, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], verbose=True, plotting=True):
        """Runs Particle Swarm Optimization to solve the simulation optimization problem defined in the `OptimiSim`

        Args:
            x0 (numpy.array): Array of initial values for the degrees of freedom
            xlb (numpy.array): Array of lower bounds for the degrees of freedom
            xub (numpy.array): Array of upper bounds for the degrees of freedom
            pen_method (string): Penalization method ('barrier', 'quad', or 'exp')
            pen_factor (float): Penalization factor (default=1000)
            pop (int): population size (default=`2*n_dof`)
            max_ite (int): maximum number of iterations (default=`5*n_dof`)
            verbose (boolean): verbose (default=True)
            plotting(boolean): boolean for plotting or not (default=True)

        Returns:
            result_pso (sko.PSO.PSO): `sko` object with the optimization results
        """
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

        if plotting==True:
            import matplotlib.pyplot as plt

            print(f'PSO finished with x* = {result_pso.gbest_x}')
            self.converge_simulation((result_pso.gbest_x))
            print(f'fobj = {self.f[0]()}')
            for i in range(self.n_g):
                print(f'g_{i} = {self.g[i][0]()}')

            plt.plot(result_pso.gbest_y_hist)
            plt.show()

        return result_pso

    def GA(self, x0, xlb, xub, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], prob_mut=[], verbose=True, plotting=True):
        """Runs Genetic Algorithm to solve the simulation optimization problem defined in the `OptimiSim`

        Args:
            x0 (numpy.array): Array of initial values for the degrees of freedom
            xlb (numpy.array): Array of lower bounds for the degrees of freedom
            xub (numpy.array): Array of upper bounds for the degrees of freedom
            pen_method (string): Penalization method ('barrier', 'quad', or 'exp')
            pen_factor (float): Penalization factor (default=1000)
            pop (int): population size (default=`2*n_dof`)
            max_ite (int): maximum number of iterations (default=`5*n_dof`)
            prob_mut (float): probability of mutation from 0 to 1 (default=0.5)
            verbose (boolean): verbose (default=True)
            plotting(boolean): boolean for plotting or not (default=True)

        Returns:
            result_GA (sko.GA.GA): `sko` object with the optimization results
        """
        # Global optimization with GA
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
            prob_mut = 0.5
        
        result_GA = GA(func= f_pen, n_dim=self.n_dof, size_pop=pop, max_iter=max_ite, prob_mut=prob_mut, lb=xlb, ub=xub)
        result_GA.run()
        result_GA.record_mode = True
        if self.n_f > 1:
            raise Exception("Multi-objective optimization not supported (yet)")
        elif self.n_f < 1:
            raise Exception("Invalid number of objective functions")
        else:
            print("Starting global optimization")
            result_GA.run()

        if plotting==True:
            import matplotlib.pyplot as plt

            print(f'GA finished with x* = {result_GA.best_x}')
            self.converge_simulation((result_GA.best_x))
            print(f'fobj = {self.f[0]()}')
            for i in range(self.n_g):
                print(f'g_{i} = {self.g[i][0]()}')

            plt.plot(result_GA.generation_best_Y)
            plt.show()

        return result_GA

    
    def DE(self, x0, xlb, xub, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], verbose=True, plotting=True):
        """Runs Differential Evolution to solve the simulation optimization problem defined in the `OptimiSim`

        Args:
            x0 (numpy.array): Array of initial values for the degrees of freedom
            xlb (numpy.array): Array of lower bounds for the degrees of freedom
            xub (numpy.array): Array of upper bounds for the degrees of freedom
            pen_method (string): Penalization method ('barrier', 'quad', or 'exp')
            pen_factor (float): Penalization factor (default=1000)
            pop (int): population size (default=`2*n_dof`)
            max_ite (int): maximum number of iterations (default=`5*n_dof`)
            verbose (boolean): verbose (default=True)
            plotting(boolean): boolean for plotting or not (default=True)

        Returns:
            result_DE (sko.DE.DE): `sko` object with the optimization results
        """
        # Global optimization with DE
        from sko.DE import DE

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
        
        result_DE = DE(func= f_pen, n_dim=self.n_dof, size_pop=pop, max_iter=max_ite, lb=xlb, ub=xub)
        result_DE.run()
        result_DE.record_mode = True
        if self.n_f > 1:
            raise Exception("Multi-objective optimization not supported (yet)")
        elif self.n_f < 1:
            raise Exception("Invalid number of objective functions")
        else:
            print("Starting global optimization")
            result_DE.run()

        if plotting==True:
            import matplotlib.pyplot as plt

            print(f'DE finished with x* = {result_DE.best_x}')
            self.converge_simulation((result_DE.best_x))
            print(f'fobj = {self.f[0]()}')
            for i in range(self.n_g):
                print(f'g_{i} = {self.g[i][0]()}')

            plt.plot(result_DE.generation_best_Y)
            plt.show()

        return result_DE

    def AFSA(self, x0, pen_method='barrier', pen_factor=1000, pop=[], max_ite=[], verbose=True, plotting=True,
                max_try_num=100, step=0.5, visual=0.3, q=0.98, delta=0.5):
        # Global optimization with AFSA
        from sko.AFSA import AFSA

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
        
        result_AFSA = AFSA(func= f_pen, n_dim=self.n_dof, size_pop=pop, max_iter=max_ite, max_try_num=max_try_num, step=step, visual=visual, q=q, delta=delta)
        result_AFSA.record_mode = True
        result_AFSA.run()
        if self.n_f > 1:
            raise Exception("Multi-objective optimization not supported (yet)")
        elif self.n_f < 1:
            raise Exception("Invalid number of objective functions")
        else:
            print("Starting global optimization")
            result_AFSA.run()
        return result_AFSA

        # if plotting==True:
        #     import matplotlib.pyplot as plt

        #     print(f'AFSA finished with x* = {result_AFSA.best_x}')
        #     self.converge_simulation((result_AFSA.best_x))
        #     print(f'fobj = {self.f[0]()}')
        #     for i in range(self.n_g):
        #         print(f'g_{i} = {self.g[i][0]()}')

        #     plt.plot(result_AFSA.generation_best_Y)
        #     plt.show()

        # return result_AFSA