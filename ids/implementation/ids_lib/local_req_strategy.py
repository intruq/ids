from abc import ABC, abstractmethod
import numpy as np 

# Strategy class from which all single requirements will inherit, to make this easily extendible 
class LocalRequirementCheckStrategy(ABC):
    
    def __init__(self, rtu_config, data_ref, violations_queue, logger):
        self._rtu_conf = rtu_config
        self._data_ref = data_ref
        self._vio_queue = violations_queue
        self.logger = logger
        
    @abstractmethod
    def check(self):
        pass
    
    # helper functions to access the data 
    async def get_raw_meter_data(self, sensor_name): 
        data = await self._data_ref.read_value()
        meter_config = self._rtu_conf["meters"]
        d = []
        for m in meter_config: 
                if(m["id"] == sensor_name):
                    d = self.get_meter_data(data, m)
        return d
    
    async def get_v_data(self, sensor_name):
        d = await self.get_raw_meter_data(sensor_name)
        if d: 
            return d.voltage
        else: 
            return []
        
    async def get_c_data(self, sensor_name):
        d = await self.get_raw_meter_data(sensor_name)
        if d: 
            return d.current
        else: 
            return []
    
    def get_meter_data(self, data, m):
        for d in data.meters:
            if d.id == m["id"]:
                return d


    def get_switch_data(self, data, s):
        for d in data.switches:
            if d.id == s["id"]:
                return d
            
    def get_lm_id(self):
        bus_config = self._rtu_conf["buses"]
        lm = []
        for b in bus_config:
            lm = b["id"]
        if lm:
            return int(lm[-1])
            
# REQ for Coteq case
# REQ for SST case
class Saftey_Threshold_C(LocalRequirementCheckStrategy):
    def __init__(self, rtu_config, data_ref, violations_queue, logger):
        super().__init__(rtu_config, data_ref, violations_queue, logger)
        
    async def check(self):
        """Checks Requirement S7: Safety threshold regarding current is met at every meter."""
        data = await self._data_ref.read_value()
        meter_config = self._rtu_conf["meters"]
        
        for m in meter_config:
            max_current = m["s_current"]
            d = self.get_meter_data(data, m)
            temp_current = d.current
            
            if temp_current > max_current:
                # Add violation to queue
                self._vio_queue.put_nowait({
                    "req_id": 7,
                    "component_id": m["id"]}
                )
                self.logger.error("Requirement 7 violated! Max current in %s should be < %s but is currently %s",
                            m["id"], max_current, round(temp_current, 3))

# REQ for Coteq case
# REQ for SST case
class Saftey_Threshold_V(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S8: Safety threshold regarding voltage is met at every meter."""
        # Get meter data from server
        data = await self._data_ref.read_value()
        meter_config = self._rtu_conf["meters"]
        for m in meter_config:
            max_voltage = m["s_voltage"]
            d = self.get_meter_data(data, m)
            temp_voltage = d.voltage
            if temp_voltage > max_voltage:
                # Add violation to queue
                self._vio_queue.put_nowait({
                    "req_id": 8,
                    "component_id": m["id"]}
                )

                # Report to console
                self.logger.error("Requirement 8 violated! Max voltage in %s should be < %s but is currently %s",
                            m["id"], max_voltage, round(temp_voltage, 3))
                

# REQ Coteq case      
class Solar_Plant_Sanity(LocalRequirementCheckStrategy):
    async def check(self): 
        d = await self.get_v_data("sensor_115")
        if(float(d)< 0): 
            self.logger.error("Something strange happens at the solar plant.")       
    
# REQ Coteq case 
# check saftey threshold for toegestann strom on both sides 
# subcheck for LV side
# subcheck for MV side
class Transformer_Saftey_Threshold_Current(LocalRequirementCheckStrategy):
    async def check(self):
        togestaan_lv = 550
        lv_side = await self.get_c_data("sensor_c_1") 
        # todo: maybe check with 3 phase current and transform it to once phase current 
        if(float(lv_side)>togestaan_lv):
            self.logger.error("LV side current at transformer is higher than allowed.")
        
        togestaan_mv = 21.5 #todo fix value
        mv_side = await self.get_c_data("sensor_212")
        if(float(mv_side)>togestaan_mv):
            self.logger.error("LM side current at transformer is higher than allowed.")
                

# REQ Coteq case
# use THD als saftey threshold to secure the electornic devices in the LV grid, as a value that is independent of I and V 
class THD_Threshold(LocalRequirementCheckStrategy):
    async def check(self):
        
        # todo: adapt data load so that it actually provides the thd data
        thd_1 = await self.get_c_data("thd_1")
        thd_2 = await self.get_c_data("thd_2")
        thd_3 = await self.get_c_data("thd_3")
        
        # todo: figure out a meaningful threshold for this 
        saftey_threshold = 5

        if thd_1 < saftey_threshold  and thd_2 < saftey_threshold and thd_3 < saftey_threshold: 
            print("THD looks good")
        else: 
            self.logger.error("Power quality undesirable on LV side of transformer.")    
            
# REQ Coteq case 
# no value should be outside of allowed values on both sides 
# subcheck for LV side 
# subcheck for MV side 
class Transformer_Border_Values(LocalRequirementCheckStrategy):
    async def check(self):
        #todo maybe add some margin for errors of a few percent 
        min_lv = 420
        max_lv = 420 
        lv_side = await self.get_v_data("sensor_v_1") # todo figure out correct values
        if(float(lv_side)>max_lv or float(lv_side)< min_lv):
            self.logger.error("LV side voltage at transformer is outside of allowed boundaries.")
        
        min_mv = 10250
        max_mv = 11250 
        mv_side = await self.get_v_data("sensor_212") # todo figure out correct values
        if(float(mv_side)>max_mv or float(mv_side)< min_mv):
            self.logger.error("MV side voltage at transformer is outside of allowed boundaries.")
      
# Further Level of Class 
# to combine SST Helper functions and make them available to all checks 
class SST_checks(LocalRequirementCheckStrategy): 
    
    # helper function, calculates V4
    async def _calc_v_4(self): 
        i_5_3 = await self.get_c_data("sensor_v_5") 
        i_5 = i_5_3[:3] # aus drei phasen eine machen ? check when real data is available 
        
        z5 = 5 # todo configure correct value 
        v_5_raw = await self.get_v_data("sensor_5")
        v_5 = v_5_raw + i_5 * z5 
        
        z45 = 5 # todo configure correct value 
        v_4 = v_5 + i_5*z45
        return v_4 

    # helper function 
    # caluclates V3 from the right side with assumed I4 = [0.0.0]
    async def _calc_v_3_r(self): 
        i_4 = np.asarray([complex(0,0)],[complex(0,0)],[complex(0,0)])
        
        v_4 = self._calc_v_4()
        
        z34 = 5 # todo configure correct value
        
        i_5_3 = await self.get_c_data("sensor_v_5") 
        i_5 = i_5_3[:3] # aus drei phasen eine machen ? check when real data is available 
        
        v_3_r = v_4 + z34*(i_5 + i_4)
        
        return v_3_r
    
# REQ SST case 
# calculate V4 and check if it is reasonable 
# local check from the House 5 
class SST_V_4(SST_checks):
    async def check(self): 
        
        v_4 = self._calc_v_4()
        max_v = 10 
        
        if v_4 > max_v: 
            self.logger.error("Calculated V4 is unreasonable, either V5 or I5 are corrupted.")
            
    
        
# REQ SST case 
# calculate V3 from right side and check if it is reasonable 
# local check from house 5  
class SST_V_3(SST_checks):
    async def check(self): 
        
        v_3_r = self._calc_v_3_r()
        
        max_v = 10 
        
        if v_3_r > max_v: 
            self.logger.error("Calculated V3 from the right side is unreasonable, either V5 or I5 are corrupted in case of assumed I4 = 0.")
        
        return 0 
    
#Test Case DEMKit
    
class Demkit_Test_Case(LocalRequirementCheckStrategy):
    async def check(self):
        """Reads meter value and passes it to log."""
        # Get meter data from server
        print("Start Test")
        data = await self._data_ref.read_value()
        print(data)
        meter_config = self._rtu_conf["meters"]
        print(meter_config)
        for m in meter_config:
            print(self.get_meter_data(data, m))
            #print(self.get_meter_data(data, m).id)
                
# Requirement Checks DEMKit

class DEMKit_S1_Household_Grid_Balance(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S1: In every household the power generated equals the power consumed."""
        if not self.get_lm_id() == 4:
            # Get meter data from server
            meter_current = await self.get_c_data("sensor_21")
            meter_config = self._rtu_conf["meters"]
            data = await self._data_ref.read_value()
            temp_current = meter_current * (-1)

            for m in meter_config:
                temp_current += self.get_meter_data(data, m).current

            if not (meter_current -1 <= temp_current <= meter_current + 1):
                # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 1,
                        "component_id": "sensor_21"}
                    )
                    
                    # Report to console
                    self.logger.error("LM%s: Requirement S1 violated! sensor_21 current of %sW is not equal to produced/consumed current of the household grid: %sW",
                                self.get_lm_id(), meter_current, temp_current)
        
class DEMKit_S2_Saftey_Threshold_C(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S2: Safety threshold regarding current is met at every meter."""
        # Get meter data from server
        data = await self._data_ref.read_value()
        meter_config = self._rtu_conf["meters"]
        for m in meter_config:
            max_current = m["s_current"]
            min_current = 0
            temp_current = self.get_meter_data(data, m).current
            if not (min_current <= temp_current <= max_current):
                # Add violation to queue
                self._vio_queue.put_nowait({
                    "req_id": 2,
                    "component_id": m["id"]}
                )
                # Report to console
                self.logger.error("LM%s: Requirement S2 violated! Max current in %s should be > 0 and < %s but is currently %s",
                            self.get_lm_id(), m["id"], max_current, round(temp_current, 3))
                
class DEMKit_S3_Battery_Overcharge(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S3: State of charge never exceeds defined limit(12000Wh)."""
        if not self.get_lm_id() == 4:
            # Get meter data from server
            # sensor_25 stores the SoC data in the "voltage-slot" and the Current data in the "current-slot"
            soc_current = await self.get_v_data("sensor_25")
            soc_max = 12000
            soc_min = 0
            battery_current = await self.get_c_data("sensor_25")
            
            if isinstance(battery_current, float):

                if not (soc_min <= soc_current <= soc_max):
                    # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 3,
                        "component_id": "sensor_25"}
                    )

                    # Report to console
                    self.logger.error("LM%s: Requirement S3 violated! Max battery soc should be %s <= and < %s but is currently %s",
                                self.get_lm_id(), soc_min, soc_max, round(soc_current, 3))
                
                if soc_current == soc_max and battery_current > 0:
                    # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 3,
                        "component_id": "sensor_25"}
                    )

                    # Report to console
                    self.logger.error("LM%s: Requirement S3 violated! Battery soc is 100%%, but battery current %s > 0.", self.get_lm_id(), battery_current)

                if soc_current == soc_min and battery_current < 0:
                    # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 3,
                        "component_id": "sensor_25"}
                    )

                    # Report to console
                    self.logger.error("LM%s: Requirement S3 violated! Battery soc is 0%%, but battery current %s < 0.", self.get_lm_id(), battery_current)

class DEMKit_S4_Feedin_Only_Generators(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement 4: Only power generating devices can feed power into the grid."""
        # Get meter data from server
        if not self.get_lm_id() == 4:
            generators = ["sensor_21", "sensor_25", "sensor_33"]
            data = await self._data_ref.read_value()
            meter_config = self._rtu_conf["meters"]
            for m in meter_config:
                d = self.get_meter_data(data, m)
                temp_current = d.current
                if temp_current < 0 and not (m["id"] in generators):
                    # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 4,
                        "component_id": m["id"]}
                    )

                    # Report to console
                    self.logger.error("LM%s: Requirement S4 violated! Current of %s should be > 0 but is currently %s.",
                                self.get_lm_id(), m["id"], round(temp_current, 3))

class DEMKit_S5_Battery_Discharge(LocalRequirementCheckStrategy):
    async def check(self):
        """Checks Requirement S5: Battery dis-/charge rate does not exceed safe operational limit."""
        if not self.get_lm_id() == 4:
            # Get meter data from server
            max_current = 3700
            min_current = -3700
            battery_current = await self.get_v_data("sensor_25")
            
            if isinstance(battery_current, float):
                if not (min_current <= battery_current <= max_current):
                    # Add violation to queue
                    self._vio_queue.put_nowait({
                        "req_id": 5,
                        "component_id": "sensor_25"}
                    )

                    # Report to console
                    self.logger.error("LM%s: Requirement S5 violated! Battery current should be > %s and < %s but is currently %s",
                                self.get_lm_id(), min_current, max_current, round(battery_current, 3))