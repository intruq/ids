import asyncio
import os
import uuid
import sys

from ids_lib import opc_local_monitor
from ids_lib.config.config_lm import LMConfig


def run_lm():
    # Setup config based on environment
    config = LMConfig()
    config.uuid = "lm00" + str(uuid.uuid4())[4:]
    config.c2_address = os.getenv('IDS_C2_ADDRESS')
    config.opc_domain = os.getenv('IDS_OPC_DOMAIN')
    config.lm_opc_address = os.getenv('IDS_LM_OPC_ADDRESS')
    config.lm_opc_port = os.getenv("IDS_LM_OPC_PORT")
    config.nm_cert = os.getenv('IDS_NM_CERT')
    config.c2_cert = os.getenv('IDS_C2_CERT')
    config.cert = os.getenv('IDS_CERT')
    config.private_key = os.getenv('IDS_PRIVATE_KEY')
    config.private_key_password = os.getenv('IDS_PRIVATE_KEY_PASSWORD')
    config.rtu_modbus_host = os.getenv('IDS_RTU_MODBUS_HOST')
    config.rtu_modbus_port = os.getenv('IDS_RTU_MODBUS_PORT')
    config.label = "UT165957"
    config.hostname = "UT165957"
    config.case = os.getenv("CASE")

    with open(os.getenv('IDS_RTU_CONFIG_FILE'), 'r') as file:
        config.rtu_config = file.read()
       # print(config.rtu_config)

    # Run monitor forever
    asyncio.run(opc_local_monitor.main(config))


if __name__ == '__main__':
    run_lm()
