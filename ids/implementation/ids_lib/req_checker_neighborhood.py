import asyncio
import json

class ReqCheckerNeighborhood:

    def __init__(self, border_regions, client_lms, vio_queue, logger):
        self.__br = border_regions
        self.__client_lms = client_lms
        self.__vio_queue = vio_queue
        self.__logger = logger

    async def check_requirements(self, lm_address):
        """Check all requirements of the neighborhood scope"""
        try:
            await asyncio.gather(
                self._checkReq1(0),
                self._checkReq1(1),
                self._check_req_3(), 
                self._check_req_6()
            )
        except Exception as e:
            self.__logger.error(e)

    async def get_data_from_lm(self, i_of_lm):
        """Get the latest data values from the specified local monitor."""
        data_node = None                  
        data_node = self.__client_lms[i_of_lm]["data_node"]
        try:
            lm_data = await data_node.read_value()
            #print(lm_data)
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
        
        sensor_data = []
        
        for d in data_lm1: 
            if d[0] == name_of_sensor: 
                sensor_data = d
        
        for d in data_lm2: 
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
        
    async def _checkReq1(self, i_of_lm):
        data_lm1 = await self.get_data_from_lm(i_of_lm)        
        for c in data_lm1:
            if int(c[1]) < 0: 
                print("Requirement violated")
                
        
    async def _check_req_3(self): 
        
        v_1 = await self.get_c_data_from_sensor("sensor_213")
        v_2 = await self.get_c_data_from_sensor("sensor_114")
        
        if v_1 and v_2:
            diff = abs(v_1-v_2)
        
            if diff > 2: 
                print("Something strange going on between M1 and M2.")
        
            elif diff > 1: 
                print("Potentially Something strange going on between M1 and M2.")
            
            
    async def _check_req_6(self):
        
        mv = await self.get_c_data_from_sensor("sensor_212")
        
        if mv: 
            v_1 = await self.get_c_data_from_sensor("sensor_35") 
            v_2 = await self.get_c_data_from_sensor("sensor_36") 
            v_3 = await self.get_c_data_from_sensor("sensor_37")  
        
            if v_1: 
                av = (v_1 + v_2 + v_3)/3
                print(av)
                print("___")
                print(mv/av)
                print("Transformer all good.")
        
        