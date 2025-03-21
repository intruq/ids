import asyncio
import os
import uuid
import sys

from ids_lib import opc_neighborhood_monitor
from ids_lib.config.config_nm import NMConfig


def run_nm():
    # Setup config based on environment
    config = NMConfig()
    config.uuid = "nm00" + str(uuid.uuid4())[4:]
    config.c2_address = os.getenv('IDS_C2_ADDRESS')
    config.opc_domain = os.getenv('IDS_OPC_DOMAIN')
    config.nm_opc_address = os.getenv('IDS_NM_OPC_ADDRESS')
    config.lm_cert = os.getenv('IDS_LM_CERT')
    config.c2_cert = os.getenv('IDS_C2_CERT')
    config.cert = os.getenv('IDS_CERT')
    config.private_key = os.getenv('IDS_PRIVATE_KEY')
    config.private_key_password = os.getenv('IDS_PRIVATE_KEY_PASSWORD')
    config.client_address_list.append(os.getenv('IDS_CLIENT_ADDRESS_1'))
    config.client_address_list.append(os.getenv('IDS_CLIENT_ADDRESS_2'))
    config.client_address_list.append(os.getenv('IDS_CLIENT_ADDRESS_3'))
    config.client_address_list.append(os.getenv('IDS_CLIENT_ADDRESS_4'))
    
    config.case = os.getenv('CASE')
    
    with open(os.getenv('IDS_BR_CONFIG_FILE'), 'r') as file:
        config.br_config = file.read()
      


    # Run monitor forever
    asyncio.run(opc_neighborhood_monitor.main(config))


if __name__ == '__main__':
    run_nm()
