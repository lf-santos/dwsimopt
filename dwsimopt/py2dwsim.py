"""Module that contains functions for data exchange from-to python to-from dwsim

.. module:: py2dwsim.py
   :synopsis: Data exchange from python to dwsim

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: py2dwsim.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np

def create_pddx(desc, sim, element="dof", assign=True):
    """Main function from py2dwsim.py that creates a python-dwsim data exchange channel.
    It can return a np.array of getter or setter functions from/to the dwsim simulation.
    The default is to assing the data exchange hub to the SimulationOptimization object passed to this function.

    Args:
        desc (list): list of string containing ['dwsim object name as in the simulation', 'object attribute','phase or component name', 'unit']
        sim (dwsimopt.SimulationOpimization): object of dwsimopt.SimulationOpimization
        element (str, optional): optimization problem element: 'dof', 'fobj', or 'constraint'. Defaults to "dof".
        assign (bool, optional): if True: assign the python-dwsim data exchange channel to the corresponding `element` in `sim`, else: return lambda function. Defaults to True.

    Returns:
        numpy.array: np.array of getter or setter functions from/to the dwsim simulation if `assign==False`
    """
    #assign python-dwsim data exchange channel
    m = np.shape(desc)

    # Test if input has length 3
    if m[-1] < 2:
        print("desc list must be [object name (str), object property (str), compound or mixture (str), unit (str)='']")

    # Get only the number of inputs to be assigned to dwsim
    if len(m)<=1:
        m=1
    else:
        m = m[0]

    # If multiple Inputs:
    ff = []
    for ite in range(m):
         # Get what element is added do sim object
        if element=="dof":
            elem_add = sim.add_dof
            elem = sim.dof
            elem_n = sim.n_dof
        elif element=="fobj":
            elem_add = sim.add_fobj
            elem = sim.f
            elem_n = sim.n_f
        elif element=="constraint":
            elem_add = sim.add_constraint
            elem = sim.g
            elem_n = sim.n_g
        else:
            print(f"There is no such element in {sim} object")

        # Get current input in case of multiple ones
        if m>1:
            desc_ite = desc[ite]
        else:
            desc_ite = desc
        
        # Get function `f` that communicates with dwsim
        if element=="dof":
            f = _toDwsim(desc_ite, sim)
        else:
            f = _fromDwsim(desc_ite, sim)

        ff.append(f)
    if assign==True:
        assign_pddx(ff, desc, sim, element)
    else:
        return ff

def assign_pddx(f, desc, sim, element="dof"):
    """Assign pddx to `sim` object. This is useful for more complex objective/constaint functions. Basic use is to generate pddx getter functions to define a more complicated one and assign to `sim`.

    Args:
        f (function): function (def or lambda) containing the definition of objective/constraint function.
        desc (list): list of string containing ['dwsim object name as in the simulation', 'object attribute','phase or component name', 'unit']
        sim (dwsimopt.SimulationOpimization): object of dwsimopt.SimulationOpimization
        element (str, optional): optimization problem element: 'dof', 'fobj', or 'constraint'. Defaults to "dof".
    """
    #assign python-dwsim data exchange channel
    m = np.size(f)
    
    # If multiple Inputs:
    for ite in range(m):
         # Get what element is added do sim object
        if element=="dof":
            elem_add = sim.add_dof
            elem = sim.dof
            elem_n = sim.n_dof
        elif element=="fobj":
            elem_add = sim.add_fobj
            elem = sim.f
            elem_n = sim.n_f
        elif element=="constraint":
            elem_add = sim.add_constraint
            elem = sim.g
            elem_n = sim.n_g
        else:
            print(f"There is no such element in {sim} object")

        # Has this element already added? Disregard repetitive element
        if elem == np.array([]):
            elem_add( f, desc )
        else:
            addQuery = True
            if elem_n == 1:
                rows = elem[1:len(desc)]
                if np.all( np.array(desc[:len(desc)-1], dtype=object) == rows ):
                    addQuery = False
            else:
                for row in elem:
                    rows = row[1:len(desc)]
                    if np.all( np.array(desc[:len(desc)-1], dtype=object) == rows ):
                        addQuery = False
            if addQuery:
                elem_add( f, desc )

def _toDwsim(desc, sim):
    """Helper function that define a setter function to the dwsim object described in `desc` in `sim`.

    Args:
        desc (list): list of string containing ['dwsim object name as in the simulation', 'object attribute','phase or component name', 'unit'].
        sim (dwsimopt.SimulationOpimization): object of dwsimopt.SimulationOpimization.

    Returns:
        function: setter function to dwsim object described in `desc` in `sim`.
    """
    from DWSIM.SharedClasses.SystemsOfUnits import Converter

    # is input[0] in sim?
    try:
        obj = sim.flowsheet.GetFlowsheetSimulationObject(desc[0])
        # print(obj.GetDisplayName())
    except:
        print(f"there is no {desc[0]} in {sim}")
        return

    name = obj.GetType().FullName.split('.')
    # print(name)

    # Dealing with material stream DoF:
    if name[-1] == 'MaterialStream':
        if desc[1] == 'MassFlow':
            f = lambda x: obj.SetMassFlow( str(x) + f" {desc[3]}" )
        elif desc[1] == 'Temperature':
            f = lambda x: obj.SetTemperature( str(x) + f" {desc[3]}" )
        elif desc[1] == 'Pressure':
            f = lambda x: obj.SetPressure( str(x) + f" {desc[3]}" )
        elif desc[1] == 'MolarFlow':
            f = lambda x: obj.SetMolarFlow( str(x) + f" {desc[3]}" )
        elif desc[1] == 'CompoundMassFlow':
            # def f(x):
            #     return obj.SetOverallCompoundMassFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
            f = lambda x: obj.SetOverallCompoundMassFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        elif desc[1] == 'CompoundMolarFlow':
            f = lambda x: obj.SetOverallCompoundMolarFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        elif desc[1] == 'CompoundMolarComposition':
            f = lambda x: obj.SetOverallCompoundMassFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        else:
            print(f"No property of {desc[0]} named {desc[1]}")
            f = None
    # Dealing with energy stram DoF:
    elif name[-1] == 'EnergyStream':
        if desc[1] == 'EnergyFlow':
            f = lambda x: _set_property( str(x) + f" {desc[3]}", obj.EnergyFlow )
        else:
            print(f"No property of {desc[0]} named {desc[1]}")
            f = None
    # Dealing with Unit Operations:
    elif name[-2] == 'UnitOperations':
        # calcMode = obj.CalcMode
        if desc[1] == 'OutletPressure':
            if name[-1]=='Compressor':
                f = lambda x: _set_property( str(x) + f" {desc[3]}", obj.POut )
            else:
                f = lambda x: _set_property( str(x) + f" {desc[3]}", obj.OutletPressure )
        elif desc[1] == 'OutletTemperature':
            f = lambda x: _set_property( str(x) + f" {desc[3]}", obj.OutletTemperature )
        else:
            f=None
    else:
        f = None

    return f
    
def _fromDwsim(desc, sim):
    """Helper function that define a getter function to the dwsim object described in `desc` in `sim`.

    Args:
        desc (list): list of string containing ['dwsim object name as in the simulation', 'object attribute','phase or component name', 'unit'].
        sim (dwsimopt.SimulationOpimization): object of dwsimopt.SimulationOpimization.

    Returns:
        function: getter function to dwsim object described in `desc` in `sim`.
    """
    from DWSIM.SharedClasses.SystemsOfUnits import Converter

    # is input[0] in sim?
    try:
        obj = sim.flowsheet.GetFlowsheetSimulationObject(desc[0])
        # print(obj.GetDisplayName())
    except:
        print(f"there is no {desc[0]} in {sim}")
        return

    name = obj.GetType().FullName.split('.')
    # print(name)

    # Dealing with material stream DoF:
    if name[-1] == 'MaterialStream':
        if desc[1] == 'MassFlow':
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.GetMassFlow()) 
        elif desc[1] == 'Temperature':
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.GetTemperature())
        elif desc[1] == 'Pressure':
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.GetPressure()) 
        elif desc[1] == 'MolarFlow':
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.GetMolarFlow()) 
        # elif desc[1] == 'CompoundMassFlow':
        #     f = lambda x: obj.SetOverallCompoundMassFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        # elif desc[1] == 'CompoundMolarFlow':
        #     f = lambda x: obj.SetOverallCompoundMolarFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        # elif desc[1] == 'CompoundMolarComposition':
        #     f = lambda x: obj.SetOverallCompoundMassFlow( desc[2], Converter.ConvertToSI(desc[3], x) )
        else:
            print(f"No property of {desc[0]} named {desc[1]}")
            f = None
    # Dealing with energy stram DoF:
    elif name[-1] == 'EnergyStream':
        if desc[1] == 'EnergyFlow':
            # def f(x):
            #     return Converter.ConvertFromSI( f"{desc[3]}", obj.EnergyFlow) 
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.EnergyFlow) 
        else:
            print(f"No property of {desc[0]} named {desc[1]}")
            f = None
    # Dealing with Unit Operations:
    elif name[-2] == 'UnitOperations':
        # calcMode = obj.CalcMode
        if desc[1] == 'OutletPressure':
            if name[-1]=='Compressor':
                f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.POut) 
            else:
                f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.OutletPressure) 
        elif desc[1] == 'OutletTemperature':
            f = lambda: Converter.ConvertFromSI( f"{desc[3]}", obj.OutletTemperature)
        elif desc[1] == 'OutputVariable':
            # def f(x):
            #     return obj.OutputVariables[desc[2]]
            f = lambda: obj.OutputVariables[desc[2]]
        else:
            f=None
    else:
        f = None

    return f

def _set_property(x, obj):
    """Helper setter function. obj <- x

    Args:
        x (Float): value to be set to obj property
        obj (Object property): object property to recieve x value
    """
    obj = x