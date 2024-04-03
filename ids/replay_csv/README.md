# Implementation: Input files 

This directory contains different types of input files used for the monitoring. <br><br>

``rtu_1.json, rtu_2.json and border_region_o_1.json``: Topology configuration for the scenarios used within the thesis. rtu_1.json and rtu_2.json contain the topologies of the two subgrids, border_region_0_1.json contains the topology for the border region between the two subgrids. 

<br>

``scenario_x_subgrid_y.csv``: The input file for scenario x and subgrid y. 

<br>

*basic_files directory*: Contains "naked" config files to easier create further topology configuration files. 

<br> 

*results directory*: Contains the output of the monitoring system for each scenario. 
<br>

## Manipulations done for each scenario 


### Scenario 1 
No manipulations were done within the files for scenario 1. All other scenarios re-use the files and manipulated them as mentioned below.  

### Scenario 2

**subgrid 0:** <br>
Line 5: m17v manipulated -> REQ 2L Alert

Line 7: Switch 3 manipulated -> REQ 3L Alert

Line 11: sensor 20 cmanipulated -> REQ 7L Alert

Line 17: sensor 23 v manipulated -> REQ 8L Alert 

**subgrid 1:**<br>
Line 3: m5 v manipulated -> REQ 2L Alert

Line 9: Switch1 manipulated-> REQ 3L Alert

Line 13: sensor 6 c manipulated -> REQ 7L Alert
 
Line 15: sensor 8 v manipulated -> REQ 8L Alert

### Scenario 3

**subgrid 0:** <br>
Line 2: m13 manipulated -> REQ 2L in Monitor 0 + REQ 4N in N0 und N1

**subgrid 1:**<br>
Line 5: m10 manipulated -> REQ 2L in Monitor 1 + REQ 4N in N0 und N1

Line 7:switch 2 manipulated -> REQ 3N in N0 und N1

### Scenario 4

**subgrid 0:** <br>
Line 6: manipulation of m21, m22, m23, m24 voltage, i.e. the complete bus_23 -> Violation of REQ 4N

Copied Line 14 and exchanged Line 15-17 with it 

**subgrid 1:**<br>

Line 3: Switch S2 set to false and the current of m11 was set to 0,0 -> Violation of REQ 3N