import asyncio
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
            
    async def _check_req_2(self): 
        d = await self.get_v_data("sensor_115")
        if(float(d)< 0): 
            self.logger.error("Something strange happens at the solar plant.")       
    
    # check saftey threshold for toegestann strom on both sides 
    # subcheck for LV side
    # subcheck for MV side
    async def _check_transformer_req_I(self):
        togestaan_lv = 550
        lv_side = await self.get_c_data("sensor_c_1") # maybe check with 3 phase current and transform it to once phase current 
        if(float(lv_side)>togestaan_lv):
            self.logger.error("LV side current at transformer is higher than allowed.")
        
        togestaan_mv = 21.5
        mv_side = await self.get_c_data("sensor_212")
        if(float(mv_side)>togestaan_mv):
            self.logger.error("LM side current at transformer is higher than allowed.")
                

    
    # use THD als saftey threshold to secure the electornic devices in the LV grid, as a value that is independent of I and V 
    async def _check_transformer_req_II(self):
        
        # todo: adapt data load so that it actually provides the thd data
        thd_1 = await self.get_c_data("thd_1")
        thd_2 = await self.get_c_data("thd_2")
        thd_3 = await self.get_c_data("thd_3")
        
        # todo: figure out a meaningful threshold for this 
        saftey_threshold = 5

        if thd_1 < saftey_threshold  and thd_2 < saftey_threshold and thd_3 < saftey_threshold: 
            print("thd looks good")
        else: 
            self.logger.error("Power quality undesirable on LV side of transformer.")    
            
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
