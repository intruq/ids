
import openpyxl
import numpy
import csv
  
excel = openpyxl.load_workbook("MV_Station2.xlsx")
  
sheet = excel.active
  
col = csv.writer(open("MV2.csv",
                      'w', 
                      newline=""), delimiter=";")


# zugeschnitten auf MV 1 und nur zehner Minuten 
#header_1 = ["Date","V04_IA_L2",'V05_IA_L2', 'V06_IA_L2', 'V09_IA_L2', 'V10_IA_L2', 'V11_IA_L2', 'V12_IA_L2','V14_IA_L2',' V15_IA_L2',  'PQ1_UA_L1' , 'PQ1_UA_L2' , 'PQ1_UA_L3', 'PQ1_PSTA_L1', 'PQ1_PSTA_L2', 'PQ1_PSTA_L3' ] 
header_2 = ["Date", "V01_IA_L2","V02_IA_L2","V03_IA_L2", "V04_IA_L2", "V05_IA_L2", "V06_IA_L2", "V09_IA_L2", "V10_IA_L2", "V11_IA_L2", "V12_IA_L2", "V13_IA_L2", "V14_IA_L2", "PQ1_UA_L1", "PQ1_UA_L2", "PQ1_UA_L3", "PQ1_PSTA_L1", "PQ1_PSTA_L2", "PQ1_PSTA_L3"]
col.writerow(header_2)

#for i in range(0,20000,24):
for i in range(0,20000,30):
	
	rowC = []
	rowC.append(str(sheet[i+2][0].value))

	
	#for row in range(15):
	for row in range(18):
		rowC.append(str(sheet[row+2+i][2].value))

	print(rowC)

	col.writerow(rowC)

	rowC = ""
