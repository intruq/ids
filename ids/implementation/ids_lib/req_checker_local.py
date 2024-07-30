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
