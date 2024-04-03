import csv
import time
import pprint
import logging
import logging.handlers

# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler())

from mosaikrtu.rtu_model import create_server, create_cache, create_datablock, load_rtu


# TODO: translate comments into english

class Replay:

    def __init__(self):
        self.server = []
        self.datablocks = []
        self.configs = []
        # self.caches = []
        self.scenario_length = 21
        self.scenario = []
        self.amnt_switches = [1, 2]  # TODO: set automatically depending on config
        self.amnt_sensors = [12, 13]  # TODO: set automatically depending on config

    def load_scenario(self, x):
        print("Lade Szenario")

        # Konfiguration des Testbeds aus XML lesen
        for i in [0, 1]:
            self.configs.append(load_rtu("replay_csv/data/new_rtu_{}.xml".format(i)))

        # CSV Dateien laden
        for i in [0, 1]:
            with open("replay_csv/data/scenario_{}_subgrid_{}.csv".format(x, i), "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                self.scenario.append([])

                # skip header row
                csv_reader.__next__()

                # Daten Zeile für Zeile auslesen
                # for j in range(self.scenario_length):
                for row in csv_reader:
                    self.scenario[i].append(row)
                # try:
                #    while 1:
                #        self.scenario[i].append(csv_reader.__next__())
                # except StopIteration:
                #    pass

        # Cache erstellen
        # for i in [0, 1]:
        #    self.caches.append(create_cache(self.configs[i]))

        # Datablock erstellen
        for i in [0, 1]:
            self.datablocks.append(create_datablock(self.configs[i]))

        # Modbus Server erstellen
        for i in [0, 1]:
            self.server.append(create_server(self.configs[i], self.datablocks[i]))

        print("Server erstellt")

    def run_scenario(self, sleeptime):
        print("Szenario wird gestartet")

        # Modbus Server starten
        for i in [0, 1]:
            self.server[i].start()
            # self.server[i].run()
            print("Started server {}".format(i))

        # debug prints
        # for a in range(3):
        #     print("----------------------------- \n")
        # print('configs [%s]' % ', '.join(map(str, self.configs)))
        # for a in range(3):
        #     print("----------------------------- \n")
        # print('scenario [%s]' % ', '.join(map(str, self.scenario)))
        # for a in range(3):
        #     print("----------------------------- \n")

        # Modbus Server (synchron) im 2 Sekundentakt mit Daten aus CSV Datei aktualisieren
        y = 0
        while y < len(self.scenario[0]):
            #print("Refreshing datasets")
            # update values
            for i in [0, 1]:
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

        time.sleep(5)

        print("No more data available, stopping server")

        # Server wieder anhalten
        for i in [0, 1]:
            self.server[i].stop()

        print("Servers stopped")


if __name__ == '__main__':
    for i in [1, 2, 3, 4]:
        for j in [1, 3, 5]:
            print("starting scenario {} mit time {}".format(i, j))

            replay = Replay()
            replay.load_scenario(i)
            replay.run_scenario(j)

            #TODO: aufgenommene Zeiten als csv in die Konsole printen


            print("finished scenario {}".format(i))
            time.sleep(10)


            #csv dateien
            # with open('Salary_Data.csv') as file:
            #     content = file.readlines()
            # header = content[:1]
            # rows = content[1:]
            # print(header)
            # print(rows)
