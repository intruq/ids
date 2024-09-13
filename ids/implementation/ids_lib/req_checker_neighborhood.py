import asyncio
import json
import pandapower as pp
import time
import math
import neighbourhood_req_strategy

import numpy as np 

class ReqCheckerNeighborhood:

    def __init__(self, border_regions, client_lms, vio_queue, logger, case ):
        self.NeighbourhoodReqConfiguration = NeighbourhoodReqConfiguration()
        
        if(case == "SST"): 
            sst_voltage_drop = neighbourhood_req_strategy.SST_Voltage_Drop(self, border_regions, client_lms, vio_queue, logger, case)
            self.NeighbourhoodReqConfiguration.add_check(sst_voltage_drop)
            
            sst_i_7_8 = neighbourhood_req_strategy.SST_I_7_8(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_7_8)
            
            sst_i_1 = neighbourhood_req_strategy.SST_I_1(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_1)
            
            sst_v_1 = neighbourhood_req_strategy.SST_V_1(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_v_1)
            
            sst_i_4 = neighbourhood_req_strategy.SST_I_4(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_4)
            
            sst_v_3_l = neighbourhood_req_strategy.SST_V_3_L(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_v_3_l)
            
            sst_v_6 = neighbourhood_req_strategy.SST_V_6(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(sst_v_6)
            
        
        if(case == "Coteq"):
            transformer_switch = neighbourhood_req_strategy.Transformer_Switch_History(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(transformer_switch)
            
            transformer_coil = neighbourhood_req_strategy.Transformer_Coil_Proportion(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add(transformer_coil)
            
            coteq_pf = neighbourhood_req_strategy.Coteq_Powerflow(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(coteq_pf)
            
            two_sides = neighbourhood_req_strategy.Values_Both_Cable_Sides(self, border_regions, client_lms, vio_queue, logger, case )
            self.NeighbourhoodReqConfiguration.add_check(two_sides)

    async def check_requirements(self):
        self.NeighbourhoodReqConfiguration.run_checks()
    

# helper class 
# that allows to store requirement configurations and to execute all the checks in an configuration 
class NeighbourhoodReqConfiguration: 
    def __init__(self):
        self.checks = []
    
    def add_check(self, check_strategy):
        self.checks.append(check_strategy)
        
    def run_checks(self, data):
        for check_strategy in self.checks:
            check_strategy.check(data)
           