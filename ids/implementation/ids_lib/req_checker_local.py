import asyncio
import numpy as np 
from .local_req_strategy import *
class ReqCheckerLocal:

    def __init__(self, rtu_config, data_ref, violations_queue, logger, case):
        self.LocalReqConfiguration = LocalReqConfiguration()
        
        if(case == "SST"): 
            saftey_threshold_C = Saftey_Threshold_C(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_C)
            
            saftey_threshold_v = LocalRequirementCheckStrategy.Saftey_Threshold_V(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_v)
            
            sst_v_4 = LocalRequirementCheckStrategy.SST_V_4(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(sst_v_4)
            
            sst_v_3 = LocalRequirementCheckStrategy.SST_V_3(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(sst_v_3)
            
        
        if (case == "Coteq"):  
            saftey_threshold_C = Saftey_Threshold_C(rtu_config, data_ref, violations_queue, logger)
            self.LocalReqConfiguration.add_check(saftey_threshold_C)
            
            saftey_threshold_v = Saftey_Threshold_V(rtu_config, data_ref, violations_queue, logger)
            self.LocalReqConfiguration.add_check(saftey_threshold_v)
            
            solar_plant_sanity = Solar_Plant_Sanity(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(solar_plant_sanity)
            
            transformer_threshold = Transformer_Saftey_Threshold_Current(rtu_config, data_ref, violations_queue, logger)
           # self.LocalReqConfiguration.add_check(transformer_threshold)
            
            transformer_border = Transformer_Border_Values(rtu_config, data_ref, violations_queue, logger)
           # self.LocalReqConfiguration.add_check(transformer_border)
            
            thd_threshold = THD_Threshold(rtu_config, data_ref, violations_queue, logger)
           # self.LocalReqConfiguration.add_check(thd_threshold)

        if (case == "demkit"):
            #demkit_test_case = Demkit_Test_Case_3(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_test_case)

            #demkit_case_1 = DEMKit_S1_Household_Grid_Balance(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_1)

            #demkit_case_2 = DEMKit_S2_Saftey_Threshold_C(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_2)

            #demkit_case_3 = DEMKit_S3_Battery_Overcharge(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_3)

            demkit_case_4 = DEMKit_S4_Feedin_Only_Generators(rtu_config, data_ref, violations_queue, logger)
            self.LocalReqConfiguration.add_check(demkit_case_4)

            #demkit_case_5 = DEMKit_S5_Battery_Discharge(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_5)

            #demkit_case_6 = DEMKit_S6_Isolated_Power_Activity(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_6)

            #demkit_case_7 = DEMKit_S7(rtu_config, data_ref, violations_queue, logger)
            #self.LocalReqConfiguration.add_check(demkit_case_7)
            
    
    async def check_requirements(self):
        await self.LocalReqConfiguration.run_checks()

# helper class 
# that allows to store requirement configurations and to execute all the checks in an configuration 
class LocalReqConfiguration: 
    def __init__(self):
        self.checks = []
    
    def add_check(self, check_strategy):
        self.checks.append(check_strategy)
        
    async def run_checks(self):
        for check_strategy in self.checks:
            await check_strategy.check()
           
 
      

