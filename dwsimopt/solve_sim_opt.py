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
                path2dwsim = "", 
                savepath = "", 
                verbose = True, 
                force_convergence=True)  # pragma: no cover

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

            print(f'PSO finished with x* = {result_pso.gbest_x}')
            self.converge_simulation((result_pso.gbest_x))
            print(f'fobj = self.f[0]()')
            for i in range(self.n_g):
                print(f'g_{i} = {self.g[i][0]()}')

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

        if printing==True:
            import matplotlib.pyplot as plt

            print(f'GA finished with x* = {result_GA.best_x}')
            self.converge_simulation((result_GA.best_x))
            print(f'fobj = self.f[0]()')
            for i in range(self.n_g):
                print(f'g_{i} = {self.g[i][0]()}')

            plt.plot(result_GA.generation_best_Y)
            plt.show()

        return result_GA