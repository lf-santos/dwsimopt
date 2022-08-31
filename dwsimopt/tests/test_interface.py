"""Module that contains the tests for the DWSIM-Python interface

.. module:: test_interface.py
   :synopsis: Tests for the DWSIM-Python interface

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: test_interface.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np
import os
import sys
import unittest

from dwsimopt.sim_opt import SimulationOptimization
from dwsimopt.utils import PATH2DWSIMOPT

class TestDWSIM_Interface(unittest.TestCase):
    """Class that contains the tests for the DWSIM-Python interface

    Args:
        unittest (): Standard python module for unit testting code.
    """

    def test_SimOpt_instantiation(self):
        """SimulationOptimziation class instantiation test.
        """
        # Getting DWSIM path from system path
        path2dwsim = []
        for k,v in enumerate(os.environ['path'].split(';')):
            if v.find('\DWSIM')>-1:
                path2dwsim = os.path.join(v, '')
        if path2dwsim == []:
            path2dwsim = input(r"Please, input the path to your DWSIM installation, usually C:\Users\UserName\AppData\Local\DWSIM7")   #insert manuall
            if path2dwsim[-1] not in '\/':
                path2dwsim += r'/'

        # Loading DWSIM simulation into Python (Simulation object)
        ROOT_DIR = os.path.abspath(os.getcwd())
        if ROOT_DIR.find('tests')>-1:
            ROOT_DIR = '\\'.join(ROOT_DIR.split('\\')[0:-2])
        print(ROOT_DIR)
        self.sim1 = SimulationOptimization(path2sim= os.path.join(ROOT_DIR, "dwsimopt\\tests\\test_sim_heater.dwxmz"), 
                            path2dwsim = path2dwsim)
        
        self.assertIsNotNone(self.sim1)
        self.sim2 = SimulationOptimization(path2sim="wrong_simulation_name.dwxmz", 
                                                                     path2dwsim = path2dwsim)
        self.assertIsNotNone(self.sim2)
                                                                     

    def test_addRef2DWSIM(self):
        """DWSIM dlls reference adding test.
        """

        # Test import automation manager class
        self.test_SimOpt_instantiation()
        self.sim1.add_refs()
        try:
            from DWSIM.Automation import Automation2
        except ModuleNotFoundError:
            pass
        self.assertIn('DWSIM.Automation', sys.modules)

    def test_connectDWSIM_simulation(self):
        """DWSIM connection test.
        """
        # Connect simulation in sim.path2sim
        self.test_SimOpt_instantiation()
        self.sim1.add_refs()
        try:
            from DWSIM.Automation import Automation2
        except ModuleNotFoundError:
            pass
        self.assertIn('DWSIM.Automation', sys.modules)
        if ('interf' not in globals()):    # create automation manager
            global interf
            interf = Automation2()

        #Connect simulation in sim.path2sim
        sim = interf.CreateFlowsheet()

        # add water
        water = sim.AvailableCompounds["Water"]
        sim.SelectedCompounds.Add(water.Name, water)

        # create and connect objects
        from DWSIM.Interfaces.Enums.GraphicObjects import ObjectType
        from DWSIM.Thermodynamics import Streams, PropertyPackages
        from DWSIM.UnitOperations import UnitOperations
        from DWSIM.GlobalSettings import Settings

        m1 = sim.AddObject(ObjectType.MaterialStream, 50, 50, "inlet")
        m2 = sim.AddObject(ObjectType.MaterialStream, 150, 50, "outlet")
        e1 = sim.AddObject(ObjectType.EnergyStream, 100, 50, "power")
        h1 = sim.AddObject(ObjectType.Heater, 100, 50, "heater")

        sim.ConnectObjects(m1.GraphicObject, h1.GraphicObject, -1, -1)
        sim.ConnectObjects(h1.GraphicObject, m2.GraphicObject, -1, -1)
        sim.ConnectObjects(e1.GraphicObject, h1.GraphicObject, -1, -1)

        sim.AutoLayout()

        # steam tables property package
        stables = PropertyPackages.SteamTablesPropertyPackage()
        sim.AddPropertyPackage(stables)

        # set inlet stream temperature
        # default properties: T = 298.15 K, P = 101325 Pa, Mass Flow = 1 kg/s
        m1.SetTemperature(300.0) # K
        m1.SetMassFlow(100.0) # kg/s

        # set heater outlet temperature
        h1.CalcMode = UnitOperations.Heater.CalculationMode.OutletTemperature
        h1.OutletTemperature = 400 # K

        # request a calculation
        Settings.SolverMode = 0
        errors = interf.CalculateFlowsheet2(sim)
        print(f"Heater Heat Load: {h1.DeltaQ} kW")

        # save file
        interf.SaveFlowsheet(sim, self.sim1.path2sim, True)

        self.assertIsNone(self.sim1.connect(interf))
        try:
            self.sim2.connect(interf)
        except Exception as e:
            exception = e.__class__
        self.assertIsNotNone(exception)

if __name__ == '__main__':
    unittest.main()