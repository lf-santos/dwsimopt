import time
import numpy as np

def fobj_smr(sim_smr, x, dtmin=3):
    mr1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
    comp1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-1") 
    comp2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-2") 
    comp3 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-3") 
    comp4 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4") 
    pump1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("PUMP-01") 
    pump2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("PUMP-02") 
    vlv1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("VALV-01")
    cool8 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-08")
    lng = sim_smr.flowsheet.GetFlowsheetSimulationObject("LNG-1")
    ps1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc")
    ps2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc")
    if sim_smr.x is None:
        sim_smr.x = np.zeros(len(x))
    if np.linalg.norm(sim_smr.x - np.asarray(x))>1e-10:
        sep1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("SEP-02")
        sep2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("SEP-03")
        sep1.GraphicObject.Active = False
        sep2.GraphicObject.Active = False
        ps1.GraphicObject.Active = False
        ps2.GraphicObject.Active = False

        mr1.SetOverallCompoundMassFlow(0,x[1])
        mr1.SetOverallCompoundMassFlow(1,x[2])
        mr1.SetOverallCompoundMassFlow(2,x[3])
        mr1.SetOverallCompoundMassFlow(5,x[4])
        mr1.SetOverallCompoundMassFlow(7,x[0])
        vlv1.OutletPressure = x[5]
        comp4.POut = x[6]
        cool8.OutletTemperature = x[7]

        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction == 0:
            pump1.GraphicObject.Active = False
            sim_smr.flowsheet.DisconnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-29").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject)
        else:
            pump1.GraphicObject.Active = True
            sim_smr.flowsheet.DisconnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-29").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject)     #avoid bug
            sim_smr.flowsheet.ConnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-29").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject,-1,-1)
        sep1.GraphicObject.Active = True
        sep1.Calculate()
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction == 0:
            pump2.GraphicObject.Active = False
            sim_smr.flowsheet.DisconnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-30").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject)
        else:
            pump2.GraphicObject.Active = True
            sim_smr.flowsheet.DisconnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-30").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject)
            sim_smr.flowsheet.ConnectObjects(
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-30").GraphicObject,
                sim_smr.flowsheet.GetFlowsheetSimulationObject("MIX-02").GraphicObject,-1,-1)
        sep2.GraphicObject.Active = True
        sep2.Calculate()
        ps1.GraphicObject.Active = True
        ps2.GraphicObject.Active = True
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        # ps1.Calculate()
        # ps2.Calculate()
        # while ps1.Calculated is not True or ps2.Calculated is not True:
        #     time.sleep(0.1)
        #     print("MITA calculation failed in x=")
        #     print(x)
        # print(comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'])
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'])
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        # print(comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'])
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'])
        error = sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        if bool(error):
            print(f"{error[0]} at x = {x}")
        # print(comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'])
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'])
        # sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        # print(comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita'])
        # print(sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita'])
        sumW = (comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction > 1e-5:
            sumW += pump1.DeltaQ 
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction > 1e-5:    
            sumW += pump2.DeltaQ
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").Phases[1].Properties.massfraction == 0:    
            sumW += 1e10
        sumW = sumW/lng.GetMassFlow()/3600
        mita1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita']
        mita2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita']
    else:
        sumW = sim_smr.f
        mita1 = dtmin - sim_smr.g
        mita2 = dtmin - sim_smr.g
    sim_smr.x = x
    sim_smr.f = sumW
    sim_smr.g = dtmin-min(mita1, mita2)
    return sumW, (dtmin-min(mita1, mita2))

def fobj_smr_generic(sim, x):
    for i in range(sim.n_dof):
        sim.dof[i](x[i])
    # source = sim.flowsheet.Scripts.Values.Where(lambda x: x.Title == 'fobj_calc').FirstOrDefault().ScriptText.replace('\r', '')
    # exec(source)
    import time
    while sim.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").GraphicObject.Calculated == False or sim.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").GraphicObject.Calculated == False:
        time.sleep(0.1)
    sumW = (sim.flowsheet.GetFlowsheetSimulationObject("COMP-1") .DeltaQ 
            + sim.flowsheet.GetFlowsheetSimulationObject("COMP-2") .DeltaQ 
            + sim.flowsheet.GetFlowsheetSimulationObject("COMP-3") .DeltaQ 
            + sim.flowsheet.GetFlowsheetSimulationObject("COMP-4") .DeltaQ)
    if sim.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction > 1e-5:
        sumW += sim.flowsheet.GetFlowsheetSimulationObject("PUMP-01") .DeltaQ 
    if sim.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction > 1e-5:    
        sumW += sim.flowsheet.GetFlowsheetSimulationObject("PUMP-02") .DeltaQ
    mita1 = sim.flowsheet.GetFlowsheetSimulationObject("MITA1-Calc").OutputVariables['mita']
    mita2 = sim.flowsheet.GetFlowsheetSimulationObject("MITA2-Calc").OutputVariables['mita']
    sim.x = x
    sim.f = sumW
    sim.g = 3-min(mita1, mita2)
    return sumW, (3-min(mita1, mita2))
