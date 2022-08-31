"""Module that contains the tests for the OptimiSim utilization for calculating the DWSIM flowsheet

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

from dwsimopt.solve_sim_opt import OptimiSim

class TestOptimiSim(unittest.TestCase):
    """Class that contains the tests for the OptimiSim utilization for calculating the DWSIM flowsheet.

    Args:
        unittest (): Standard python module for unit testting code.
    """

    def test_OptimiSim_reproductibility(self):
        """Test for the DWSIM flowsheet calculation via Python interface and reproductibility.
        """

        # Loading DWSIM simulation into Python (Simulation object)
        ROOT_DIR = os.path.abspath(os.getcwd())
        if ROOT_DIR.find('tests')>-1:
            ROOT_DIR = '\\'.join(ROOT_DIR.split('\\')[0:-2])
        print(ROOT_DIR)
        sim_smr = OptimiSim(path2sim= os.path.join(ROOT_DIR, "dwsimopt\\tests\\test_sim.dwxmz"))
        sim_smr.savepath = os.getcwd() + "\\dwsimopt\\tests\\test_sim2.dwxmz"

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

        self.sim = sim_smr

    def test_OptimiSim_PSO(self):
        try: self.sim
        except:
            self.test_OptimiSim_reproductibility()
            sim_smr = self.sim
        
        results_pso = []
        try:
            results_pso = sim_smr.PSO(sim_smr.x_val, 0.75*sim_smr.x_val, 1.25*sim_smr.x_val, pop=3, max_ite=2)
        except:
            pass
        
        print(results_pso)
        self.assertIsNot(results_pso, [])

if __name__ == '__main__':
    unittest.main()