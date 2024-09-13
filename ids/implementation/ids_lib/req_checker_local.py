import asyncio
import numpy as np 
import local_req_strategy
class ReqCheckerLocal:

    def __init__(self, rtu_config, data_ref, violations_queue, logger, case):
        self.LocalReqConfiguration = LocalReqConfiguration()
        
        if(case == "SST"): 
            saftey_threshold_C = local_req_strategy.Saftey_Threshold_C(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_C)
            
            saftey_threshold_v = local_req_strategy.Saftey_Threshold_V(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_v)
            
            sst_v_4 = local_req_strategy.SST_V_4(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(sst_v_4)
            
            sst_v_3 = local_req_strategy.SST_V_3(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(sst_v_3)
            
        
        if (case == "Coteq"):  
            saftey_threshold_C = local_req_strategy.Saftey_Threshold_C(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_C)
            
            saftey_threshold_v = local_req_strategy.Saftey_Threshold_V(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(saftey_threshold_v)
            
            solar_plant_sanity = local_req_strategy.Solar_Plant_Sanity(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(solar_plant_sanity)
            
            transformer_threshold = local_req_strategy.Transformer_Saftey_Threshold_Current(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check*transformer_threshold
            
            transformer_border = local_req_strategy.Transformer_Border_Values(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(transformer_border)
            
            thd_threshold = local_req_strategy.THD_Threshold(self, rtu_config, data_ref, violations_queue, logger, case)
            self.LocalReqConfiguration.add_check(thd_threshold)
            
    
    async def check_requirements(self):
        self.LocalReqConfiguration.run_checks()

# helper class 
# that allows to store requirement configurations and to execute all the checks in an configuration 
class LocalReqConfiguration: 
    def __init__(self):
        self.checks = []
    
    def add_check(self, check_strategy):
        self.checks.append(check_strategy)
        
    def run_checks(self, data):
        for check_strategy in self.checks:
            check_strategy.check(data)
           
 
      

