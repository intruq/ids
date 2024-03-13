import csv 

def load_data_from_csv(file_path):
    data_array = []
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            row_array = []
            for entry in row:
                row_array.append(entry) 
            data_array.append(row_array)
    return data_array


def print_data_one_by_one(data_array):
     for row in data_array:
        date = row[0]
        print("Date:", date)
        for i in range(len(row)-1):       
            print("Values:", row[i+1])
        print()

def communicate_data(time_steps, data_array_M1, data_array_M2, data_array_L1): 
    for i in range(time_steps):
        for j in range(len(data_array_M1[0])):
            print("Values:", data_array_M1[i][j])
            #send(data_array_M1[i])

        for j in range(len(data_array_M2[0])):
            print("Values:", data_array_M2[i][j])
            #send(data_array_M2[i])

        for j in range(len(data_array_L1[0])):
            print("Values:", data_array_L1[i][j])
            #send(data_array_L1[i])

        print("Time step " + str(i) + " communicated.")
        print()


# Path to your CSV file
csv_file_path_M1 = 'data/MV1.csv'
csv_file_path_M2 = 'data/MV2.csv'
csv_file_path_L1 = 'data/LV_Station1.csv'

time_steps = 3

# Load data from CSV file
# data_array = [[[Date],[Value 1], [Value 2]], 
#               [[Date], [Value 1], [Value 2]],
#                ...]
print("Start loading the data from all CSV files.")
data_array_M1 = load_data_from_csv(csv_file_path_M1)
data_array_M2 = load_data_from_csv(csv_file_path_M2)
data_array_L1 = load_data_from_csv(csv_file_path_L1)
print("Loading complete.")

communicate_data(time_steps, data_array_M1, data_array_M2, data_array_L1)

