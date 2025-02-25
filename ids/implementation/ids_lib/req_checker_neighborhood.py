import asyncio
import json
import pandapower as pp
import time
import math
from .neighbourhood_req_strategy import *

import numpy as np 

class ReqCheckerNeighborhood:

    def __init__(self, border_regions, client_lms, vio_queue, logger, case ):
        self.NeighbourhoodReqConfiguration = NeighbourhoodReqConfiguration()
        
        if(case == "SST"): 
            sst_voltage_drop = SST_Voltage_Drop( border_regions, client_lms, vio_queue, logger)
            self.NeighbourhoodReqConfiguration.add_check(sst_voltage_drop)
            
            sst_i_7_8 = SST_I_7_8(border_regions, client_lms, vio_queue, logger )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_7_8)
            
            sst_i_1 = SST_I_1( border_regions, client_lms, vio_queue, logger )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_1)
            
            sst_v_1 = SST_V_1( border_regions, client_lms, vio_queue, logger)
            self.NeighbourhoodReqConfiguration.add_check(sst_v_1)
            
            sst_i_4 = SST_I_4( border_regions, client_lms, vio_queue, logger )
            self.NeighbourhoodReqConfiguration.add_check(sst_i_4)
            
            sst_v_3_l = SST_V_3_L(border_regions, client_lms, vio_queue, logger )
            self.NeighbourhoodReqConfiguration.add_check(sst_v_3_l)
            
            sst_v_6 = SST_V_6( border_regions, client_lms, vio_queue, logger)
            self.NeighbourhoodReqConfiguration.add_check(sst_v_6)
            
     
        if(case == "Coteq"):
            transformer_switch = Transformer_Switch_History( border_regions, client_lms, vio_queue, logger )
           # self.NeighbourhoodReqConfiguration.add_check(transformer_switch)
            
            transformer_coil = Transformer_Coil_Proportion( border_regions, client_lms, vio_queue, logger )
           # self.NeighbourhoodReqConfiguration.add_check(transformer_coil)
            
            coteq_pf =Coteq_Powerflow( border_regions, client_lms, vio_queue, logger )
          #  self.NeighbourhoodReqConfiguration.add_check(coteq_pf)
            
            two_sides = Values_Both_Cable_Sides(border_regions, client_lms, vio_queue, logger )
           # self.NeighbourhoodReqConfiguration.add_check(two_sides)

        if (case == "demkit"):
            print("Hello nm")

    async def check_requirements(self, client_address_list):
        await self.NeighbourhoodReqConfiguration.run_checks()
    

# helper class 
# that allows to store requirement configurations and to execute all the checks in an configuration 
class NeighbourhoodReqConfiguration: 
    def __init__(self):
        self.checks = []
    
    def add_check(self, check_strategy):
        self.checks.append(check_strategy)
        
    async def run_checks(self):
        for check_strategy in self.checks:
            await check_strategy.check()
           