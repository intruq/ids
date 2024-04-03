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
            self._check_req_1(),
            self._check_req_2(),
            self._check_req_3(),
            self._check_req_4(),
            self._check_req_7(),
            self._check_req_8()
        )

    async def _check_req_1(self):
        """Check Requirement 1: Incoming current matches outgoing current at one bus."""
        data = await self.__data_ref.read_value()

        for bus in self.__rtu_conf["buses"]:
            power_lines_incoming = bus["power_lines_in"]
            power_lines_outgoing = bus["power_lines_out"]

            # Get ids from incoming and outgoing power lines
            power_lines_in_ids = []
            if "id" in power_lines_incoming:
                power_lines_in_ids.append(power_lines_incoming["id"])
            elif "ids" in power_lines_incoming:
                power_lines_in_ids = power_lines_incoming["ids"]
            power_lines_out_ids = []
            if "id" in power_lines_outgoing:
                power_lines_out_ids.append(power_lines_outgoing["id"])
            elif "ids" in power_lines_outgoing:
                power_lines_out_ids = power_lines_outgoing["ids"]

            # Get current for incoming and outgoing power lines
            readings_in = []
            readings_out = []
            # for m in self.__rtu_conf["meters"]:
            #     if m["power_line_id"] in power_lines_in_ids and m["bus_id"] == bus["id"]:
            #         d = get_meter_data(data, m)
            #         readings_in.append(d)
            #     elif m["power_line_id"] in power_lines_out_ids and m["bus_id"] == bus["id"]:
            #         d = get_meter_data(data, m)
            #         readings_out.append(d)

            for m in self.__rtu_conf["meters"]:
                if m["power_line_id"] in power_lines_in_ids:
                    power_lines_in_ids.remove(m["power_line_id"]) # Only one meter per branch shall be checked
                    d = get_meter_data(data, m)
                    readings_in.append(d)
                elif m["power_line_id"] in power_lines_out_ids:
                    power_lines_out_ids.remove(m["power_line_id"]) # Only one meter per branch shall be checked
                    d = get_meter_data(data, m)
                    readings_out.append(d)

            # Calculate sum for incoming and outcoming current
            sum_current_in = 0
            sum_current_out = 0

            calc = "calculation: in "

            for d in readings_in:
                sum_current_in += d.current
                calc += "+ {}".format(d.current)

            calc += "  =  "

            for d in readings_out:
                sum_current_out += d.current
                calc += "{} + ".format(d.current)

            calc += " out"

            # Check if sums are equal
            if abs(round(sum_current_in, 2) - round(sum_current_out, 2)) > 0.1:
                # Add violation to queue
                self.__vio_queue.put_nowait({
                    "req_id": 1,
                    "component_id": bus["id"]}
                )

                # Report to console
                self.logger.error("Requirement 1 violated! Sum of incoming current at bus %s is %s, "
                            "and sum of outgoing current is %s. " + calc, bus["id"], round(sum_current_in, 2),
                            round(sum_current_out, 2))

    async def _check_req_2(self):
        """Checks Requirement 2: All voltages reported at one bus are equal."""
        data = await self.__data_ref.read_value()

        for bus in self.__rtu_conf["buses"]:
            # Get the voltage readings from each meter on this bus
            voltage_readings = []
            for m in self.__rtu_conf["meters"]:
                #TODO: using the bus id of a meter might be unrealistic as all meters on a powerline
                # do also need to measure the same voltage
                if m["bus_id"] == bus["id"]:
                    voltage_readings.append(get_meter_data(data, m))

            ref_voltage = round(voltage_readings[0].voltage, 2)
            for d in voltage_readings:
                if not (ref_voltage - 0.05 <= round(d.voltage, 2) <= ref_voltage + 0.05):
                    # Add violation to queue
                    self.__vio_queue.put_nowait({
                        "req_id": 2,
                        "component_id": bus["id"]}
                    )

                    # Report to console
                    self.logger.error("Requirement 2 violated! Voltage on bus %s measured by %s : %s (!= %s)",
                                bus["id"], d.id, round(d.voltage, 2), ref_voltage)

    async def _check_req_3(self):
        """Checks Requirement 3 (local scope): There is no current on a power line with an open switch."""
        data = await self.__data_ref.read_value()

        #self.logger.info("Data to be checked: {}\n\n\n".format(data))

        # Get all power lines with open switch
        open_switch_lines = []
        for s in self.__rtu_conf["switches"]:
            d = get_switch_data(data, s)

            #self.logger.info("Switch: {}\n\n".format(d.value))

            # Note: switch is open <=> switch.value = False
            if not d.value[0]:
                power_line_id = s["power_line_id"]
                open_switch_lines.append(power_line_id)

        #self.logger.info("Open switch lines found: {}\n\n\n".format(open_switch_lines))


        # Get all local power lines
        power_lines_local = []
        for power_line in self.__rtu_conf["power_lines"]:
            if power_line["id"] in open_switch_lines:
                power_lines_local.append(power_line["id"])

        # Get values of all meters on local power line with open switch
        for m in self.__rtu_conf["meters"]:
            if m["power_line_id"] in power_lines_local:
                d = get_meter_data(data, m)
                # If current != 0
                if d.current:
                    # Add violation to queue
                    self.__vio_queue.put_nowait({
                        "req_id": 3,
                        "component_id": m["power_line_id"]}
                    )

                    # Report to console
                    self.logger.error("Requirement 3 (local) violated! There is current on line %s with "
                                "an open switch", m["power_line_id"])

    async def _check_req_4(self):
        """Checks Requirement 4 (local scope): Measured voltage and current remain the same over the length of a
        power line. """
        data = await self.__data_ref.read_value()

        for power_line in self.__rtu_conf["power_lines"]:
            # Get all meter ids from local power line
            pl_meters = []
            for m in self.__rtu_conf["meters"]:
                if m["power_line_id"] == power_line["id"]:
                    d = get_meter_data(data, m)
                    pl_meters.append(d)

            # Compare the values with one another
            ref_current = round(pl_meters[0].current, 2)
            ref_voltage = round(pl_meters[0].voltage, 2)
            for d in pl_meters:
                if not (ref_current - 0.05 <= round(d.current, 2) <= ref_current + 0.05):
                    # Add violation to queue
                    self.__vio_queue.put_nowait({
                        "req_id": 4,
                        "component_id": power_line["id"]}
                    )

                    # Report to console
                    self.logger.error("Requirement 4 (local) violated! Current on line %s measured by %s : %s (!= %s)",
                                power_line["id"], d.id, round(d.current, 2), ref_current)

                if not (ref_voltage - 0.05 <= round(d.voltage, 2) <= ref_voltage + 0.05):
                    # Add violation to queue
                    self.__vio_queue.put_nowait({
                        "req_id": 4,
                        "component_id": power_line["id"]}
                    )

                    # Report to console
                    self.logger.error("Requirement 4 (local) violated! Voltage on line %s measured by %s : %s (!= %s)",
                                power_line["id"], d.id, round(d.voltage, 2), ref_voltage)

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
