import asyncio
import numpy as np 
class ReqCheckerLocal:

    def __init__(self, rtu_config, data_ref, violations_queue, logger):
        self.__rtu_conf = rtu_config
        self.__data_ref = data_ref
        self.__vio_queue = violations_queue
        self.logger = logger

    async def check_requirements(self):
        """Check all requirements of the local scope"""
        await asyncio.gather(
            self._check_req_1_c(),
            self._check_req_1_v(), 
            self._check_req_2()
        )

    # REQ for Coteq case
    # REQ for SST case
    async def _check_req_1_c(self):
        """Checks Requirement S7: Safety threshold regarding current is met at every meter."""
        data = await self.__data_ref.read_value()
        meter_config = self.__rtu_conf["meters"]
        for m in meter_config:
            max_current = float(m["s_current"])
            d = get_meter_data(data, m)
            temp_current = d.current
            if temp_current > max_current:
                # Add violation to queue
                self.__vio_queue.put_nowait({
                    "req_id": 7,
                    "component_id": m["id"]}
                )

                # Report to console
                self.logger.error("Requirement 7 violated! Max current in %s should be < %s but is currently %s",
                            m["id"], max_current, round(temp_current, 3))
    
    # REQ for Coteq case
    # REQ for SST case
    async def _check_req_1_v(self):
        """Checks Requirement S8: Safety threshold regarding voltage is met at every meter."""
        # Get meter data from server
        data = await self.__data_ref.read_value()
        meter_config = self.__rtu_conf["meters"]
        for m in meter_config:
            max_voltage = float(m["s_voltage"])
            d = get_meter_data(data, m)
            temp_voltage = d.voltage
            if temp_voltage > max_voltage:
                # Add violation to queue
                self.__vio_queue.put_nowait({
                    "req_id": 8,
                    "component_id": m["id"]}
                )

                # Report to console
                self.logger.error("Requirement 8 violated! Max voltage in %s should be < %s but is currently %s",
                            m["id"], max_voltage, round(temp_voltage, 3))
    
    # REQ Coteq case      
    async def _check_req_2(self): 
        d = await self.get_v_data("sensor_115")
        if(float(d)< 0): 
            self.logger.error("Something strange happens at the solar plant.")       
    
    # REQ Coteq case 
    # check saftey threshold for toegestann strom on both sides 
    # subcheck for LV side
    # subcheck for MV side
    async def _check_transformer_req_I(self):
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
    async def _check_transformer_req_II(self):
        
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
    async def _check_transformer_req_III(self):
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
      
    
    # REQ SST case 
    # calculate V4 and check if it is reasonable 
    # local check from the House 5 
    async def _check_v_4(self): 
        
        v_4 = self._calc_v_4()
        max_v = 10 
        
        if v_4 > max_v: 
            self.logger.error("Calculated V4 is unreasonable, either V5 or I5 are corrupted.")
            
    
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
    # calculate V3 from right side and check if it is reasonable 
    # local check from house 5  
    async def _check_v3_rightside(self): 
        
        v_3_r = self._calc_v_3_r()
        
        max_v = 10 
        
        if v_3_r > max_v: 
            self.logger.error("Calculated V3 from the right side is unreasonable, either V5 or I5 are corrupted in case of assumed I4 = 0.")
        
        return 0 
        
    async def get_raw_meter_data(self, sensor_name): 
        data = await self.__data_ref.read_value()
        meter_config = self.__rtu_conf["meters"]
        d = []
        for m in meter_config: 
                if(m["id"] == sensor_name):
                    d = get_meter_data(data, m)
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
    


def get_meter_data(data, m):
    for d in data.meters:
        if d.id == m["id"]:
            return d


def get_switch_data(data, s):
    for d in data.switches:
        if d.id == s["id"]:
            return d
