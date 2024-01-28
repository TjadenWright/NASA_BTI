# esp32 class
import serial.tools.list_ports
import re
import numpy as np

total_voltage = np.array([0.0, 0.0])
current = np.array([0.0, 0.0])
power = np.array([0.0, 0.0])
charging_power = np.array([0.0, 0.0])
discharging_power = np.array([0.0, 0.0])
capacity_remaining = np.array([0.0, 0.0])
nominal_capacity = np.array([0.0, 0.0])
charging_cycles = np.array([0.0, 0.0])
balancer_status_bitmask = np.array([0.0, 0.0])
errors_bitmask = np.array([0.0, 0.0])
software_version = np.array([0.0, 0.0])
state_of_charge = np.array([0.0, 0.0])
operation_status_bitmask = np.array([0.0, 0.0])
battery_strings = np.array([0.0, 0.0])
temperature_1 = np.array([0.0, 0.0])
temperature_2 = np.array([0.0, 0.0])
temperature_3 = np.array([0.0, 0.0])
cell_voltage_1 = np.array([0.0, 0.0])
cell_voltage_2 = np.array([0.0, 0.0])
cell_voltage_3 = np.array([0.0, 0.0])
cell_voltage_4 = np.array([0.0, 0.0])
cell_voltage_5 = np.array([0.0, 0.0])
cell_voltage_6 = np.array([0.0, 0.0])
cell_voltage_7 = np.array([0.0, 0.0])
cell_voltage_8 = np.array([0.0, 0.0])
cell_voltage_9 = np.array([0.0, 0.0])
cell_voltage_10 = np.array([0.0, 0.0])
cell_voltage_11 = np.array([0.0, 0.0])
cell_voltage_12 = np.array([0.0, 0.0])
cell_voltage_13 = np.array([0.0, 0.0])
cell_voltage_14 = np.array([0.0, 0.0])
cell_voltage_15 = np.array([0.0, 0.0])
cell_voltage_16 = np.array([0.0, 0.0])
min_cell_voltage = np.array([0.0, 0.0])
max_cell_voltage = np.array([0.0, 0.0])
max_voltage_cell = np.array([0.0, 0.0])
min_voltage_cell = np.array([0.0, 0.0])
delta_cell_voltage = np.array([0.0, 0.0])
average_cell_voltage = np.array([0.0, 0.0])

class Battery_class:
    def __init__(self, verbose = False, option = 1, buad_rate=115200):
        self.verbose = verbose
        self.option = option
        self.buad_rate = buad_rate
        # self.total_voltage = 0
        # self.current = 0
        # self.power = 0
        # self.charging_power = 0
        # self.discharging_power = 0
        # self.capacity_remaining = 0
        # self.nominal_capacity = 0
        # self.charging_cycles = 0
        # self.balancer_status_bitmask = 0
        # self.errors_bitmask = 0
        # self.software_version = 0
        # self.state_of_charge = 0
        # self.operation_status_bitmask = 0
        # self.battery_strings = 0
        # self.temperature_1 = 0
        # self.temperature_2 = 0
        # self.temperature_3 = 0
        # self.cell_voltage_1 = 0
        # self.cell_voltage_2 = 0
        # self.cell_voltage_3 = 0
        # self.cell_voltage_4 = 0
        # self.cell_voltage_5 = 0
        # self.cell_voltage_6 = 0
        # self.cell_voltage_7 = 0
        # self.cell_voltage_8 = 0
        # self.cell_voltage_9 = 0
        # self.cell_voltage_10 = 0
        # self.cell_voltage_11 = 0
        # self.cell_voltage_12 = 0
        # self.cell_voltage_13 = 0
        # self.cell_voltage_14 = 0
        # self.cell_voltage_15 = 0
        # self.cell_voltage_16 = 0
        # self.min_cell_voltage = 0
        # self.max_cell_voltage = 0
        # self.max_voltage_cell = 0
        # self.min_voltage_cell = 0
        # self.delta_cell_voltage = 0
        # self.average_cell_voltage = 0

    def get_esp32(self):
        esp32_port = None
        count = 1         # start out at count 1
        ports = serial.tools.list_ports.comports() # get a list of the ports
        for port in ports: # look through all the ports for an esp32
            if 'Silicon Labs CP210x' in port.description:  # Adjust the description as needed
                if(count == self.option):
                    esp32_port = port.device # if you find an esp32 then you're good to go.
                    break
                else:
                    count+=1 # increment count till we find the esp32
        # error message
        if esp32_port is None:
            print("ESP32 not found. Check the connection or adjust the description.")
            exit(1)
        else:
            print(port)

        return esp32_port # return the port to be used in serial comms
 
    def enable_read(self):
        esp32_port = self.get_esp32()

        self.arduinoData = serial.Serial(esp32_port, 115200)

        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
        dataPacket=self.arduinoData.readline() 
    
    def read_esp32(self):

        while(self.arduinoData.inWaiting()==0): # wait for data
            pass

        dataPacket=self.arduinoData.readline()                         # read the data from the arduino
        self.dataPacket = dataPacket.decode('utf-8').rstrip()                    # convert the bytes to a str
        # print(self.dataPacket)

    def disable_read(self):
        self.arduinoData.close()


    def parse_data(self):
        # Regular expression to extract data
        pattern = re.compile(r"'jbd-bms-ble bms(\d+) (.*?)': Sending state (\d+\.\d+)")

        for line in self.dataPacket.split('\n'):
            match = pattern.search(line)
            if match:
                # print(match.group(1), match.group(2), match.group(3))
                index = int(match.group(1))
                key = match.group(2)
                key = key.replace(' ', '_')  # Replace spaces with underscores
                value = float(match.group(3))
                globals()[key][index] = value

        # # Iterate through each line in the data
        # for line in self.dataPacket.split('\n'):
        #     match = pattern.search(line)
        #     if match:
        #         key = match.group(1)
        #         key = key.replace(' ', '_')  # Replace spaces with underscores
        #         value = float(match.group(2))
        #         globals()[key] = value
        
        
        return total_voltage, current, power, charging_power, discharging_power, capacity_remaining, nominal_capacity, charging_cycles, balancer_status_bitmask, errors_bitmask, software_version, state_of_charge, operation_status_bitmask, battery_strings, temperature_1, temperature_2, temperature_3, cell_voltage_1, cell_voltage_2, cell_voltage_3, cell_voltage_4, cell_voltage_5, cell_voltage_6, cell_voltage_7, cell_voltage_8, cell_voltage_9, cell_voltage_10, cell_voltage_11, cell_voltage_12, cell_voltage_13, cell_voltage_14, cell_voltage_15, cell_voltage_16, min_cell_voltage, max_cell_voltage, max_voltage_cell, min_voltage_cell, delta_cell_voltage, average_cell_voltage

    def parse_data_test(self):
        self.test_input()
        # Regular expression to extract data
        pattern = re.compile(r"'jbd-bms-ble (.*?)': Sending state (\d+\.\d+)")

        # Iterate through each line in the data
        for line in self.data.split('\n'):
            match = pattern.search(line)
            if match:
                key = match.group(1)
                key = key.replace(' ', '_')  # Replace spaces with underscores
                # key = "self." + key
                value = float(match.group(2))
                globals()[key] = value
        
        # Print the values of the variables
        # print(f"Total Voltage: {self.total_voltage}")
        # print(f"Current: {self.current}")
        # print(f"Power: {self.power}")
        # print(f"Charging Power: {self.charging_power}")
        # print(f"Discharging Power: {self.discharging_power}")
        # print(f"Capacity Remaining: {self.capacity_remaining}")
        # print(f"Nominal Capacity: {self.nominal_capacity}")
        # print(f"Charging Cycles: {self.charging_cycles}")
        # print(f"Balancer Status Bitmask: {self.balancer_status_bitmask}")
        # print(f"Errors Bitmask: {self.errors_bitmask}")
        # print(f"Software Version: {self.software_version}")
        # print(f"State of Charge: {self.state_of_charge}")
        # print(f"Operation Status Bitmask: {self.operation_status_bitmask}")
        # print(f"Battery Strings: {self.battery_strings}")
        # print(f"Temperature 1: {self.temperature_1}")
        # print(f"Temperature 2: {self.temperature_2}")
        # print(f"Temperature 3: {self.temperature_3}")
        # print(f"Cell Voltage 1: {self.cell_voltage_1}")
        # print(f"Cell Voltage 2: {self.cell_voltage_2}")
        # print(f"Cell Voltage 3: {self.cell_voltage_3}")
        # print(f"Cell Voltage 4: {self.cell_voltage_4}")
        # print(f"Cell Voltage 5: {self.cell_voltage_5}")
        # print(f"Cell Voltage 6: {self.cell_voltage_6}")
        # print(f"Cell Voltage 7: {self.cell_voltage_7}")
        # print(f"Cell Voltage 8: {self.cell_voltage_8}")
        # print(f"Cell Voltage 9: {self.cell_voltage_9}")
        # print(f"Cell Voltage 10: {self.cell_voltage_10}")
        # print(f"Cell Voltage 11: {self.cell_voltage_11}")
        # print(f"Cell Voltage 12: {self.cell_voltage_12}")
        # print(f"Cell Voltage 13: {self.cell_voltage_13}")
        # print(f"Cell Voltage 14: {self.cell_voltage_14}")
        # print(f"Cell Voltage 15: {self.cell_voltage_15}")
        # print(f"Cell Voltage 16: {self.cell_voltage_16}")
        # print(f"Min Cell Voltage: {self.min_cell_voltage}")
        # print(f"Max Cell Voltage: {self.max_cell_voltage}")
        # print(f"Max Voltage Cell: {self.max_voltage_cell}")
        # print(f"Min Voltage Cell: {self.min_voltage_cell}")
        # print(f"Delta Cell Voltage: {self.delta_cell_voltage}")
        # print(f"Average Cell Voltage: {self.average_cell_voltage}")

        # # Print the values of the variables
        # print(f"Total Voltage: {total_voltage}")
        # print(f"Current: {current}")
        # print(f"Power: {power}")
        # print(f"Charging Power: {charging_power}")
        # print(f"Discharging Power: {discharging_power}")
        # print(f"Capacity Remaining: {capacity_remaining}")
        # print(f"Nominal Capacity: {nominal_capacity}")
        # print(f"Charging Cycles: {charging_cycles}")
        # print(f"Balancer Status Bitmask: {balancer_status_bitmask}")
        # print(f"Errors Bitmask: {errors_bitmask}")
        # print(f"Software Version: {software_version}")
        # print(f"State of Charge: {state_of_charge}")
        # print(f"Operation Status Bitmask: {operation_status_bitmask}")
        # print(f"Battery Strings: {battery_strings}")
        # print(f"Temperature 1: {temperature_1}")
        # print(f"Temperature 2: {temperature_2}")
        # print(f"Temperature 3: {temperature_3}")
        # print(f"Cell Voltage 1: {cell_voltage_1}")
        # print(f"Cell Voltage 2: {cell_voltage_2}")
        # print(f"Cell Voltage 3: {cell_voltage_3}")
        # print(f"Cell Voltage 4: {cell_voltage_4}")
        # print(f"Cell Voltage 5: {cell_voltage_5}")
        # print(f"Cell Voltage 6: {cell_voltage_6}")
        # print(f"Cell Voltage 7: {cell_voltage_7}")
        # print(f"Cell Voltage 8: {cell_voltage_8}")
        # print(f"Cell Voltage 9: {cell_voltage_9}")
        # print(f"Cell Voltage 10: {cell_voltage_10}")
        # print(f"Cell Voltage 11: {cell_voltage_11}")
        # print(f"Cell Voltage 12: {cell_voltage_12}")
        # print(f"Cell Voltage 13: {cell_voltage_13}")
        # print(f"Cell Voltage 14: {cell_voltage_14}")
        # print(f"Cell Voltage 15: {cell_voltage_15}")
        # print(f"Cell Voltage 16: {cell_voltage_16}")
        # print(f"Min Cell Voltage: {min_cell_voltage}")
        # print(f"Max Cell Voltage: {max_cell_voltage}")
        # print(f"Max Voltage Cell: {max_voltage_cell}")
        # print(f"Min Voltage Cell: {min_voltage_cell}")
        # print(f"Delta Cell Voltage: {delta_cell_voltage}")
        # print(f"Average Cell Voltage: {average_cell_voltage}")

        return total_voltage, current, power, charging_power, discharging_power, capacity_remaining, nominal_capacity, charging_cycles, balancer_status_bitmask, errors_bitmask, software_version, state_of_charge, operation_status_bitmask, battery_strings, temperature_1, temperature_2, temperature_3, cell_voltage_1, cell_voltage_2, cell_voltage_3, cell_voltage_4, cell_voltage_5, cell_voltage_6, cell_voltage_7, cell_voltage_8, cell_voltage_9, cell_voltage_10, cell_voltage_11, cell_voltage_12, cell_voltage_13, cell_voltage_14, cell_voltage_15, cell_voltage_16, min_cell_voltage, max_cell_voltage, max_voltage_cell, min_voltage_cell, delta_cell_voltage, average_cell_voltage

    def test_input(self):
        self.data = """
        [15:26:55][I][app:102]: ESPHome version 2023.10.3 compiled on Oct 30 2023, 15:13:37
        [15:26:55][I][app:104]: Project syssi.esphome-jbd-bms version 1.5.0
        [15:26:55][C][logger:416]: Logger:
        [15:26:55][C][logger:417]:   Level: DEBUG
        [15:26:55][C][logger:418]:   Log Baud Rate: 115200
        [15:26:55][C][logger:420]:   Hardware UART: UART0
        [15:26:55][D][switch:055]: 'jbd-bms-ble enable bluetooth connection': Sending state ON
        [15:26:55][C][jbd_bms_ble:399]: JbdBmsBle:
        [15:26:55][C][jbd_bms_ble:400]:   Fake traffic enabled: NO
        [15:26:55][C][jbd_bms_ble:402]: Balancing 'jbd-bms-ble balancing'
        [15:26:55][C][jbd_bms_ble:403]: Charging 'jbd-bms-ble charging'
        [15:26:55][C][jbd_bms_ble:404]: Discharging 'jbd-bms-ble discharging'
        [15:26:55][C][jbd_bms_ble:406]: Total voltage 'jbd-bms-ble total voltage'
        [15:26:55][C][jbd_bms_ble:406]:   Device Class: 'voltage'
        [15:26:55][C][jbd_bms_ble:406]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:406]:   Unit of Measurement: 'V'
        [15:26:55][C][jbd_bms_ble:406]:   Accuracy Decimals: 2
        [15:26:55][C][jbd_bms_ble:407]: Battery strings 'jbd-bms-ble battery strings'
        [15:26:55][C][jbd_bms_ble:407]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:407]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:407]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:407]:   Icon: 'mdi:car-battery'
        [15:26:55][C][jbd_bms_ble:408]: Software version 'jbd-bms-ble software version'
        [15:26:55][C][jbd_bms_ble:408]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:408]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:408]:   Accuracy Decimals: 1
        [15:26:55][C][jbd_bms_ble:408]:   Icon: 'mdi:numeric'
        [15:26:55][C][jbd_bms_ble:409]: Current 'jbd-bms-ble current'
        [15:26:55][C][jbd_bms_ble:409]:   Device Class: 'current'
        [15:26:55][C][jbd_bms_ble:409]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:409]:   Unit of Measurement: 'A'
        [15:26:55][C][jbd_bms_ble:409]:   Accuracy Decimals: 1
        [15:26:55][C][jbd_bms_ble:409]:   Icon: 'mdi:current-dc'
        [15:26:55][C][jbd_bms_ble:410]: Power 'jbd-bms-ble power'
        [15:26:55][C][jbd_bms_ble:410]:   Device Class: 'power'
        [15:26:55][C][jbd_bms_ble:410]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:410]:   Unit of Measurement: 'W'
        [15:26:55][C][jbd_bms_ble:410]:   Accuracy Decimals: 1
        [15:26:55][C][jbd_bms_ble:411]: Charging Power 'jbd-bms-ble charging power'
        [15:26:55][C][jbd_bms_ble:411]:   Device Class: 'power'
        [15:26:55][C][jbd_bms_ble:411]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:411]:   Unit of Measurement: 'W'
        [15:26:55][C][jbd_bms_ble:411]:   Accuracy Decimals: 2
        [15:26:55][C][jbd_bms_ble:412]: Discharging Power 'jbd-bms-ble discharging power'
        [15:26:55][C][jbd_bms_ble:412]:   Device Class: 'power'
        [15:26:55][C][jbd_bms_ble:412]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:412]:   Unit of Measurement: 'W'
        [15:26:55][C][jbd_bms_ble:412]:   Accuracy Decimals: 2
        [15:26:55][C][jbd_bms_ble:413]: State of charge 'jbd-bms-ble state of charge'
        [15:26:55][C][jbd_bms_ble:413]:   Device Class: 'battery'
        [15:26:55][C][jbd_bms_ble:413]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:413]:   Unit of Measurement: '%'
        [15:26:55][C][jbd_bms_ble:413]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:414]: Operation status bitmask 'jbd-bms-ble operation status bitmask'
        [15:26:55][C][jbd_bms_ble:414]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:414]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:414]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:414]:   Icon: 'mdi:heart-pulse'
        [15:26:55][C][jbd_bms_ble:415]: Errors bitmask 'jbd-bms-ble errors bitmask'
        [15:26:55][C][jbd_bms_ble:415]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:415]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:415]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:415]:   Icon: 'mdi:alert-circle-outline'
        [15:26:55][C][jbd_bms_ble:416]: Nominal capacity 'jbd-bms-ble nominal capacity'
        [15:26:55][C][jbd_bms_ble:416]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:416]:   Unit of Measurement: 'Ah'
        [15:26:55][C][jbd_bms_ble:416]:   Accuracy Decimals: 2
        [15:26:55][C][jbd_bms_ble:416]:   Icon: 'mdi:battery-50'
        [15:26:55][C][jbd_bms_ble:417]: Charging cycles 'jbd-bms-ble charging cycles'
        [15:26:55][C][jbd_bms_ble:417]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:417]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:417]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:417]:   Icon: 'mdi:battery-sync'
        [15:26:55][C][jbd_bms_ble:418]: Balancer status bitmask 'jbd-bms-ble balancer status bitmask'
        [15:26:55][C][jbd_bms_ble:418]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:418]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:418]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:418]:   Icon: 'mdi:seesaw'
        [15:26:55][C][jbd_bms_ble:419]: Capacity remaining 'jbd-bms-ble capacity remaining'
        [15:26:55][C][jbd_bms_ble:419]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:419]:   Unit of Measurement: 'Ah'
        [15:26:55][C][jbd_bms_ble:419]:   Accuracy Decimals: 2
        [15:26:55][C][jbd_bms_ble:419]:   Icon: 'mdi:battery-50'
        [15:26:55][C][jbd_bms_ble:420]: Average cell voltage sensor 'jbd-bms-ble average cell voltage'
        [15:26:55][C][jbd_bms_ble:420]:   Device Class: 'voltage'
        [15:26:55][C][jbd_bms_ble:420]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:420]:   Unit of Measurement: 'V'
        [15:26:55][C][jbd_bms_ble:420]:   Accuracy Decimals: 4
        [15:26:55][C][jbd_bms_ble:421]: Delta cell voltage sensor 'jbd-bms-ble delta cell voltage'
        [15:26:55][C][jbd_bms_ble:421]:   Device Class: 'voltage'
        [15:26:55][C][jbd_bms_ble:421]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:421]:   Unit of Measurement: 'V'
        [15:26:55][C][jbd_bms_ble:421]:   Accuracy Decimals: 4
        [15:26:55][C][jbd_bms_ble:422]: Maximum cell voltage 'jbd-bms-ble max cell voltage'
        [15:26:55][C][jbd_bms_ble:422]:   Device Class: 'voltage'
        [15:26:55][C][jbd_bms_ble:422]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:422]:   Unit of Measurement: 'V'
        [15:26:55][C][jbd_bms_ble:422]:   Accuracy Decimals: 3
        [15:26:55][C][jbd_bms_ble:422]:   Icon: 'mdi:battery-plus-outline'
        [15:26:55][C][jbd_bms_ble:423]: Min voltage cell 'jbd-bms-ble min voltage cell'
        [15:26:55][C][jbd_bms_ble:423]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:423]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:423]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:423]:   Icon: 'mdi:battery-minus-outline'
        [15:26:55][C][jbd_bms_ble:424]: Max voltage cell 'jbd-bms-ble max voltage cell'
        [15:26:55][C][jbd_bms_ble:424]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:424]:   Unit of Measurement: ''
        [15:26:55][C][jbd_bms_ble:424]:   Accuracy Decimals: 0
        [15:26:55][C][jbd_bms_ble:424]:   Icon: 'mdi:battery-plus-outline'
        [15:26:55][C][jbd_bms_ble:425]: Minimum cell voltage 'jbd-bms-ble min cell voltage'
        [15:26:55][C][jbd_bms_ble:425]:   Device Class: 'voltage'
        [15:26:55][C][jbd_bms_ble:425]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:425]:   Unit of Measurement: 'V'
        [15:26:55][C][jbd_bms_ble:425]:   Accuracy Decimals: 3
        [15:26:55][C][jbd_bms_ble:425]:   Icon: 'mdi:battery-minus-outline'
        [15:26:55][C][jbd_bms_ble:427]: Temperature 1 'jbd-bms-ble temperature 1'
        [15:26:55][C][jbd_bms_ble:427]:   Device Class: 'temperature'
        [15:26:55][C][jbd_bms_ble:427]:   State Class: 'measurement'
        [15:26:55][C][jbd_bms_ble:427]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:427]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:428]: Temperature 2 'jbd-bms-ble temperature 2'
        [15:26:56][C][jbd_bms_ble:428]:   Device Class: 'temperature'
        [15:26:56][C][jbd_bms_ble:428]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:428]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:428]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:429]: Temperature 3 'jbd-bms-ble temperature 3'
        [15:26:56][C][jbd_bms_ble:429]:   Device Class: 'temperature'
        [15:26:56][C][jbd_bms_ble:429]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:429]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:429]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:430]: Temperature 4 'jbd-bms-ble temperature 4'
        [15:26:56][C][jbd_bms_ble:430]:   Device Class: 'temperature'
        [15:26:56][C][jbd_bms_ble:430]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:430]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:430]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:431]: Temperature 5 'jbd-bms-ble temperature 5'
        [15:26:56][C][jbd_bms_ble:431]:   Device Class: 'temperature'
        [15:26:56][C][jbd_bms_ble:431]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:431]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:431]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:432]: Temperature 6 'jbd-bms-ble temperature 6'
        [15:26:56][C][jbd_bms_ble:432]:   Device Class: 'temperature'
        [15:26:56][C][jbd_bms_ble:432]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:432]:   Unit of Measurement: '°C'
        [15:26:56][C][jbd_bms_ble:432]:   Accuracy Decimals: 1
        [15:26:56][C][jbd_bms_ble:433]: Cell Voltage 1 'jbd-bms-ble cell voltage 1'
        [15:26:56][C][jbd_bms_ble:433]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:433]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:433]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:433]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:434]: Cell Voltage 2 'jbd-bms-ble cell voltage 2'
        [15:26:56][C][jbd_bms_ble:434]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:434]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:434]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:434]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:435]: Cell Voltage 3 'jbd-bms-ble cell voltage 3'
        [15:26:56][C][jbd_bms_ble:435]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:435]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:435]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:435]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:436]: Cell Voltage 4 'jbd-bms-ble cell voltage 4'
        [15:26:56][C][jbd_bms_ble:436]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:436]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:436]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:436]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:437]: Cell Voltage 5 'jbd-bms-ble cell voltage 5'
        [15:26:56][C][jbd_bms_ble:437]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:437]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:437]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:437]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:438]: Cell Voltage 6 'jbd-bms-ble cell voltage 6'
        [15:26:56][C][jbd_bms_ble:438]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:438]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:438]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:438]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:439]: Cell Voltage 7 'jbd-bms-ble cell voltage 7'
        [15:26:56][C][jbd_bms_ble:439]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:439]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:439]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:439]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:440]: Cell Voltage 8 'jbd-bms-ble cell voltage 8'
        [15:26:56][C][jbd_bms_ble:440]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:440]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:440]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:440]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:441]: Cell Voltage 9 'jbd-bms-ble cell voltage 9'
        [15:26:56][C][jbd_bms_ble:441]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:441]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:441]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:441]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:442]: Cell Voltage 10 'jbd-bms-ble cell voltage 10'
        [15:26:56][C][jbd_bms_ble:442]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:442]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:442]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:442]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:443]: Cell Voltage 11 'jbd-bms-ble cell voltage 11'
        [15:26:56][C][jbd_bms_ble:443]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:443]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:443]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:443]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:444]: Cell Voltage 12 'jbd-bms-ble cell voltage 12'
        [15:26:56][C][jbd_bms_ble:444]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:444]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:444]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:444]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:445]: Cell Voltage 13 'jbd-bms-ble cell voltage 13'
        [15:26:56][C][jbd_bms_ble:445]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:445]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:445]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:445]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:446]: Cell Voltage 14 'jbd-bms-ble cell voltage 14'
        [15:26:56][C][jbd_bms_ble:446]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:446]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:446]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:446]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:447]: Cell Voltage 15 'jbd-bms-ble cell voltage 15'
        [15:26:56][C][jbd_bms_ble:447]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:447]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:447]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:447]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:448]: Cell Voltage 16 'jbd-bms-ble cell voltage 16'
        [15:26:56][C][jbd_bms_ble:448]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:448]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:448]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:448]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:449]: Cell Voltage 17 'jbd-bms-ble cell voltage 17'
        [15:26:56][C][jbd_bms_ble:449]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:449]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:449]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:449]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:450]: Cell Voltage 18 'jbd-bms-ble cell voltage 18'
        [15:26:56][C][jbd_bms_ble:450]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:450]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:450]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:450]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:451]: Cell Voltage 19 'jbd-bms-ble cell voltage 19'
        [15:26:56][C][jbd_bms_ble:451]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:451]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:451]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:451]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:452]: Cell Voltage 20 'jbd-bms-ble cell voltage 20'
        [15:26:56][C][jbd_bms_ble:452]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:452]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:452]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:452]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:453]: Cell Voltage 21 'jbd-bms-ble cell voltage 21'
        [15:26:56][C][jbd_bms_ble:453]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:453]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:453]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:453]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:454]: Cell Voltage 22 'jbd-bms-ble cell voltage 22'
        [15:26:56][C][jbd_bms_ble:454]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:454]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:454]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:454]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:455]: Cell Voltage 23 'jbd-bms-ble cell voltage 23'
        [15:26:56][C][jbd_bms_ble:455]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:455]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:455]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:455]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:456]: Cell Voltage 24 'jbd-bms-ble cell voltage 24'
        [15:26:56][C][jbd_bms_ble:456]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:456]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:456]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:456]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:457]: Cell Voltage 25 'jbd-bms-ble cell voltage 25'
        [15:26:56][C][jbd_bms_ble:457]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:457]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:457]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:457]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:458]: Cell Voltage 26 'jbd-bms-ble cell voltage 26'
        [15:26:56][C][jbd_bms_ble:458]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:458]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:458]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:458]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:459]: Cell Voltage 27 'jbd-bms-ble cell voltage 27'
        [15:26:56][C][jbd_bms_ble:459]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:459]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:459]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:459]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:460]: Cell Voltage 28 'jbd-bms-ble cell voltage 28'
        [15:26:56][C][jbd_bms_ble:460]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:460]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:460]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:460]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:461]: Cell Voltage 29 'jbd-bms-ble cell voltage 29'
        [15:26:56][C][jbd_bms_ble:461]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:461]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:461]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:461]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:462]: Cell Voltage 30 'jbd-bms-ble cell voltage 30'
        [15:26:56][C][jbd_bms_ble:462]:   Device Class: 'voltage'
        [15:26:56][C][jbd_bms_ble:462]:   State Class: 'measurement'
        [15:26:56][C][jbd_bms_ble:462]:   Unit of Measurement: 'V'
        [15:26:56][C][jbd_bms_ble:462]:   Accuracy Decimals: 3
        [15:26:56][C][jbd_bms_ble:463]: Cell Voltage 31 'jbd-bms-ble cell voltage 31'
        [15:26:56][C][jbd_bms_ble:463]:   Device Class: 'voltage'
        [15:26:57][C][jbd_bms_ble:463]:   State Class: 'measurement'
        [15:26:57][C][jbd_bms_ble:463]:   Unit of Measurement: 'V'
        [15:26:57][C][jbd_bms_ble:463]:   Accuracy Decimals: 3
        [15:26:57][C][jbd_bms_ble:464]: Cell Voltage 32 'jbd-bms-ble cell voltage 32'
        [15:26:57][C][jbd_bms_ble:464]:   Device Class: 'voltage'
        [15:26:57][C][jbd_bms_ble:464]:   State Class: 'measurement'
        [15:26:57][C][jbd_bms_ble:464]:   Unit of Measurement: 'V'
        [15:26:57][C][jbd_bms_ble:464]:   Accuracy Decimals: 3
        [15:26:57][C][jbd_bms_ble:466]: Operation status 'jbd-bms-ble operation status'
        [15:26:57][C][jbd_bms_ble:466]:   Icon: 'mdi:heart-pulse'
        [15:26:57][C][jbd_bms_ble:467]: Errors 'jbd-bms-ble errors'
        [15:26:57][C][jbd_bms_ble:467]:   Icon: 'mdi:alert-circle-outline'
        [15:26:57][C][jbd_bms_ble:468]: Device model 'jbd-bms-ble device model'
        [15:26:57][C][jbd_bms_ble:468]:   Icon: 'mdi:chip'
        [15:26:57][W][jbd_bms_ble:175]: [70:3E:97:07:A9:83] Not connected
        [15:26:57][W][esp32_ble_tracker:108]: Too many BLE events to process. Some devices may not show up.
        [15:26:57][C][ble_switch:068]: BLE Client Switch 'jbd-bms-ble enable bluetooth connection'
        [15:26:57][C][ble_switch:070]:   Icon: 'mdi:bluetooth'
        [15:26:57][C][ble_switch:091]:   Restore Mode: always OFF
        [15:26:57][C][jbd_bms_ble.switch:068]: JbdBmsBle Switch 'jbd-bms-ble discharging'
        [15:26:57][C][jbd_bms_ble.switch:070]:   Icon: 'mdi:battery-charging-50'
        [15:26:57][C][jbd_bms_ble.switch:091]:   Restore Mode: always OFF
        [15:26:57][C][jbd_bms_ble.switch:068]: JbdBmsBle Switch 'jbd-bms-ble charging'
        [15:26:57][C][jbd_bms_ble.switch:070]:   Icon: 'mdi:battery-charging-50'
        [15:26:57][C][jbd_bms_ble.switch:091]:   Restore Mode: always OFF
        [15:26:57][C][esp32_ble:238]: ESP32 BLE:
        [15:26:57][C][esp32_ble:240]:   MAC address: EC:62:60:F0:47:8E
        [15:26:57][C][esp32_ble:241]:   IO Capability: none
        [15:26:57][C][esp32_ble_tracker:617]: BLE Tracker:
        [15:26:57][C][esp32_ble_tracker:618]:   Scan Duration: 300 s
        [15:26:57][C][esp32_ble_tracker:619]:   Scan Interval: 320.0 ms
        [15:26:57][C][esp32_ble_tracker:620]:   Scan Window: 30.0 ms
        [15:26:57][C][esp32_ble_tracker:621]:   Scan Type: ACTIVE
        [15:26:57][C][esp32_ble_tracker:622]:   Continuous Scanning: True
        [15:26:57][C][ble_client:027]: BLE Client:
        [15:26:57][C][ble_client:028]:   Address: 70:3E:97:07:A9:83
        [15:26:58][W][jbd_bms_ble:175]: [70:3E:97:07:A9:83] Not connected
        [15:27:00][W][jbd_bms_ble:175]: [70:3E:97:07:A9:83] Not connected
        [15:27:01][D][esp32_ble_client:048]: [0] [70:3E:97:07:A9:83] Found device
        [15:27:01][D][esp32_ble_tracker:214]: Pausing scan to make connection...
        [15:27:01][I][esp32_ble_client:064]: [0] [70:3E:97:07:A9:83] 0x00 Attempting BLE connection
        [15:27:02][I][esp32_ble_client:196]: [0] [70:3E:97:07:A9:83] Connected
        [15:27:02][D][esp32_ble_tracker:246]: Starting scan...
        [15:27:02][I][jbd_bms_ble:093]: Request device info
        [15:27:04][D][binary_sensor:036]: 'jbd-bms-ble online status': Sending state ON
        [15:27:04][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:04][D][jbd_bms_ble:263]:   Device model:
        [15:27:04][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:04][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:04][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:04][D][binary_sensor:036]: 'jbd-bms-ble balancing': Sending state OFF
        [15:27:04][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:04][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:04][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:04][D][binary_sensor:036]: 'jbd-bms-ble charging': Sending state OFF
        [15:27:04][D][switch:055]: 'jbd-bms-ble charging': Sending state OFF
        [15:27:04][D][binary_sensor:036]: 'jbd-bms-ble discharging': Sending state OFF
        [15:27:04][D][switch:055]: 'jbd-bms-ble discharging': Sending state OFF
        [15:27:04][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:04][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:04][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:04][W][component:215]: Components should block for at most 20-30ms.
        [15:27:05][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:05][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:05][W][component:214]: Component esp32_ble took a long time for an operation (0.18 s).
        [15:27:05][W][component:215]: Components should block for at most 20-30ms.
        [15:27:06][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:06][D][jbd_bms_ble:263]:   Device model:
        [15:27:06][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:06][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:06][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:06][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:06][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.60000 °C with 1 decimals of accuracy
        [15:27:06][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:06][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:06][W][component:215]: Components should block for at most 20-30ms.
        [15:27:07][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:07][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:07][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:07][W][component:215]: Components should block for at most 20-30ms.
        [15:27:08][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:08][D][jbd_bms_ble:263]:   Device model:
        [15:27:08][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:08][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:08][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:08][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:08][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:08][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:08][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:08][W][component:215]: Components should block for at most 20-30ms.
        [15:27:09][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:09][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:09][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:09][W][component:215]: Components should block for at most 20-30ms.
        [15:27:10][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:10][D][jbd_bms_ble:263]:   Device model:
        [15:27:10][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:10][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:10][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:10][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:10][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:10][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:10][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:10][W][component:215]: Components should block for at most 20-30ms.
        [15:27:11][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:11][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:11][W][component:214]: Component esp32_ble took a long time for an operation (0.18 s).
        [15:27:11][W][component:215]: Components should block for at most 20-30ms.
        [15:27:12][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:12][D][jbd_bms_ble:263]:   Device model:
        [15:27:12][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:12][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:12][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:12][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:12][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.10000 °C with 1 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.60000 °C with 1 decimals of accuracy
        [15:27:12][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:12][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:12][W][component:215]: Components should block for at most 20-30ms.
        [15:27:13][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:13][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:13][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:13][W][component:215]: Components should block for at most 20-30ms.
        [15:27:14][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:14][D][jbd_bms_ble:263]:   Device model:
        [15:27:14][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:14][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:14][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:14][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:14][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:14][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:14][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:14][W][component:215]: Components should block for at most 20-30ms.
        [15:27:15][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:15][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:15][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:15][W][component:215]: Components should block for at most 20-30ms.
        [15:27:16][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:16][D][jbd_bms_ble:263]:   Device model:
        [15:27:16][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:16][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:16][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:16][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:16][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:16][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:16][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:16][W][component:215]: Components should block for at most 20-30ms.
        [15:27:17][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:17][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28900 V with 4 decimals of accuracy
        [15:27:17][W][component:214]: Component esp32_ble took a long time for an operation (0.18 s).
        [15:27:17][W][component:215]: Components should block for at most 20-30ms.
        [15:27:18][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:18][D][jbd_bms_ble:263]:   Device model:
        [15:27:18][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:18][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:18][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:18][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:18][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:18][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:18][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:18][W][component:215]: Components should block for at most 20-30ms.
        [15:27:19][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:19][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:19][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:19][W][component:215]: Components should block for at most 20-30ms.
        [15:27:20][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:20][D][jbd_bms_ble:263]:   Device model:
        [15:27:20][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:20][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:20][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:20][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:20][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:20][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:20][W][component:215]: Components should block for at most 20-30ms.
        [15:27:20][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:20][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:21][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:21][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:21][W][component:215]: Components should block for at most 20-30ms.
        [15:27:22][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:22][D][jbd_bms_ble:263]:   Device model:
        [15:27:22][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:22][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:22][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:22][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:22][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.10000 °C with 1 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.60000 °C with 1 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:22][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:22][W][component:215]: Components should block for at most 20-30ms.
        [15:27:22][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:22][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:22][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:23][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:23][W][component:214]: Component esp32_ble took a long time for an operation (0.18 s).
        [15:27:23][W][component:215]: Components should block for at most 20-30ms.
        [15:27:24][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:24][D][jbd_bms_ble:263]:   Device model:
        [15:27:24][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:24][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:24][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:24][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:24][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:24][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:24][W][component:215]: Components should block for at most 20-30ms.
        [15:27:24][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:24][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:24][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:25][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:25][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:25][W][component:215]: Components should block for at most 20-30ms.
        [15:27:26][I][jbd_bms_ble:260]: Hardware info frame (38 bytes) received
        [15:27:26][D][jbd_bms_ble:263]:   Device model:
        [15:27:26][D][sensor:094]: 'jbd-bms-ble total voltage': Sending state 52.62000 V with 2 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble current': Sending state 0.00000 A with 1 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble power': Sending state 0.00000 W with 1 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble charging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble discharging power': Sending state 0.00000 W with 2 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble capacity remaining': Sending state 38.99000 Ah with 2 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble nominal capacity': Sending state 100.00000 Ah with 2 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble charging cycles': Sending state 1.00000  with 0 decimals of accuracy
        [15:27:26][D][jbd_bms_ble:290]:   Date of manufacture: 2022.9.24
        [15:27:26][D][sensor:094]: 'jbd-bms-ble balancer status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble errors bitmask': Sending state 4096.00000  with 0 decimals of accuracy
        [15:27:26][D][text_sensor:064]: 'jbd-bms-ble errors': Sending state 'Mosfet Software Lock'
        [15:27:26][D][sensor:094]: 'jbd-bms-ble software version': Sending state 4.40000  with 1 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble state of charge': Sending state 39.00000 % with 0 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble operation status bitmask': Sending state 0.00000  with 0 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble battery strings': Sending state 16.00000  with 0 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble temperature 1': Sending state 20.00000 °C with 1 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble temperature 2': Sending state 18.70000 °C with 1 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble temperature 3': Sending state 18.80000 °C with 1 decimals of accuracy
        [15:27:26][W][component:214]: Component esp32_ble took a long time for an operation (0.16 s).
        [15:27:26][W][component:215]: Components should block for at most 20-30ms.
        [15:27:26][I][jbd_bms_ble:209]: Cell info frame (32 bytes) received
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 1': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 2': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 3': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 4': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 5': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 6': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 7': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:26][D][sensor:094]: 'jbd-bms-ble cell voltage 8': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 9': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 10': Sending state 3.28700 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 11': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 12': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 13': Sending state 3.29000 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 14': Sending state 3.28800 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 15': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble cell voltage 16': Sending state 3.28900 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble min cell voltage': Sending state 3.28600 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble max cell voltage': Sending state 3.29400 V with 3 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble max voltage cell': Sending state 12.00000  with 0 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble min voltage cell': Sending state 15.00000  with 0 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble delta cell voltage': Sending state 0.00800 V with 4 decimals of accuracy
        [15:27:27][D][sensor:094]: 'jbd-bms-ble average cell voltage': Sending state 3.28913 V with 4 decimals of accuracy
        [15:27:27][W][component:214]: Component esp32_ble took a long time for an operation (0.19 s).
        [15:27:27][W][component:215]: Components should block for at most 20-30ms.
        [15:27:27]
        ERROR Serial port closed!
        """

    
