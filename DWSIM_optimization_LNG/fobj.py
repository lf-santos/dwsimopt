import time
import numpy as np

def fobj(sim_smr,x=0.00118444444444444):
    mr1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
    mr1.SetMassFlow(x)
    comp1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-1") 
    comp2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-2") 
    comp3 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-3") 
    comp4 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4") 
    #for i in mr1.ComponentIds:
        #print(i)

    sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)

    sumW = comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ

    mita = min(sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(), 
        sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-1").GetTemperature()   - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(),
        sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-12").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature(),
        sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-3").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature()
    )

    return sumW, mita

def fobj3n(sim_smr, x):
    mr1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
    comp1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-1") 
    comp2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-2") 
    comp3 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-3") 
    comp4 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4") 
    vlv1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("VALV-01")
    if ( abs(mr1.GetMassFlow() - x[0])/abs(x[0]) + abs(vlv1.OutletPressure - x[1])/abs(x[1]) + abs(comp4.POut - x[2])/abs(x[2]) ) > 1e-12:
        # print("calculated with ")
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
        mr1.SetMassFlow(x[0])
        vlv1.OutletPressure = x[1]
        comp4.POut = x[2]
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
    # else:
        # print("skipped with")
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
    sumW = comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ
    mita = min(sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(), 
        sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-1").GetTemperature()   - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(),
        sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-12").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature(),
        sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-3").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature()
    )
    # sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet,sim_smr.path,True)
    return sumW, mita

def fobj8n(sim_smr, x):
    mr1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
    comp1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-1") 
    comp2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-2") 
    comp3 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-3") 
    comp4 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COMP-4") 
    vlv1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("VALV-01")
    cool8 = sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-08")
    if np.linalg.norm(sim_smr.x-x)>1e-10:
    # if ( abs(mr1.GetMassFlow() - x[0])/abs(x[0]) + abs(vlv1.OutletPressure - x[1])/abs(x[1]) + abs(comp4.POut - x[2])/abs(x[2]) ) > 1e-12:
        print("calculated with ")
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
        # mr1.SetMassFlow(x[0])
        mr1.SetOverallCompoundMassFlow(0,x[1])
        mr1.SetOverallCompoundMassFlow(1,x[2])
        mr1.SetOverallCompoundMassFlow(2,x[3])
        mr1.SetOverallCompoundMassFlow(5,x[4])
        mr1.SetOverallCompoundMassFlow(7,x[0])
        vlv1.OutletPressure = x[5]
        comp4.POut = x[6]
        cool8.OutletTemperature = x[7]
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        sumW = comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ
        mita = min(sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-07").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(), 
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-1").GetTemperature()   - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-12").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-3").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature()
        )
    else:
        print("skipped with")
        sumW = sim_smr.f
        mita = sim_smr.g
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
    
    # sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet,sim_smr.path,True)
    sim_smr.x = x
    sim_smr.f = sumW
    sim_smr.g = mita
    return sumW, mita

def fobj8n_2exp(sim_smr, x):
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
    if sim_smr.x is None:
        sim_smr.x = np.zeros(len(x))
    if np.linalg.norm(sim_smr.x - np.asarray(x))>1e-10:
    # m_old = np.ones(mr1.Phases[0].Compounds.Values.Count)
    # ite=0
    # for m_i in mr1.Phases[0].Compounds.Values:
    #     m_old[ite] = m_i.MassFraction*mr1.GetMassFlow()
    #     ite+=1
    # x_old = np.array( [m_old[7],m_old[0],m_old[1],m_old[2],m_old[5], vlv1.OutletPressure, comp4.POut, cool8.OutletTemperature] ) 
    # if np.linalg.norm( x-x_old ) > 1e-5:
    # if ( abs(mr1.GetMassFlow() - x[0])/abs(x[0]) + abs(vlv1.OutletPressure - x[1])/abs(x[1]) + abs(comp4.POut - x[2])/abs(x[2]) ) > 1e-12:
        # print("calculated with ")
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
        # mr1.SetMassFlow(x[0])
        sep1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("SEP-02")
        sep2 = sim_smr.flowsheet.GetFlowsheetSimulationObject("SEP-03")
        # sep1.Calculated = False
        # sep2.Calculated = False
        mr1.SetOverallCompoundMassFlow(0,x[1])
        mr1.SetOverallCompoundMassFlow(1,x[2])
        mr1.SetOverallCompoundMassFlow(2,x[3])
        mr1.SetOverallCompoundMassFlow(5,x[4])
        mr1.SetOverallCompoundMassFlow(7,x[0])
        vlv1.OutletPressure = x[5]
        comp4.POut = x[6]
        cool8.OutletTemperature = x[7]
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        # if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction < 1e-5:
        #     pump1.Calculated = False
        #     pump1.Uncalcu
        # else:
        #     pump1.Calculated = True
        # sep1.Calculated = True
        # sep1.Calculate()
        # sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        # if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction < 1e-5:
        #     pump2.Calculated = False
        # else:
        #     pump2.Calculated = True
        # sep2.Calculated = True
        # sep2.Calculate()
        #force to calculate spec2 spec3 cool6 e cool5
        sim_smr.flowsheet.GetFlowsheetSimulationObject("SPEC-02").Solve()
        sim_smr.flowsheet.GetFlowsheetSimulationObject("SPEC-03").Solve()
        sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-06").Solve()
        sim_smr.flowsheet.GetFlowsheetSimulationObject("COOL-05").Solve()
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        time.sleep(0.05)
        sim_smr.interface.CalculateFlowsheet2(sim_smr.flowsheet)
        sumW = (comp1.DeltaQ + comp2.DeltaQ + comp3.DeltaQ + comp4.DeltaQ)
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-03").Phases[1].Properties.massfraction > 1e-5:
            sumW += pump1.DeltaQ 
        if sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-05").Phases[1].Properties.massfraction > 1e-5:    
            sumW += pump2.DeltaQ
        sumW = sumW/lng.GetMassFlow()/3600
        mita1 = min(sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-08").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-09").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(), 
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-1_2").GetTemperature()   - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-17").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-10").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-15").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-11").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-15").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-2").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-15").GetTemperature()
        )
        mita2 = min(sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-10").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-16").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-2").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-16").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-12").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature(),
            sim_smr.flowsheet.GetFlowsheetSimulationObject("NG-3").GetTemperature() - sim_smr.flowsheet.GetFlowsheetSimulationObject("MSTR-13").GetTemperature()
        )
    else:
        sumW = sim_smr.f
        mita1 = sim_smr.g
        mita2 = sim_smr.g
        # print("skipped with")
        # print( abs(mr1.GetMassFlow() - x[0])/abs(x[0]))
        # print(abs(vlv1.OutletPressure - x[1])/abs(x[1]))
        # print(abs(comp4.POut - x[2])/abs(x[2]) )
    # if np.linalg.norm( x-x_old ) > 1e-5:
    #     sim_smr.interface.SaveFlowsheet(sim_smr.flowsheet,sim_smr.path,True)
    sim_smr.x = x
    sim_smr.f = sumW
    sim_smr.g = min(mita1, mita2)
    return sumW, min(mita1, mita2)

def fpen(x,sim,fobj):
    f, g = fobj(sim,x)
    return f + 1000*max(0,3-g)