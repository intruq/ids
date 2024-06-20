import asyncio
import logging


class ReqCheckerLocal:

    def __init__(self, rtu_config, data_ref, violations_queue, logger):
        self.__rtu_conf = rtu_config
        self.__data_ref = data_ref
        self.__vio_queue = violations_queue
        self.logger = logger

    async def check_requirements(self):
        """Check all requirements of the local scope"""

        #self.logger.error(self.__rtu_conf)

        await asyncio.gather(
            self._check_req_7(),
            self._check_req_8()
        )


    async def _check_req_7(self):
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

    async def _check_req_8(self):
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


def get_meter_data(data, m):
    for d in data.meters:
        if d.id == m["id"]:
            return d


def get_switch_data(data, s):
    for d in data.switches:
        if d.id == s["id"]:
            return d
