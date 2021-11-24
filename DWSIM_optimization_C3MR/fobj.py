def fobj(sim_smr,x=0.00118444444444444):
    mr1 = sim_smr.flowsheet.GetFlowsheetSimulationObject("MR-1")
    mr1.flowsheet.SetMassFlow(x)
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