import csv
import time
import sys
from mosaikrtu.rtu_model import create_server, create_datablock, load_rtu



class Replay:

    def __init__(self):
        self.server = []
        self.datablocks = []
        self.configs = []
        self.scenario = []

    def load_scenario(self):
        print("Lade Szenario")

        # Konfiguration des Testbeds aus XML lesen
    
        self.configs.append(load_rtu("./data/Coteq/LV_Station_1.xml"))
        self.configs.append(load_rtu("./data/Coteq/MV_Station_1.xml"))
        self.configs.append(load_rtu("./data/Coteq/MV_Station_2.xml"))
        
        #print(self.configs)
        

        # CSV Dateien laden
        # vermutlich möchte ich das so anpassen, dass jede CSV Datei einzeln geladen wird, um da unterschiedliche Sachen auch skippen zu können
        with open("./data/Coteq/LV_Station_1.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            self.scenario.append([])

            # skip header row
            csv_reader.__next__()

            for row in csv_reader:
                self.scenario[0].append(row[3:14]) # ggf. aus 0 noch 2 machen, damit reihenfolge MV1, MV2, LV1 ist 
        
        with open("./data/Coteq/MV_Station_1.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            self.scenario.append([])

            # skip header row
            csv_reader.__next__()

            for row in csv_reader:
                self.scenario[1].append(row[1:12])
        
        with open("./data/Coteq/MV_Station_2.csv", "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            self.scenario.append([])

            # skip header row
            csv_reader.__next__()

            for row in csv_reader:
                self.scenario[2].append(row[1:16])
        


        # Datablock erstellen
        for i in [0, 1, 2]:
            self.datablocks.append(create_datablock(self.configs[i]))

        # Modbus Server erstellen
        for i in [0, 1, 2]:
            self.server.append(create_server(self.configs[i], self.datablocks[i]))

        print("Server erstellt")

    def run_scenario(self, sleeptime):
        print("Szenario wird gestartet")

        # Modbus Server starten
        for i in [0, 1, 2]:
            self.server[i].start()
            print("Started server {}".format(i))


        # Modbus Server (synchron) im 2 Sekundentakt mit den bereits geladenenen Daten aus CSV Datei aktualisieren
        y = 0
        while y < len(self.scenario[0]):
            print("Refreshing datasets")
            # update values
            for i in [0, 1, 2]:
                index_register = 0
                for value in self.scenario[i][y]:
                    if value != "":
                        config_item = list(self.configs[i]['registers'].values())[index_register]

                        # set register
                        self.datablocks[i].set(
                            config_item[0],
                            config_item[1],
                            value,
                            config_item[2],
                        )
                        index_register += 1

            # wait <sleeptime> seconds
            time.sleep(sleeptime)

            # increase "time" aka csv row index
            y += 1

        time.sleep(10)

        print("No more data available, stopping server")

        # Server wieder anhalten
        for i in [0, 1]:
            self.server[i].stop()

        print("Servers stopped")


if __name__ == '__main__':

    print("starting scenario")

    replay = Replay()
    replay.load_scenario() # lädt alle Dateien aus der CSV Datei einmal vor 
    replay.run_scenario(10) # spielt sie ab 

    print("finished scenario.")
    time.sleep(10)
    sys.exit(0)