# esp32 class
import serial.tools.list_ports
import cmath
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

class UWB_Class:
    def __init__(self, verbose = False, option = 1, buad_rate=115200, a = -1, b = -1, speed = 1, anchor_add = np.array([1, 2, 3, 4]),
                anchor_x = np.array([0.0, 1.0, 1.0, 0.0]), anchor_y = np.array([0.0, 0.0, 1.0, 1.0]), distances = np.array([0.0, 0.0, 0.0, 0.0]),
                change_dist = np.array([0, 0, 0, 0]), prev_dist = np.array([0.0, 0.0, 0.0, 0.0]), update_fig_interval = 0,
                update_fig_interval_max = 10, distance_changes_max = 20):
        
        self.verbose = verbose
        self.option = option
        self.buad_rate = buad_rate
        self.a = a
        self.b = b
        self.speed = speed
        self.anchor_add = anchor_add
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.distances = distances
        self.change_dist = change_dist
        self.prev_dist = prev_dist
        self.update_fig_interval = update_fig_interval
        self.update_fig_interval_max = update_fig_interval_max
        self.distance_changes_max = distance_changes_max

        plt.ion()

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
 
    def serial_communication(self):
        esp32_port = self.get_esp32()

        arduinoData = serial.Serial(esp32_port, 115200)

        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 
        dataPacket=arduinoData.readline() 

        return arduinoData
    
    def read_arduino(self, arduinoData):
        
        a_change = False
        b_change = False

        while(arduinoData.inWaiting()==0): # wait for data
            pass

        dataPacket=arduinoData.readline()                         # read the data from the arduino
        dataPacket_str = dataPacket.decode('utf-8')               # convert the bytes to a str
        comma_spot = dataPacket_str.find(',')                     # get the comma spot
        return_spot = dataPacket_str.find('\n')                   # get the stuff return spot
        address = int(dataPacket[0:comma_spot])                   # grab the stuff before the comma (address of the anchor)
        measurement = float(dataPacket[comma_spot+1:return_spot]) # grab the stuff after the comma (measurement)

        if(address <= 3): # first three adresses are for the first "big anchor"
            a_n = measurement
            a_change = True
        elif(address > 3 and address <= 6): # second three adresses are for the first "big anchor"
            b_n = measurement
            b_change = True
        # last three adresses are for the first "big anchor"

        if(a_change):
            if(self.a != -1):
                if(a_n < self.a + self.speed and a_n > self.a - self.speed): # witin 5m
                    self.a = a_n
            else:
                self.a = a_n
        
        if(b_change):
            if(self.b != -1):
                if(b_n < self.b + self.speed and b_n > self.b - self.speed): # witin 5m
                    self.b = b_n
            else:
                self.b = b_n

        return [self.a, self.b]
    
    def read_arduino_2(self, arduinoData):

        while(arduinoData.inWaiting()==0): # wait for data
            pass

        dataPacket=arduinoData.readline()                         # read the data from the arduino
        dataPacket_str = dataPacket.decode('utf-8')               # convert the bytes to a str
        comma_spot = dataPacket_str.find(',')                     # get the comma spot
        return_spot = dataPacket_str.find('\\')                   # get the stuff return spot
        address = int(dataPacket[0:comma_spot])                   # grab the stuff before the comma (address of the anchor)
        measurement = float(dataPacket[comma_spot+1:return_spot]) # grab the stuff after the comma (measurement)
        return [address, measurement]
    
    def coordinates_calc(self, c, arduinoData):
        # a = length between orgin anchor
        # b = legnth between distant anchor
        # c = length between anchors

        [b, a] = self.read_arduino(arduinoData) # get data

        if b == 0 or c == 0:
            # Handle the case where b or c is zero to avoid division by zero
            return None, None
        
        cos_a = (b * b + c * c - a * a) / (2 * b * c)
        x = b * cos_a
        y = b * cmath.sqrt(1 - cos_a * cos_a)

        return round(x.real, 2), round(y.real, 2)
    
    def calculate_closest_point(self, condition):
        # Define a function that calculates the sum of squared errors between
        # the distances from a point (x, y) to the circle centers and the circle radii.
        anchor_x = self.anchor_x[condition]
        anchor_y = self.anchor_y[condition], 
        distances = self.distances[condition]

        def objective(point):
            x, y = point
            dx = x - anchor_x
            dy = y - anchor_y
            errors = np.sum((np.sqrt(dx**2 + dy**2) - distances)**2)
            return errors

        # Initial guess based on the average of anchor coordinates
        initial_guess = (np.mean(anchor_x), np.mean(anchor_y))

        # Use minimize to find the point that minimizes the objective function
        result = minimize(objective, initial_guess, method='Nelder-Mead', options={'xtol': 1e-5, 'ftol': 1e-5})

        if result.success:
            return result.x
        else:
            return None  # Optimization did not converge to a solution
        
    def make_circles(self, closest_point, circles = True):
        """
        Plot circles with given radii and center points for multiple anchors.

        :param anchor_add: List of anchor labels or names.
        :param anchor_x: List of anchor x-coordinates.
        :param anchor_y: List of anchor y-coordinates.
        :param distances: List of radii for each anchor.
        :param closest_point: (x, y) coordinates of the closest point (optional).
        """

        # Create a figure and axis if it doesn't exist
        if not plt.fignum_exists(1):
            fig, ax = plt.subplots()
        else:
            fig = plt.gcf()
            ax = plt.gca()

        # Clear the current axis
        ax.clear()

        # Plot circles for each anchor
        for i, (x, y, label, radius) in enumerate(zip(self.anchor_x, self.anchor_y, self.anchor_add, self.distances)):
            if(circles == True):
                circle = plt.Circle((x, y), radius, fill=False, label=f"Anchor {label} Radius")
                ax.add_artist(circle)

            # Plot the anchor point
            ax.scatter(x, y, label=f"Anchor {label}", marker='o', color='blue')

            # Add text annotations for anchor label and radius
            ax.text(x, y, f"{label}", fontsize=12, ha="left")

        # Plot the closest point if provided
        if closest_point is not None:
            x, y = closest_point
            ax.scatter(x, y, label="Closest Point", marker='x', color='red')

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.grid()

        # Set equal scaling for x and y axes
        ax.set_aspect('equal', adjustable='box')

        # Calculate the limits for x and y axes
        x_min = -5 #min(anchor_x - distances)
        x_max = 80 #max(anchor_x + distances)
        y_min = -5 #min(anchor_y - distances)
        y_max = 80 #max(anchor_y + distances)

        # Set axis limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        plt.draw()
        plt.pause(1e-3)  # Adjust the pause duration as needed

    def Graphical_display(self, arduinoData, plot = True, circles = True):
        add, dist = self.read_arduino_2(arduinoData)
        self.prev_dist = self.distances.copy()
        self.distances[add-1] = dist

        for i in range(len(self.anchor_add)):
            if(self.prev_dist[i] == self.distances[i]):
                self.change_dist[i] += 1 # add one each time
            else:
                self.change_dist[i] = 0 # reset back to zero

        print(self.distances)

        condition = self.change_dist < self.distance_changes_max

        closest_point = self.calculate_closest_point(condition)

        if(plot == True):
            if(self.update_fig_interval == self.update_fig_interval_max):
                self.make_circles(closest_point, circles)
                self.update_fig_interval = 0
            else:
                self.update_fig_interval+=1
            
            plt.ioff()

        return round(closest_point[0], 2), round(closest_point[1], 2)
        

    

                
            



        
