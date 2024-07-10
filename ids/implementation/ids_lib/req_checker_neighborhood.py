import asyncio
import json


def get_meter_data(data1, data2, m):
    """Checks if the meter m is contained in either one of the MeterData lists and returns the corresponding MeterData
    object. """
    for d in data1.meters:
        if d.id == m["id"]:
            return d

    for d in data2.meters:
        if d.id == m["id"]:
            return d

    return None


def get_switch_data(data1, data2, s):
    """Checks if the switch is contained in either one of the SwitchData lists and returns the corresponding SwitchData
        object. """
    for d in data1.switches:
        if d.id == s["id"]:
            return d

    for d in data2.switches:
        if d.id == s["id"]:
            return d

    return None


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
                self._checkReq1(),
               # self.__logger.error("No requirement checks implemented.")
            )
        except Exception as e:
            self.__logger.error(e)

    async def get_data_from_lm(self, i_of_lm):
        """Get the latest data values from the specified local monitor."""
        data_node = None                  
        data_node = self.__client_lms[i_of_lm]["data_node"]
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
        
    async def _checkReq1(self):
        data_lm1 = await self.get_data_from_lm(0)
       # print(data_lm1)
        
        for c in data_lm1:
            if int(c[1]) > 0: 
                print("OK")
            else:
                print("Requirement violated")
                
        data_lm2 = await self.get_data_from_lm(1)
        #print(data_lm2)
        