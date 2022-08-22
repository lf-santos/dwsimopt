"""Module that contains the tests for the SimulationOptimization utilization for calculating the DWSIM flowsheet

.. module:: tests_sim_opt.py
   :synopsis: Tests for the DWSIM flowsheet calculation via Python interface

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: tests_sim_opt.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import sys
import os
import numpy as np
import unittest

from dwsimopt.sim_opt import SimulationOptimization
from dwsimopt.utils import PATH2DWSIMOPT

class TestSimOpt(unittest.TestCase):
    """Class that contains the tests for the SimulationOptimization utilization for calculating the DWSIM flowsheet.

    Args:
        unittest (): Standard python module for unit testting code.
    """

    def test_SimOpt_reproductibility(self):
        """Test for the DWSIM flowsheet calculation via Python interface and reproductibility.
        """
        # Getting DWSIM path from system path
        for k,v in enumerate(os.environ['path'].split(';')):
            if v.find('\DWSIM')>-1:
                path2dwsim = os.path.join(v, '')
        if path2dwsim == None:
            path2dwsim = input(r"Please, input the path to your DWSIM installation, usually C:\Users\UserName\AppData\Local\DWSIM7")   #insert manuall
            if path2dwsim[-1] not in '\/':
                path2dwsim += r'/'

        # Loading DWSIM simulation into Python (Simulation object)
        ROOT_DIR = os.path.abspath(os.getcwd())
        if ROOT_DIR.find('tests')>-1:
            ROOT_DIR = '\\'.join(ROOT_DIR.split('\\')[0:-2])
        print(ROOT_DIR)
        sim_smr = SimulationOptimization(dof=np.array([]), path2sim= os.path.join(ROOT_DIR, "dwsimopt\\tests\\test_sim.dwxmz"), 
                            path2dwsim = path2dwsim)
        sim_smr.savepath = os.getcwd() + "\\dwsimopt\\tests\\test_sim2.dwxmz"
        sim_smr.add_refs()

        # Instanciate automation manager object
        from DWSIM.Automation import Automation2

        # print('=========================================================LOCALS============================================')
        # print(locals())
        # print('=========================================================GLOBALS============================================')
        # print(globals())
        if ('interf' not in locals()):    # create automation manager
            interf = Automation2()
        # else:
        #     interf = locals()['Automation2']
        # print('=========================================================Interf============================================')
        # print(dir(interf))

        # Connect simulation in sim.path2sim
        sim_smr.connect(interf)

        # Add dof
        sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(7,x))
        sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(0,x))
        sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(1,x))
        sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(2,x))
        sim_smr.add_dof(lambda x: sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1").SetOverallCompoundMassFlow(5,x))
        def set_property(x, obj):
            obj = x
        sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("VALV-01").OutletPressure) )
        sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4").POut) )
        sim_smr.add_dof( lambda x: set_property(x, sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-08").OutletTemperature) )
        # adding objective function (f_i):
        sim_smr.add_fobj(lambda : sim_smr.flowsheet.GetFlowsheetSimulationObject("Sum_W").EnergyFlow)
        # adding constraints (g_i <= 0):
        sim_smr.add_constraint(np.array([lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita']]))
        sim_smr.add_constraint(np.array([lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita']]))
        sim_smr.add_constraint(np.array([lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction]))
        sim_smr.add_constraint(np.array([lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction]))
        
        # Initial simulation optimization setup
        # Initial guess of optimization
        x0 = np.array( [0.25/3600, 0.70/3600, 1.0/3600, 1.10/3600, 1.80/3600, 2.50e5, 50.00e5, -60+273.15] )

        # Testing for simulation at x0
        f = sim_smr.calculate_optProblem(1.0*x0)
        f2 = sim_smr.calculate_optProblem(1.1*x0)
        f3 = sim_smr.calculate_optProblem(1.0*x0)

        self.assertNotEqual(sum((f-f2)**2), 0)
        np.testing.assert_array_almost_equal(f, f3)


if __name__ == '__main__':
    unittest.main()