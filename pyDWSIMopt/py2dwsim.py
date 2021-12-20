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

def assignDoF(input, sim):
    m = np.shape(input)

    # Test if input has length 3
    if m[-1] < 2:
        print("Input list must be [object name (str), object property (str), unit (str)='']")

    # Get only the number o inputs to be assigned to dwsim
    if len(m)<=1:
        m=1
    else:
        m = m[0]

    for ite in range(m):
        if m>1:
            disp = input[ite]
        else:
            disp = input
        f = toDwsim(disp, sim)

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

def toDwsim(input, sim):
    # is input[0] in sim?
    try:
        obj = sim.flowsheet.GetFlowsheetSimulationObject(input[0])
        print(obj.GetDisplayName())
    except:
        print(f"there is no {input[0]} in {sim}")
        return

    name = obj.GetType().FullName.split('.')
    print(name)

    # Dealing with material stream DoF:
    if name[-1] == 'MaterialStream':
        if input[1] == 'MassFlow':
            f = lambda x: obj.SetMassFlow( str(x) + f" {input[3]}" )
        elif input[1] == 'Temperature':
            f = lambda x: obj.SetTemperature( str(x) + f" {input[3]}" )
        elif input[1] == 'Pressure':
            f = lambda x: obj.SetPressure( str(x) + f" {input[3]}" )
        elif input[1] == 'MolarFlow':
            f = lambda x: obj.SetMolarFlow( str(x) + f" {input[3]}" )
        elif input[1] == 'CompoundMassFlow':
            f = lambda x: obj.SetOverallCompoundMassFlow( input[2], Converter.ConvertToSI(input[3], x) )
        elif input[1] == 'CompoundMolarFlow':
            f = lambda x: obj.SetOverallCompoundMolarFlow( input[2], Converter.ConvertToSI(input[3], x) )
        elif input[1] == 'CompoundMolarComposition':
            f = lambda x: obj.SetOverallCompoundMassFlow( input[2], Converter.ConvertToSI(input[3], x) )
        else:
            print(f"No property of {input[0]} named {input[1]}")
            f = None
    # Dealing with energy stram DoF:
    elif name[-1] == 'EnergyStream':
        if input[1] == 'EnergyFlow':
            f = lambda x: set_property( str(x) + f" {input[3]}", obj.EnergyFlow )
        else:
            print(f"No property of {input[0]} named {input[1]}")
            f = None
    elif name[-2] == 'UnitOperations':
        calcMode = obj.CalcMode
        if input[1] == 'OutletPressure':
            if name[-1]=='Compressor':
                f = lambda x: set_property( str(x) + f" {input[3]}", obj.POut )
            else:
                f = lambda x: set_property( str(x) + f" {input[3]}", obj.OutletPressure )
        elif input[1] == 'OutletTemperature':
            f = lambda x: set_property( str(x) + f" {input[3]}", obj.OutletTemperature )
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