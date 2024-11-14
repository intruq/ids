# IDS_real_data_testcase

## privacy 
to prevent any data security problems, as of now, the actual real world data is not commited but only stored locally 

## How to connect new simulation/data sets

1. Replay or live connection 
    1. Replay: CSV file with time and all the different sensors 
    2. [replay.py](http://replay.py) needs to be adapted to reed the correct files, both for configuration and the actual csv files 
    3. skip the correct amount of header files 
    4. configure the amount of sensors per file 
    5. configure how long the server should run (e.g. the complete file or shorter, ideally all files have the same length) 
2. write config files for data input 
    1. need xml file for every data point with one entry per sensor + one entry per sensor as max + distinct port 
    2. index needs to be old index + 4 
    3. need JSON file per subgrid and per border region featuring the sensors - probably not so urgently needed any more because requirement checks are implemented rather fixed, yet better safe then sorry (generate subgrids first and then copy stuff from there to the border region) 
3. write config files for LM and NM 
    1. if possible, keep c2 template as is 
    2. adapt each needed LM 
        1. to have the correct port from the XML file
        2.  give it an own OPC port
        3.  make a table about who has which port
        4. adapt keys and certs if necessary, try not to  
    3. same for NMs, in addition 
        1. connect the correct client addresses 
4. generate new keys or use old ones
    1. if new ones should be used, use generate_ssl_certficate.py and make sure they are copied to the correct folder and the configuration files for the monitors are adapted to work with the new names 
5. Adapt development_setup.py
    1. create the correct amount of monitors of the correct type and read the input files for them
    2. might want to mute one or more monitors with 
    
    ```python
     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    ```
    
6. write new requirement checks matching the format 
    1. LM: 
        1. write a new case in ReqCheckerLocal featuring the needed Checks in the Configuration
        2. for each new check write a class inheriting from LocalRequirementCheckStrategy, implementing only the check() method at best, if needed write helper class for in between like e.g. SST_checks
    2. NM: 
        1. write a new case in ReqCheckerNeighbourhood featuring the needed Checks in the Configuration
        2. for each new check write a class inheriting from NeighbourhoodRequirementCheckStrategy, implementing only the check() method at best, if needed write helper class for in between like e.g. SST_helper
