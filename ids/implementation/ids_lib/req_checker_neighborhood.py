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
                self._checkReq1(lm_address),
                self.__logger.error("No requirement checks implemented.")
            )
        except Exception as e:
            self.__logger.error(e)

    async def get_data_from_lm(self, lm_address):
        """Get the latest data values from the specified local monitor."""
        print("Versuche Daten zu lesen")
        data_node = None
       # for lm in self.__client_lms:
            #if lm["url"] == lm_address:
       # data_node = lm_address["data_node"]
       # print(data_node)
     #   try:
      #      lm_data = await data_node.read_value()
      #  except Exception:
    #        lm_data = None
     #   return lm_data
    
    async def _checkReq1(self, lm_address):
        data = await self.get_data_from_lm(lm_address)
        print(data)
        print("____")
        #tmp = json.loads(br.region_definition)
      #  print(tmp)
        self.__logger.error("Test requirement!")
