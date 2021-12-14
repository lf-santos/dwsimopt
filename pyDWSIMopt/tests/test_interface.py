import numpy as np
import os
import sys
import unittest
# import pytest
from pyDWSIMopt.sim_opt import SimulationOptimization

class TestDWSIM_Interface(unittest.TestCase):

    def test_SimOpt_instantiation(self):
        # Loading DWSIM simulation into Python (Simulation object)
        ROOT_DIR = os.path.abspath(os.curdir + '\\..\\..')  # This is your Project Root
        self.sim1 = SimulationOptimization(dof=np.array([]), path2sim= ROOT_DIR + "\\examples\\SMR_LNG\\SMR_2exp_phaseSep_MSHE_MITApy_generic.dwxmz", 
                            path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\")
        
        self.assertIsNotNone(self.sim1)
        self.assertIsNotNone(SimulationOptimization(dof=np.array([]), path2sim="wrong_simulation_name.dwxmz", 
                                                                     path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\"))

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
        if ('interf' not in locals()):    # create automation manager
            interf = Automation2()

        # Connect simulation in sim.path2sim
        self.sim1.Connect(interf)

if __name__ == '__main__':
    unittest.main()