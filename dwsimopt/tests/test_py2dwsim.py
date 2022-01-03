"""Module that contains the tests for the python-dwsim data exchange interface in py2dwsim.py

.. module:: tests_py2dwisim.py
   :synopsis: Tests for the Python-DWSIM data exchange interface

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: tests_py2dwisim.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import sys
import os
import numpy as np
import unittest

from dwsimopt.sim_opt import SimulationOptimization
from dwsimopt.utils import PATH2DWSIMOPT

class TestSimOpt(unittest.TestCase):
    """Class that contains the tests for the Python-DWSIM data exchange interface

    Args:
        unittest (): Standard python module for unit testting code.
    """

    def test_SimOpt_py2dwsim(self):
        """Test for the DWSIM flowsheet calculation via Python interface and reproductibility using py2dwsim interface.
        """
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
        sim_smr = SimulationOptimization(dof=np.array([]), path2sim= os.path.join(ROOT_DIR, "dwsimopt\\tests\\test_sim.dwxmz"), 
                            path2dwsim = path2dwsim)
        sim_smr.savepath = os.getcwd() + "\\dwsimopt\\tests\\test_sim2.dwxmz"
        sim_smr.add_refs()

        # Instanciate automation manager object
        from DWSIM.Automation import Automation2

        if ('interf' not in locals()):    # create automation manager
            interf = Automation2()

        # Connect simulation in sim.path2sim
        sim_smr.connect(interf)

        from dwsimopt import py2dwsim

        # Assign DoF:
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Nitrogen", "kg/s"],    sim_smr, element="dof" )
        self.assertEqual(sim_smr.n_dof, 1)
        self.assertEqual(sim_smr.dof.size, 5)
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Methane", "kg/s"],     sim_smr, element="dof" )
        ndof_old = sim_smr.n_dof
        self.assertEqual(sim_smr.n_dof,2)
        # repeting dof 1
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Nitrogen", "kg/s"],    sim_smr, element="dof" )
        self.assertEqual(sim_smr.n_dof, ndof_old)
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Ethane", "kg/s"],      sim_smr, element="dof" )
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Propane", "kg/s"],     sim_smr, element="dof" )
        py2dwsim.create_pddx( ["MR-1", "CompoundMassFlow", "Isopentane", "Pa"],    sim_smr, element="dof" )
        py2dwsim.create_pddx( ["VALV-01", "OutletPressure", "Mixture", "Pa"],      sim_smr, element="dof" )
        py2dwsim.create_pddx( ["COMP-1", "OutletPressure", "Mixture", "Pa"],       sim_smr, element="dof" )
        py2dwsim.create_pddx( ["COOL-08", "OutletTemperature", "Mixture", "K"],    sim_smr, element="dof" )

        # Assign F
        py2dwsim.create_pddx( ["Sum_W", "EnergyFlow", "Mixture", "kW"], sim_smr, element="fobj" )
        self.assertEqual(sim_smr.n_f, 1)

        # adding constraints (g_i <= 0):
        g1 = py2dwsim.create_pddx( ["MITA1-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint", assign=False )
        py2dwsim.assign_pddx( lambda: 3-g1[0]() , ["MITA1-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint" )
        g2 = py2dwsim.create_pddx( ["MITA2-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint", assign=False )
        py2dwsim.assign_pddx( lambda: 3-g2[0]() , ["MITA2-Calc", "OutputVariable", "mita", "°C"], sim_smr, element="constraint" )
        self.assertEqual(sim_smr.n_g,2)
        print(sim_smr.g.size)
        self.assertEqual(sim_smr.g.size,10)


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