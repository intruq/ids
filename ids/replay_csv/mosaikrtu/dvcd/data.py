# data.py
# is a datablock object for the Modbus Server
# originally developed by Chromik
# only small adaptions done by me (Verena Menzel)
# version 0.2
from enum import Enum

from pymodbus3.datastore import ModbusSequentialDataBlock
from pymodbus3.datastore import ModbusSlaveContext
from pymodbus3.payload import BinaryPayloadBuilder
from pymodbus3.payload import BinaryPayloadDecoder
from pymodbus3.constants import Endian

import os

# logging options
import logging

logging.basicConfig()
log = logging.getLogger('datablock')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)


class Datatype(Enum):
    BOOLEAN = "bool"
    FLOAT32 = "32bit_float"
    FLOAT64 = "64bit_float"
    NONE = None


class Objecttype(Enum):
    DI = "di"
    CO = "co"
    HR = "hr"
    IR = "ir"


class DataBlock(object):
    """
    Chromik:
    Not locked at the moment! =)

    Locking Datablock.
    Can't be simultaniously read from and/or written to. Threads beyond the first would get in line.
    """

    def __init__(self):
        self.di = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
        self.co = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
        self.hr = ModbusSequentialDataBlock(0x00, [0] * 0xFF)
        self.ir = ModbusSequentialDataBlock(0x00, [0] * 0xFF)

        self.store = ModbusSlaveContext(
            di=self.di,  # Single Bit, Read-Only
            co=self.co,  # Single Bit, Read-Write
            hr=self.hr,  # 16-Bit Word, Read-Only
            ir=self.ir)  # 16-Bit Word, Read-Write

    def get(self, object_type: str, address: int, count: int, data_type: str = None):
        """
        Generic 'get' method for LockedDataBlock. Figures out the underlying method to call according to _type.
        :param _type: Type of modbus register ('co', 'di', 'hr', 'ir')
        :param address: Index of the register
        :param count: The amount of registers to get sequentially
        :return: Value of requested index(es).
        """

        _type = Objecttype(object_type)
        _datatype = Datatype(data_type)

        if _datatype == Datatype.NONE:
            # log.debug("Retrieving a None type")
            if _type == Objecttype.DI:
                return self._get_di(address, count)
            elif _type == Objecttype.CO:
                return self._get_co(address, count)
            elif _type == Objecttype.HR:
                return self._get_hr(address, count)
            elif _type == Objecttype.IR:
                return self._get_ir(address, count)
        elif _datatype == Datatype.BOOLEAN:
            if _type == Objecttype.DI:
                values = self._get_di(address, count)
            elif _type == Objecttype.CO:
                values = self._get_co(address, count)
            else:
                print("t: {}   a: {}   c: {}")
                raise ValueError
            decoder = BinaryPayloadDecoder.from_coils(values.bits,
                                                      endian=Endian.Big)
            return decoder.decode_bits()
        else:
            if _type == Objecttype.HR:
                values = self._get_hr(address, count)
            elif _type == Objecttype.IR:
                values = self._get_ir(address, count)
            else:
                print("t: {}   a: {}   c: {}")
                raise ValueError
            decoder = BinaryPayloadDecoder.from_registers(values, endian=Endian.Big)
            if _datatype == Datatype.FLOAT32:
                return decoder.decode_32bit_float()
            elif _datatype == Datatype.FLOAT64:
                return decoder.decode_64bit_float()

    def set(self, object_type: str, address: int, values: any, data_type: str = None):
        """
        Generic 'set' method for LockedDataBlock. Figures out the underlying method to call according to _type.
        :param _type: Type of modbus register ('co', 'di', 'hr', 'ir')
        :param address: Index of the register
        :param values: Value(s) to set the addresses to.
        :return: Value of requested address for type.
        """
        # Transfrom into Objecttype
        _type = Objecttype(object_type)
        _datatype = Datatype(data_type)

        # We assume correct types and pass through
        if _datatype == Datatype.NONE:
            # print("Adding a None type")
            if _type == Objecttype.DI:
                self._set_di(address, values)
            elif _type == Objecttype.CO:
                self._set_co(address, values)
            elif _type == Objecttype.HR:
                self._set_hr(address, values)
            elif _type == Objecttype.IR:
                self._set_ir(address, values)
            else:
                print("t: {}   a: {}   v: {}")
                raise ValueError
        else:
            # We try to cast to appropriate type
            if _datatype == Datatype.BOOLEAN:
                # convert to boolean
                val = values if type(values) == bool else values == "True"

                if _type == Objecttype.DI:
                    self._set_di(address, val)
                elif _type == Objecttype.CO:
                    self._set_co(address, val)
            else:
                val = float(values)
                builder = BinaryPayloadBuilder(endian=Endian.Big)
                if _datatype == Datatype.FLOAT32:
                    builder.add_32bit_float(val)
                elif _datatype == Datatype.FLOAT64:
                    builder.add_64bit_float(val)

                payload = builder.to_registers()
                if _type == Objecttype.HR:
                    self._set_hr(address, payload)
                elif _type == Objecttype.IR:
                    self._set_ir(address, payload)

    def _get_di(self, address, count):
        values = self.di.get_values(address + 1, count)
        return values

    def _set_di(self, address, values):
        self.di.set_values(address + 1, values)

    def _get_co(self, address, count):
        values = self.co.get_values(address + 1, count)
        return values

    def _set_co(self, address, values):
        self.co.set_values(address + 1, values)

    def _get_hr(self, address, count):
        values = self.hr.get_values(address + 1, count)
        return values

    def _set_hr(self, address, values):
        self.hr.set_values(address + 1, values)

    def _get_ir(self, address, count):
        values = self.ir.get_values(address + 1, count)
        return values

    def _set_ir(self, address, values):
        self.ir.set_values(address + 1, values)
