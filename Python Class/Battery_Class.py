# esp32 class
import serial.tools.list_ports

class Battery_class:
    def __init__(self, verbose = False, option = 1, buad_rate=115200):
        
        self.verbose = verbose
        self.option = option
        self.buad_rate = buad_rate

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
        dataPacket_str = dataPacket.decode('utf-8').rstrip()                    # convert the bytes to a str
        print(dataPacket_str)

    def disable_read(self):
        self.arduinoData.close()