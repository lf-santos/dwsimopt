import numpy as np
import os
import sys
import unittest
from pyDWSIMopt.sim_opt import SimulationOptimization

class TestSimOpt(unittest.TestCase):

    def test_SimOpt_reproductibility(self):
        # Loading DWSIM simulation into Python (Simulation object)
        ROOT_DIR = os.path.dirname(__file__) + '\\..\\..' # This is your Project Root
        sim_smr = SimulationOptimization(dof=np.array([]), path2sim= ROOT_DIR + "\\examples\\SMR_LNG\\SMR_2exp_phaseSep_MSHE_MITApy_generic.dwxmz", 
                            path2dwsim = "C:\\Users\\lfsfr\\AppData\\Local\\DWSIM7\\")
        sim_smr.savepath = os.getcwd() + "\\examples\\SMR_LNG\\SMR_2exp_phaseSep_MSHE_MITApy_generic2.dwxmz"
        sim_smr.Add_refs()

        # Instanciate automation manager object
        from DWSIM.Automation import Automation2
        if ('interf' not in locals()):    # create automation manager
            interf = Automation2()

        # Connect simulation in sim.path2sim
        sim_smr.Connect(interf)

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
        sim_smr.add_constraint(np.array([
            lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'],
            lambda : 3 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'],
            lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction, # no phase separation in the cycle
            lambda : 10*sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction, # no phase separation in the cycle
            #   lambda : 10*(1 - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").Phases[1].Properties.massfraction), # phase separation before MSHE
        ]))
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