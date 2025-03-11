from abc import ABC, abstractmethod
import asyncio
import json
import pandapower as pp
import time
import math

import numpy as np 

# Strategy class from which all single requirements will inherit, to make this easily extendible 
class NeighbourhoodRequirementCheckStrategy(ABC):

    def __init__(self, border_regions, client_lms, vio_queue, logger):
        self.__br = border_regions
        self.client_lms = client_lms
        self.__vio_queue = vio_queue
        self.logger = logger
        self.__transformer_pos = -1
        
    @abstractmethod
    def check(self): 
        pass 
    
    # helper functions to get data
    async def get_data_from_lm(self, i_of_lm):
        """Get the latest data values from the specified local monitor."""
        data_node = None                  
        data_node = self.client_lms[i_of_lm]["data_node"]
        try:
            lm_data = await data_node.read_value()
        except Exception:
           lm_data = None
        
        big_data = []
        
        for meter in lm_data.__getattribute__("meters"):
            meterdata = meter 
    
            current = meterdata.__getattribute__("current")
            voltage = meterdata.__getattribute__("voltage")
            sensor_id = meterdata.__getattribute__("id")
            
            data = []
            data.append(sensor_id)
            data.append(current)
            data.append(voltage)
            
        
            big_data.append(data)
            
        return big_data
    
    async def get_data_from_sensor(self, name_of_sensor): 
        data_lm1 = await self.get_data_from_lm(0)
        data_lm2 = await self.get_data_from_lm(1)
        data_lm3 = await self.get_data_from_lm(2)
        data_lm4 = await self.get_data_from_lm(3)
        
        sensor_data = []
        
        for d in data_lm1: 
            if d[0] == name_of_sensor: 
                sensor_data = d
        
        for d in data_lm2: 
            if d[0] == name_of_sensor: 
               sensor_data = d

        for d in data_lm3: 
            if d[0] == name_of_sensor: 
               sensor_data = d

        for d in data_lm4: 
            if d[0] == name_of_sensor: 
               sensor_data = d
        
        return sensor_data
    
    async def get_v_data_from_sensor(self, name_of_sensor): 
        sensor_data = await self.get_data_from_sensor(name_of_sensor)
        if sensor_data:
           return sensor_data[2]
        else: 
            return []
    
    async def get_c_data_from_sensor(self, name_of_sensor): 
   
        sensor_data = await self.get_data_from_sensor(name_of_sensor)
        if sensor_data:
            return sensor_data[1]
        else: 
            return []
        
    async def get_lm_sm_data(self):
        data = []
        for i in range(3):
            sensors = await self.get_data_from_lm(i)
            for m in sensors: 
                if m[0] == "sensor_21": 
                    data.append(m)
        
        return data
        
             
# REQ Coteq case     
# compare values from both sides of the connecting cable between M1 and M2 
# will only work well once replay problem is fixed
class Values_Both_Cable_Sides(NeighbourhoodRequirementCheckStrategy):
    async def check(self): 
        
        v_1 = await self.get_c_data_from_sensor("sensor_213")
        v_2 = await self.get_c_data_from_sensor("sensor_114")
        
        if v_1 and v_2:
            diff = abs(v_1-v_2)
        
            if diff > 2: 
                print("Something strange going on between M1 and M2.")
        
            elif diff > 1: 
                print("Potentially something strange going on between M1 and M2.")
                   
# REQ Coteq case 
# Power Flow solving between both MV stations 
class Coteq_Powerflow(NeighbourhoodRequirementCheckStrategy):
    async def check(self): 
        
        # todo load the respective data for V & i 
        some_data = await self.get_c_data_from_sensor("sensor_212")
        
        # todo calculate P/Q and guess theta  
        # theta = 1 means that we have only P and very little (none) Q
        # P = V * I * cos(1)
        # Q = V * I * sind(0)
        
        if some_data: 
            # taken from PowerTech Implementation
            # create empty net
            net = pp.create_empty_network()

            # needs to be calculated from our cable data 
            typ1 = {"r_ohm_per_km": 0.2179914802981896, "x_ohm_per_km": 0.0835516506922258,
                    "c_nf_per_km": 0.3386900958466454, "max_i_ka": 100}
            
            pp.create_std_type(net, name="verenas_cable_type", data=typ1, element="line")

            # create buses
            # vn_kv = The grid voltage level.
            b1 = pp.create_bus(net, vn_kv=1.5, name="MV 1")
            b2 = pp.create_bus(net, vn_kv=1.5, name="MV 2")

            # create bus elements
            
            # MV 1
            # vm_pu voltage at the slack node in per unit, default 1
            # voltage = ... 
            pp.create_ext_grid(
                net, bus=b1, vm_pu=some_data, name="Grid Connection")

            # MV 2
            # calculated as above:  
            # p_mw (float, default 0) - The active power of the load
            # - postive value   -> load
            # - negative value  -> generation
            #  q_mvar (float, default 0) - The reactive power of the load
            pp.create_load(net, bus=b2, p_mw=some_data, q_mvar=some_data, name="Load")

            # create branch elements
            pp.create_line(net, from_bus=b1, to_bus=b2, length_km=0.939,
                        name="Line", std_type="verenas_cable_type")

            # Solve the model
            start_time = time.time()
            pp.runpp(net)
            elapsed_time = time.time() - start_time
            print("Elapsed time: {}".format(elapsed_time))

            # sanitizing the results for checking later
            san_model = {}

            for i in (n+1 for n in range(2)):
                san_model[i] = {"V": net.res_bus["vm_pu"][i-1], "Theta": net.res_bus["va_degree"]
                                [i-1], "P":  net.res_bus["p_mw"][i-1], "Q": net.res_bus["q_mvar"][i-1]}

            print("Solved model is:")
            print(san_model)

# REQ Coteq case 
# proporition of coils needs to be stable 
# v_mv / v_lv = I_lv/I_mv 
    # todo get the correct sensor names
class Transformer_Coil_Proportion(NeighbourhoodRequirementCheckStrategy):
    async def check(self): 
        c_mv = await self.get_c_data_from_sensor("sensor_212")
        
        if c_mv: 
            c_1 = await self.get_c_data_from_sensor("sensor_35") 
            c_2 = await self.get_c_data_from_sensor("sensor_36") 
            c_3 = await self.get_c_data_from_sensor("sensor_37")  
        
            if c_1: 
                c_lv = math.sqrt((c_1**2 + c_2**2 + c_3**2) / 3)

        v_mv = await self.get_v_data_from_sensor("sensor_212")
        
        if v_mv: 
            v_1 = await self.get_v_data_from_sensor("sensor_35") 
            v_2 = await self.get_v_data_from_sensor("sensor_36") 
            v_3 = await self.get_v_data_from_sensor("sensor_37")  
        
            if v_1:
                v_lv = math.sqrt((v_1**2 + v_2**2 + v_3**2) / 3)
                
        coils_c = c_mv /  c_lv
        coils_v = v_mv / v_lv
        
        diff = (coils_c/coils_v)
        
        if(diff > 1.2 or diff < 0.8): # todo decide for meaningful delta 
            print(diff)
            print("Something strange going on at the transformer - ratio is off .")


# REQ Coteq case 
# check in which state we currently are and if that is desired 
# maybe also save history of states to see how they changed in the latest past 
# right now history for one time step implemented, need to see in reality if this is too harsh or possible 
class Transformer_Switch_History(NeighbourhoodRequirementCheckStrategy): 
    async def check(self): 
        s = [11250,11000,10750,10500,10250] # possible positions for input MV 
        
        v_mv = await self.get_v_data_from_sensor("sensor_212")
        
        current_pos = -1 
        for i in s: 
            tolerance = 0.1 * float(s[i])
            if(s[i] - tolerance <= v_mv <= s[i] + tolerance):
                current_pos = i 
        
        if (current_pos == -1):
            print("No matching transoformer position")
            
        if(self.__transformer_pos!=-1):
            delta = abs(current_pos-self.__transformer_pos)
            if(delta >= 2): 
                print("Hard transformer switch happened ")
            self.__transformer_pos = current_pos
            
# REQ SST case
# calculate V6 and check if it is reasonable 
# combines I6 and V0, which are both measured at Trafo 0 and Solar Roof 6, respectivly
class SST_V_6(NeighbourhoodRequirementCheckStrategy):
    async def check(self): 
        
        v_0 = await self.get_v_data_from_sensor("sensor_v_0")
        i_6_3 = await self.get_c_data_from_sensor("sensor_c_6")
        i_6 = i_6_3[:3]
        z_6 = 5 # todo add correct value
        
        v_6 = v_0 - i_6 * z_6
        max_v = 5
        if v_6 > max_v: 
            print("Calculated V6 is unreasonable, either V0 or I6 are corrupted.")
       
# helper class 
class SST_helper(NeighbourhoodRequirementCheckStrategy):
# helper function
# calculates v2
    async def _calc_v_2(self): 
        z_2 = 5 # todo fix real value 
        v_2_l = await self.get_v_data_from_sensor("sensor_v_2")
        i_2_3 = await self.get_c_data_from_sensor("sensor_c_2")
        i_2 = i_2_3[:3]
        v_2 = v_2_l + i_2 * z_2
        
        return v_2 
    
    # helper function
    # calculates V4
    async def _calc_v_4(self): 
        z_5 = 5 #todo fix real value
        v_5_l = await self.get_v_data_from_sensor("sensor_v_5")
        i_5_3 = await self.get_c_data_from_sensor("sensor_c_5")
        i_5 = i_5_3[:3]
        v_5 = v_5_l + i_5 * z_5
        
        z_45 = 5 # todo fix real value
        v_4 = v_5 + i_5 * z_45
        
        return v_4 
    
    # helper function
    # calculates I4
    async def _calc_i_4(self):
        z_34 =  5 # todo fix real value
        z_23 = 5 # todo fix real value
        # asuuming I 3 = [0,0,0]
        i_3 = np.asarray([complex(0,0)],[complex(0,0)],[complex(0,0)])
        
        i_5_3 = await self.get_c_data_from_sensor("sensor_c_5")
        i_5 = i_5_3[:3]
        
        v_2 = self._calc_v_2()
        v_4 = self._calc_v_4()
        
        i_4 = (-i_3*z_23-i_5*z_34+v_2-v_4)/(z_23+z_34)
        
        return i_4
    
    # helper function 
    # caluclates V1
    async def _calc_v_1(self):
        z_12 = 5 # todo fix 
        v_2 = self._calc_v_2()
        
        # asuuming I 3 = [0,0,0]
        i_3 = np.asarray([complex(0,0)],[complex(0,0)],[complex(0,0)])
        
        i_4 = self._calc_i_4()
        
        i_2_3 = await self.get_c_data_from_sensor("sensor_c_2")
        i_2 = i_2_3[:3]
        
        i_5_3 = await self.get_c_data_from_sensor("sensor_c_5")
        i_5 = i_5_3[:3]
        
        i_12 = i_2 + i_3 + i_4 + i_5 
        v_1 = v_2 + i_12 * z_12
        
        return v_1
             
# REQ SST case 
# calculate V3 from the left side anc check if it is reasonable 
# combines V2, V5 and a fixed I3 (or I4, but here implemented as fixed I3)
# requires House 5 and farm 2 
class SST_V_3_L(SST_helper):
    async def check(self):
       
        v_2 = self._calc_v_2()
        v_4 = self._calc_v_4()
        
        z_34 =  5 # todo fix real value
        z_23 = 5 # todo fix real value
        
        # asuuming I 3 = [0,0,0]
        i_3 = np.asarray([complex(0,0)],[complex(0,0)],[complex(0,0)])
        
        v_3 = (v_2*z_34 + v_4*z_23-i_3*z_23*z_34)/(z_34+z_23)
        
        max_v = 5
        if v_3 > max_v: 
            print("Calculated V3 is unreasonable, either V2 or I5 are corrupted.")     
    
   
    
# REQ SST case 
# calculate I_4 with assumed and fixed I_3 to check if it is reasonable 
# utilizes House 5 and Farm 2 
class SST_I_4(SST_helper):
    async def check(self):
        i_4 = self._calc_i_4()
        
        max_i = 5 # todo fix 
        
        if i_4 > max_i: 
            print("Calculated I_4 is unreasonable, either Farm 2 or House 5 are corrupted.")  

    
    
# REQ SST case 
# calculate v1 and check if it is reasonable 
# with farm 2 and house 5 
class SST_V_1(SST_helper):
    async def check(self): 
        
        v_1 = self._calc_v_1()
         
        max_v = 5 # todo fix
        if v_1 > max_v: 
            print("Calculated V1 is unreasonable, either Farm 2 or House 5 are corrupted.")   

# REQ SST Case 
# Neighbourhhood +, 
# because we need farm 2 and house 5 to calculate v1 and then still input from trafo 0 to compare with v0 there 
class SST_I_1(SST_helper):
    async def check(self): 
        max_i = 5 # todo fix 
        
        v_0 = await self.get_v_data_from_sensor("sensor_v_0")
        v_1 = self._calc_v_1()
        
        z_01 = 10 # todo fix 
        i_01 = (v_0-v_1)/z_01
        
        # calculating i_12 
        # asuuming I 3 = [0,0,0]
        i_3 = np.asarray([complex(0,0)],[complex(0,0)],[complex(0,0)])
        i_4 = self._calc_i_4()
        i_2_3 = await self.get_c_data_from_sensor("sensor_c_2")
        i_2 = i_2_3[:3]
        i_5_3 = await self.get_c_data_from_sensor("sensor_c_5")
        i_5 = i_5_3[:3]
        
        i_12 = i_2 + i_3 + i_4 + i_5 
        
        i_1 = i_01-i_12 
        
        if i_1 > max_i: 
            print("Calculated I_1 is unreasonable, either Trafo station 0, Farm 2 or House 5 are corrupted.")  
            
# REQ SST Case
# neighbourhood + 
# I_7 and I_8 should be reasonable 
# can only be checked/calculated together with the information we have
# utilizes all inputs 
class SST_I_7_8(SST_helper):  
    async def check(self): 
        i_max_together = 5 
        
        v_0 = await self.get_v_data_from_sensor("sensor_v_0")
        v_1 = self._calc_v_1()
        
        z_01 = 10 # todo fix 
        i_01 = (v_0-v_1)/z_01
        
        i_0_3 = await self.get_c_data_from_sensor("sensor_c_0")
        i_0 = i_0_3[:3]
        
        i_6_3 = await self.get_c_data_from_sensor("sensor_c_6")
        i_6 = i_6_3[:3]
        
        z_06 = 5 #todo fix 
        
        i_06 = (i_0 - i_6)/z_06
        
        i_7_8 = i_0 - i_01 - i_06 
        if i_7_8 > i_max_together: 
            print("Calculated I_1 is unreasonable, either Trafo station 0, Farm 2, House 5 or Solar 6 are corrupted.")  
            
    
# REQ SST case 
# sanity check for voltage drop, 
# adapted for i_05,i_02,i_25 
class SST_Voltage_Drop(SST_helper):   
    async def _check_i_05(self): 
        v_0 = await self.get_v_data_from_sensor("sensor_v_0")
        
        v_2 = self._calc_v_2()

        z_5 = 5 #todo fix real value
        v_5_l = await self.get_v_data_from_sensor("sensor_v_5")
        i_5_3 = await self.get_c_data_from_sensor("sensor_c_5")
        i_5 = i_5_3[:3]
        v_5 = v_5_l + i_5 * z_5
        
        #todo fix me 
        z_05 = 5 
        z_25 = 5 
        z_02 = 5
        
        i_05 = (v_0-v_5)/z_05
        i_02 = (v_0-v_2)/z_02
        i_25 = (v_2-v_5)/z_25
        
        i_border = 20 
         
        if i_05 > i_border: 
            print("Calculated I_05 is unreasonable, either Trafo station 0, Farm 2, House 5 are corrupted.")  
        if i_02 > i_border: 
            print("Calculated I_02 is unreasonable, either Trafo station 0, Farm 2, House 5 are corrupted.")  
        if i_25 > i_border: 
            print("Calculated I_25 is unreasonable, either Trafo station 0, Farm 2, House 5 are corrupted.")  
    

#REQ DEMKit case
class DEMKit_NM_Test_Case(NeighbourhoodRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S6: Only registered houses (or power generators) are feeding into the grid."""
        c1 = await self.get_c_data_from_sensor("sensor_21")
        lms = await self.get_data_from_lm(0)
        #print("Monitor1: " + str(lms[0][1]))
        lms = await self.get_data_from_lm(1)
        #print("Monitor2: " +  str(lms[1][1]))
        lms = await self.get_data_from_lm(2)
        print("Monitor3: " +  str(lms[2][1]))
        #lms = await self.get_data_from_lm(3)
        #print("Monitor4: " +  str(lms[3][1]))
    
#REQ DEMKit case
class DEMKit_S6_Registered_Feedin_Only(NeighbourhoodRequirementCheckStrategy):
    old_smartmeter_data = [1323.0, 96.0, 1272.0] #Hardcoded first smartmeter values as to not get a violation each start

    async def check(self):
        """Checks Requirement S6: Only registered houses (or power generators) are feeding into the grid."""
        sum_sm_currents = 0
        sum_old_sm_currents = 0
        smartmeter_data, feeder_current = await asyncio.gather(self.get_lm_sm_data(), self.get_c_data_from_sensor("sensor_34"))
        power_flow_direction = (feeder_current >= 0)
        irgendwas = [0, 0, 0]
        
        # Adds the value of current measured in all smart meters
        for i in range(3):
            sum_sm_currents += smartmeter_data[i][1]
            sum_old_sm_currents += self.old_smartmeter_data[i]
            irgendwas[i] = smartmeter_data[i][1]
        
        # If neighborhood production < consumption:
        if power_flow_direction:
            # If total consumption of all combined houses exceeds the feeders measurement, an alert is thrown
            if (feeder_current + 10 < sum_sm_currents) or ((feeder_current < sum_old_sm_currents) and (sum_sm_currents > sum_old_sm_currents)):
                # Report to console
                print(self.old_smartmeter_data)
                print(irgendwas)
                self.logger.error("NM: Requirement S6 violated! Power flow: feeder(%sW) -> houses(%sW)", feeder_current, sum_sm_currents)
        # If neighborhood production < consumption:
        # If total production of all combined houses exceeds the feeders measurement, an alert is thrown
        else:
            if (feeder_current > sum_sm_currents + 10) or ((feeder_current > sum_old_sm_currents) and (sum_sm_currents > sum_old_sm_currents)):
                # Report to console
                print(self.old_smartmeter_data, feeder_current)
                print(irgendwas)
                self.logger.error("NM: Requirement S6 violated! Power flow: houses(%sW) -> feeder(%sW)", sum_sm_currents, feeder_current)
        for i in range(3):
            self.old_smartmeter_data[i] = smartmeter_data[i][1]

#REQ DEMKit case
# Looks at last 10 (smart meter) values of each local monitor and checks for sudden spikes
class DEMKit_S7_Anomaly_Power_Surge(NeighbourhoodRequirementCheckStrategy):
    last_value = [0, 0, 0]
    count = 0

    async def check(self):
        """Checks Requirement S7: Operator defined threshold of current in neighborhood is met for all meters."""
        smartmeter_data = await self.get_lm_sm_data()
        self.count += 1
        for i in range(3):
            value = smartmeter_data[i][1]
            last = self.last_value[i]
            if (abs(value) > (abs(last) * 7.5)) and (self.count > 3):
                self.logger.error("NM: Requirement S7 violated! The last recorded value for LM%s was %sW, but the most recent value is %sW!", (i + 1), last, value)
            self.last_value[i] = value