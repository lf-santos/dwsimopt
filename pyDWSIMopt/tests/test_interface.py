import numpy as np
import os
import sys
import unittest

from pyDWSIMopt.sim_opt import SimulationOptimization

class TestDWSIM_Interface(unittest.TestCase):

    def test_SimOpt_instantiation(self):
        # Getting DWSIM path from system path
        for k,v in enumerate(os.environ['path'].split(';')):
            if v.find('\DWSIM')>-1:
                path2dwsim = os.path.join(v, '')
        if path2dwsim == None:
            path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"

        # Loading DWSIM simulation into Python (Simulation object)
        try:
            ROOT_DIR = os.path.dirname(__file__) # This is your Project Root
        except:
            ROOT_DIR = os.path.abspath(os.getcwd())
        if ROOT_DIR.find('tests')>-1:
            ROOT_DIR = '\\'.join(ROOT_DIR.split('\\')[0:-2])
        print(ROOT_DIR)

        self.sim1 = SimulationOptimization(dof=np.array([]), path2sim= os.path.join(ROOT_DIR, "examples\\SMR_LNG\\SMR.dwxmz"), 
                            path2dwsim = path2dwsim)
        
        self.assertIsNotNone(self.sim1)
        self.sim2 = SimulationOptimization(dof=np.array([]), path2sim="wrong_simulation_name.dwxmz", 
                                                                     path2dwsim = path2dwsim)
        self.assertIsNotNone(self.sim2)
                                                                     

    def test_addRef2DWSIM(self):

        # Test import automation manager class
        self.test_SimOpt_instantiation()
        self.sim1.Add_refs()
        try:
            from DWSIM.Automation import Automation2
        except ModuleNotFoundError:
            pass
        self.assertIn('DWSIM.Automation', sys.modules)

    def test_connectDWSIM_simulation(self):
        # Connect simulation in sim.path2sim
        self.test_SimOpt_instantiation()
        self.sim1.Add_refs()
        try:
            from DWSIM.Automation import Automation2
        except ModuleNotFoundError:
            pass
        self.assertIn('DWSIM.Automation', sys.modules)
        if ('interf' not in globals()):    # create automation manager
            global interf
            interf = Automation2()

        #Connect simulation in sim.path2sim
        self.assertIsNone(self.sim1.Connect(interf))
        try:
            self.sim2.Connect(interf)
        except Exception as e:
            exception = e.__class__
        self.assertIsNotNone(exception)

if __name__ == '__main__':
    unittest.main()