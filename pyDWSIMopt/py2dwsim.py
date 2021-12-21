"""Module that contains functions of data exchange from python to dwsim

.. module:: py2dwsim.py
   :synopsis: Data exchange from python to dwsim

.. moduleauthor:: Lucas F. Santos <lfs.francisco.95@gmail.com>

:Module: py2dwsim.py
:Author: Lucas F. Santos <lfs.francisco.95@gmail.com>

"""
import numpy as np
from DWSIM.SharedClasses.SystemsOfUnits import Converter

def set_property(x, obj):
    obj = x

def assign_pddx(desc, sim, element="dof"):
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
            f = toDwsim(desc_ite, sim)
        else:
            f = fromDwsim(desc_ite, sim)
        
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

def assignDoF(input, sim):
    m = np.shape(input)

    # Test if input has length 3
    if m[-1] < 2:
        print("Input list must be [object name (str), object property (str), compound or mixture (str), unit (str)='']")

    # Get only the number of inputs to be assigned to dwsim
    if len(m)<=1:
        m=1
    else:
        m = m[0]

    # If multiple Inputs:
    for ite in range(m):
        if m>1:
            input_ite = input[ite]
        else:
            input_ite = input
        
        # Get function `f` that communicates with dwsim
        f = toDwsim(input_ite, sim)

        # Has this DoF already added? Disregard repetitive DoF
        if sim.dof == np.array([]):
            sim.add_dof( f, input )
        else:
            addQuery = True
            if sim.n_dof == 1:
                rows = sim.dof[1:len(input)]
                if np.all( np.array(input[:len(input)-1], dtype=object) == rows ):
                    addQuery = False
            else:
                for row in sim.dof:
                    rows = row[1:len(input)]
                    if np.all( np.array(input[:len(input)-1], dtype=object) == rows ):
                        addQuery = False
            if addQuery:
                sim.add_dof( f, input )

def assignF(input, sim):
    m = np.shape(input)

    # Test if input has length 3
    if m[-1] < 2:
        print("Input list must be [object name (str), object property (str), compound or mixture (str), unit (str)='']")

    # Get only the number of inputs to be assigned to dwsim
    if len(m)<=1:
        m=1
    else:
        m = m[0]

    # If multiple Inputs:
    for ite in range(m):
        if m>1:
            input_ite = input[ite]
        else:
            input_ite = input
        
        # Get function `f` that communicates with dwsim
        f = toDwsim(input_ite, sim)

        # Has this DoF already added? Disregard repetitive DoF
        if sim.f == np.array([]):
            sim.add_fobj( f, input )
        else:
            addQuery = True
            if sim.n_f == 1:
                rows = sim.f[1:len(input)]
                if np.all( np.array(input[:len(input)-1], dtype=object) == rows ):
                    addQuery = False
            else:
                for row in sim.f:
                    rows = row[1:len(input)]
                    if np.all( np.array(input[:len(input)-1], dtype=object) == rows ):
                        addQuery = False
            if addQuery:
                sim.add_fobj( f, input )

def toDwsim(desc, sim):
    # is input[0] in sim?
    try:
        obj = sim.flowsheet.GetFlowsheetSimulationObject(desc[0])
        print(obj.GetDisplayName())
    except:
        print(f"there is no {desc[0]} in {sim}")
        return

    name = obj.GetType().FullName.split('.')
    print(name)

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
            f = lambda x: set_property( str(x) + f" {desc[3]}", obj.EnergyFlow )
        else:
            print(f"No property of {desc[0]} named {desc[1]}")
            f = None
    # Dealing with Unit Operations:
    elif name[-2] == 'UnitOperations':
        # calcMode = obj.CalcMode
        if desc[1] == 'OutletPressure':
            if name[-1]=='Compressor':
                f = lambda x: set_property( str(x) + f" {desc[3]}", obj.POut )
            else:
                f = lambda x: set_property( str(x) + f" {desc[3]}", obj.OutletPressure )
        elif desc[1] == 'OutletTemperature':
            f = lambda x: set_property( str(x) + f" {desc[3]}", obj.OutletTemperature )
        else:
            f=None
    else:
        f = None

    return f
    
def fromDwsim(desc, sim):
    # is input[0] in sim?
    try:
        obj = sim.flowsheet.GetFlowsheetSimulationObject(desc[0])
        print(obj.GetDisplayName())
    except:
        print(f"there is no {desc[0]} in {sim}")
        return

    name = obj.GetType().FullName.split('.')
    print(name)

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
            f = lambda: obj.OutputVariables[desc[2]]
        else:
            f=None
    else:
        f = None

    return f

if __name__ == "__main__":
    assign2dwsim( [["oi", "mundo", 10],
                    ["tchau", "mundo", -1]], None )
    sim = None
    assign2dwsim( ["oi", "mundo", 10], sim )