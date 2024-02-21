import cv2
from tkinter import *
from PIL import Image, ImageTk
import time
import threading
import math
import pygame
import numpy as np

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Battery dimensions
BATTERY_WIDTH = 100
BATTERY_HEIGHT = 50
BATTERY_X = 50
BATTERY_Y = 40 # 40

# Speedometer dimensions
SPEEDOMETER_RADIUS = 50
SPEEDOMETER_CENTER = (BATTERY_X + BATTERY_WIDTH + 100, BATTERY_Y + BATTERY_HEIGHT // 2)
SPEEDOMETER_START_ANGLE = 2 * math.pi  # Start angle for semicircle
SPEEDOMETER_END_ANGLE = math.pi  # End angle for semicircle
SPEEDOMETER_MAX_VALUE= 70

# Thermometer dimensions
THERMOMETER_X = 500
THERMOMETER_Y = BATTERY_Y - 30 #10
THERMOMETER_WIDTH = 20
THERMOMETER_HEIGHT = 70

class GUI:
    def __init__(self):
        self.cam1 = None
        self.cam2 = None
        self.cam3 = None
        self.cam4 = None
        self.cam5 = None
        self.cam6 = None
        self.First = True

        self.cap = None
        self.toggleCamera = np.array([0, 0, 0, 0, 0, 0])

        self.cap1 = None
        self.cap2 = None
        self.cap3 = None
        self.cap4 = None
        self.cap5 = None
        self.cap6 = None

        self.img = None

        self.first_camera = 0

        self.total_voltage = np.array([0.0, 0.0])
        self.current = np.array([0.0, 0.0])
        self.power = np.array([0.0, 0.0])
        self.charging_power = np.array([0.0, 0.0])
        self.discharging_power = np.array([0.0, 0.0])
        self.capacity_remaining = np.array([0.0, 0.0])
        self.nominal_capacity = np.array([0.0, 0.0])
        self.charging_cycles = np.array([0.0, 0.0])
        self.balancer_status_bitmask = np.array([0.0, 0.0])
        self.errors_bitmask = np.array([0.0, 0.0])
        self.software_version = np.array([0.0, 0.0])
        self.state_of_charge = np.array([0.0, 0.0])
        self.operation_status_bitmask = np.array([0.0, 0.0])
        self.battery_strings = np.array([0.0, 0.0])
        self.temperature_1 = np.array([0.0, 0.0])
        self.temperature_2 = np.array([0.0, 0.0])
        self.temperature_3 = np.array([0.0, 0.0])
        self.cell_voltage_1 = np.array([0.0, 0.0])
        self.cell_voltage_2 = np.array([0.0, 0.0])
        self.cell_voltage_3 = np.array([0.0, 0.0])
        self.cell_voltage_4 = np.array([0.0, 0.0])
        self.cell_voltage_5 = np.array([0.0, 0.0])
        self.cell_voltage_6 = np.array([0.0, 0.0])
        self.cell_voltage_7 = np.array([0.0, 0.0])
        self.cell_voltage_8 = np.array([0.0, 0.0])
        self.cell_voltage_9 = np.array([0.0, 0.0])
        self.cell_voltage_10 = np.array([0.0, 0.0])
        self.cell_voltage_11 = np.array([0.0, 0.0])
        self.cell_voltage_12 = np.array([0.0, 0.0])
        self.cell_voltage_13 = np.array([0.0, 0.0])
        self.cell_voltage_14 = np.array([0.0, 0.0])
        self.cell_voltage_15 = np.array([0.0, 0.0])
        self.cell_voltage_16 = np.array([0.0, 0.0])
        self.min_cell_voltage = np.array([0.0, 0.0])
        self.max_cell_voltage = np.array([0.0, 0.0])
        self.max_voltage_cell = np.array([0.0, 0.0])
        self.min_voltage_cell = np.array([0.0, 0.0])
        self.delta_cell_voltage = np.array([0.0, 0.0])
        self.average_cell_voltage = np.array([0.0, 0.0])
        self.connection = np.array([0, 0])

        self.bms_numb = 0

        self.lock_bat = threading.Lock()
        self.lock_cam = threading.Lock()
        self.lock_cam_connect = threading.Lock()

        self.calibrateM = 0
        self.up_key = 0
        self.down_key = 0
        self.position_IMU = 0

        # Font
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)

    def Get_Camera_IPs(self, skip = False):
        if(not skip):
            root = Tk()
            root.geometry("800x300")
            root.title("IP of Webcams")
            root.config(bg="light grey")

            # Create an entry for the camera index
            camera_entry_label1 = Label(root, text="Camera 1 IP", bg="light grey", fg="black")
            camera_entry_label1.pack()
            camera_entry1 = Entry(root)
            camera_entry1.pack(ipadx=300)

            # Create an entry for the camera index
            camera_entry_label2 = Label(root, text="Camera 2 IP", bg="light grey", fg="black")
            camera_entry_label2.pack()
            camera_entry2 = Entry(root)
            camera_entry2.pack(ipadx=300)

            # Create an entry for the camera index
            camera_entry_label3 = Label(root, text="Camera 3 IP", bg="light grey", fg="black")
            camera_entry_label3.pack()
            camera_entry3 = Entry(root)
            camera_entry3.pack(ipadx=300)

            # Create an entry for the camera index
            camera_entry_label4 = Label(root, text="Camera 4 IP", bg="light grey", fg="black")
            camera_entry_label4.pack()
            camera_entry4 = Entry(root)
            camera_entry4.pack(ipadx=300)

            # Create an entry for the camera index
            camera_entry_label5 = Label(root, text="Camera 5 IP", bg="light grey", fg="black")
            camera_entry_label5.pack()
            camera_entry5 = Entry(root)
            camera_entry5.pack(ipadx=300)

            # Create an entry for the camera index
            camera_entry_label6 = Label(root, text="Camera 6 IP", bg="light grey", fg="black")
            camera_entry_label6.pack()
            camera_entry6 = Entry(root)
            camera_entry6.pack(ipadx=300)

            def connect():
                self.cam1 = camera_entry1.get()
                self.cam2 = camera_entry2.get()
                self.cam3 = camera_entry3.get()
                self.cam4 = camera_entry4.get()
                self.cam5 = camera_entry5.get()
                self.cam6 = camera_entry6.get()
                self.First = False

            button_text = "Connect to Cameras"
            button = Button(root, text=button_text, bg="white", fg="black", command=connect)
            button.pack(pady=20)


            while self.First:
                root.update()

            root.destroy()
            
        elif(skip):
            self.cam1 = 0

        print(self.cam1, self.cam2, self.cam3, self.cam4, self.cam5, self.cam6)

    def connect_camera(self):
        cap1 = None
        cap2 = None
        cap3 = None
        cap4 = None
        cap5 = None
        cap6 = None
        cap = None

        while True:
            if(self.first_camera == 0 and self.toggleCamera[self.first_camera] == 1 and cap1 is None):
                cap1 = cv2.VideoCapture(int(self.cam1))
            elif(self.first_camera == 1 and self.toggleCamera[self.first_camera] == 1 and cap2 is None):
                cap2 = cv2.VideoCapture(int(self.cam2))
            elif(self.first_camera == 2 and self.toggleCamera[self.first_camera] == 1 and cap3 is None):
                cap3 = cv2.VideoCapture(self.cam3)
            elif(self.first_camera == 3 and self.toggleCamera[self.first_camera] == 1 and cap4 is None):
                cap4 = cv2.VideoCapture(self.cam4)
            elif(self.first_camera == 4 and self.toggleCamera[self.first_camera] == 1 and cap5 is None):
                cap5 = cv2.VideoCapture(self.cam5)
            elif(self.first_camera == 5 and self.toggleCamera[self.first_camera] == 1 and cap6 is None):
                cap6 = cv2.VideoCapture(self.cam6)

            if(self.first_camera == 0 and self.toggleCamera[self.first_camera] == 1):
                cap = cap1
            elif(self.first_camera == 1 and self.toggleCamera[self.first_camera] == 1):
                cap = cap2
            elif(self.first_camera == 2 and self.toggleCamera[self.first_camera] == 1):
                cap = cap3
            elif(self.first_camera == 3 and self.toggleCamera[self.first_camera] == 1):
                cap = cap4
            elif(self.first_camera == 4 and self.toggleCamera[self.first_camera] == 1):
                cap = cap5
            elif(self.first_camera == 5 and self.toggleCamera[self.first_camera] == 1):
                cap = cap6

            if(self.first_camera == 0 and self.toggleCamera[self.first_camera] == 0):
                cap1 = None
                cap = cap1
            if(self.first_camera == 1 and self.toggleCamera[self.first_camera] == 0):
                cap2 = None
                cap = cap2
            if(self.first_camera == 2 and self.toggleCamera[self.first_camera] == 0):
                cap3 = None
                cap = cap3
            if(self.first_camera == 3 and self.toggleCamera[self.first_camera] == 0):
                cap4 = None
                cap = cap4
            if(self.first_camera == 4 and self.toggleCamera[self.first_camera] == 0):
                cap5 = None
                cap = cap4
            if(self.first_camera == 5 and self.toggleCamera[self.first_camera] == 0):
                cap6 = None
                cap = cap5
        
            # print(self.first_camera, self.toggleCamera)

            time.sleep(0.1)

            with self.lock_cam_connect:
                self.cap = cap
                self.cap1 = cap1
                self.cap2 = cap2
                self.cap3 = cap3
                self.cap4 = cap4
                self.cap5 = cap5
                self.cap6 = cap6

    def start_camera_connect_thread(self):
        self.camera_connect_thread = threading.Thread(target=self.connect_camera)
        self.camera_connect_thread.daemon = True
        self.camera_connect_thread.start()

    # helper functions for camera
    def toggle(self):   
        if(self.toggleCamera[self.first_camera] == 0): # turn on camera
            # if(self.first_camera == 0):
            #     self.cap1 = cv2.VideoCapture(int(self.cam1))
            #     self.cap = self.cap1
            # elif(self.first_camera == 1):
            #     self.cap2 = cv2.VideoCapture(int(self.cam2))
            #     self.cap = self.cap2
            # elif(self.first_camera == 2):
            #     self.cap3 = cv2.VideoCapture(self.cam3)
            #     self.cap = self.cap3
            # elif(self.first_camera == 3):
            #     self.cap4 = cv2.VideoCapture(self.cam4)
            #     self.cap = self.cap4
            # elif(self.first_camera == 4):
            #     self.cap5 = cv2.VideoCapture(self.cam5)
            #     self.cap = self.cap5
            # else:
            #     self.cap6 = cv2.VideoCapture(self.cam6)
            #     self.cap = self.cap6
            # toggle stuff
            self.toggleCamera[self.first_camera] = 1
            button_text = "Disconnect Camera"
        else:
            # self.cap.release()
            self.toggleCamera[self.first_camera] = 0
            button_text = "Connect Camera"

        self.cameraB.config(text=button_text)

    def change_cam_add(self):
        if(self.first_camera < 5):
            self.first_camera = self.first_camera + 1
        else:
            self.first_camera = 0

        # if(self.first_camera == 0):
        #     self.cap = self.cap1
        # elif(self.first_camera == 1):
        #     self.cap = self.cap2
        # elif(self.first_camera == 2):
        #     self.cap = self.cap3
        # elif(self.first_camera == 3):
        #     self.cap = self.cap4
        # elif(self.first_camera == 4):
        #     self.cap = self.cap5
        # else:
        #     self.cap = self.cap6

        if(self.toggleCamera[self.first_camera] == 0):
            self.cameraB.config(text="Connect Camera")
        else:
            self.cameraB.config(text="Disconnect Camera")

        self.frame1.config(text="Camera Feed " + str(self.first_camera+1))

        print(self.first_camera, self.toggleCamera)

    def change_cam_sub(self):
        if(self.first_camera > 0):
            self.first_camera = self.first_camera - 1
        else:
            self.first_camera = 5

        # if(self.first_camera == 0):
        #     self.cap = self.cap1
        # elif(self.first_camera == 1):
        #     self.cap = self.cap2
        # elif(self.first_camera == 2):
        #     self.cap = self.cap3
        # elif(self.first_camera == 3):
        #     self.cap = self.cap4
        # elif(self.first_camera == 4):
        #     self.cap = self.cap5
        # else:
        #     self.cap = self.cap6

        if(self.toggleCamera[self.first_camera] == 0):
            self.cameraB.config(text="Connect Camera")
        else:
            self.cameraB.config(text="Disconnect Camera")


        self.frame1.config(text="Camera Feed " + str(self.first_camera+1))

        print(self.first_camera, self.toggleCamera)

    # helper functions for map
    def calibrate_map_p(self):
        self.calibrateM = 1

    def calibrate_map_r(self):
        self.calibrateM = 0

    def up_p(self):
        self.up_key = 1
    
    def up_r(self):
        self.up_key = 0

    def down_p(self):
        self.down_key = 1
    
    def down_r(self):
        self.down_key = 0

    # diagnostic data helper functions
    def get_bat_data(self):
        while True:
            self.battery.read_esp32()
            total_voltage, current, power, charging_power, discharging_power, capacity_remaining, nominal_capacity, charging_cycles, balancer_status_bitmask, errors_bitmask, software_version, state_of_charge, operation_status_bitmask, battery_strings, temperature_1, temperature_2, temperature_3, cell_voltage_1, cell_voltage_2, cell_voltage_3, cell_voltage_4, cell_voltage_5, cell_voltage_6, cell_voltage_7, cell_voltage_8, cell_voltage_9, cell_voltage_10, cell_voltage_11, cell_voltage_12, cell_voltage_13, cell_voltage_14, cell_voltage_15, cell_voltage_16, min_cell_voltage, max_cell_voltage, max_voltage_cell, min_voltage_cell, delta_cell_voltage, average_cell_voltage, connection = self.battery.parse_data()
            
            with self.lock_bat:
                self.total_voltage = total_voltage
                self.current = current
                self.power = power
                self.charging_power = charging_power
                self.discharging_power = discharging_power
                self.capacity_remaining = capacity_remaining
                self.nominal_capacity = nominal_capacity
                self.charging_cycles = charging_cycles
                self.balancer_status_bitmask = balancer_status_bitmask
                self.errors_bitmask = errors_bitmask
                self.software_version = software_version
                self.state_of_charge = state_of_charge
                self.operation_status_bitmask = operation_status_bitmask
                self.battery_strings = battery_strings
                self.temperature_1 = temperature_1
                self.temperature_2 = temperature_2
                self.temperature_3 = temperature_3
                self.cell_voltage_1 = cell_voltage_1
                self.cell_voltage_2 = cell_voltage_2
                self.cell_voltage_3 = cell_voltage_3
                self.cell_voltage_4 = cell_voltage_4
                self.cell_voltage_5 = cell_voltage_5
                self.cell_voltage_6 = cell_voltage_6
                self.cell_voltage_7 = cell_voltage_7
                self.cell_voltage_8 = cell_voltage_8
                self.cell_voltage_9 = cell_voltage_9
                self.cell_voltage_10 = cell_voltage_10
                self.cell_voltage_11 = cell_voltage_11
                self.cell_voltage_12 = cell_voltage_12
                self.cell_voltage_13 = cell_voltage_13
                self.cell_voltage_14 = cell_voltage_14
                self.cell_voltage_15 = cell_voltage_15
                self.cell_voltage_16 = cell_voltage_16
                self.min_cell_voltage = min_cell_voltage
                self.max_cell_voltage = max_cell_voltage
                self.max_voltage_cell = max_voltage_cell
                self.min_voltage_cell = min_voltage_cell
                self.delta_cell_voltage = delta_cell_voltage
                self.average_cell_voltage = average_cell_voltage
                self.connection = connection
                
    def start_bat_thread(self):
        self.battery_thread = threading.Thread(target=self.get_bat_data)
        self.battery_thread.daemon = True
        self.battery_thread.start()

    def change_batt(self):
        if(self.bms_numb == 0):
            self.bms_numb = 1
        else:
            self.bms_numb = 0
        self.frame3.config(text="Battery Diagnostics BMS " + str(self.bms_numb))

    def init_pygame(self):
        screen = pygame.Surface((self.diag_w, self.diag_h))

        # Initialize Pygame screen
        screen.fill((0, 0, 0))

        self.clock = pygame.time.Clock()

        return screen

    def update_pygames_screen(self, screen):
        # Update Pygame screen
        # pygame.display.flip()
        """Convert Pygame surface to PIL image."""
        image_str = pygame.image.tostring(screen, 'RGB')
        img = Image.frombytes('RGB', (self.diag_w, self.diag_h), image_str)
        img_tk = ImageTk.PhotoImage(image=img)

        self.clock.tick(60)
        # end program 
        return img_tk

    # Function to draw battery
    def draw_battery(self, screen, percent, charging, x= BATTERY_X, y = BATTERY_Y):
        # Draw background
        screen.fill(BLACK)
        
        y_shift = 20

        txt = self.font_small.render("Battery SoC", True, WHITE)
        tet_rect = txt.get_rect(center=(x + 50, y - 30))
        screen.blit(txt, tet_rect)

        # Draw battery outline
        pygame.draw.rect(screen, WHITE, (x, y - y_shift, BATTERY_WIDTH, BATTERY_HEIGHT), 2)
        
        pygame.draw.rect(screen, WHITE, (x + BATTERY_WIDTH - 2, y - y_shift + 30 // 2, 8, 20), 2)

        # Calculate fill width based on percent
        fill_width = (BATTERY_WIDTH - 4) * percent / 100
        
        # Determine color based on percent
        if percent <= 10:
            color = RED
        elif percent <= 25:
            color = YELLOW
        else:
            color = GREEN
        
        # Draw battery fill
        pygame.draw.rect(screen, color, (x + 2, y + 2 - y_shift, fill_width, BATTERY_HEIGHT - 4))
        
        # Draw charge symbol if charging
        if charging:
            charge_x = x + BATTERY_WIDTH + 20
            charge_y = y + BATTERY_HEIGHT // 2 - y_shift
            self.draw_charging_symbol(screen, charge_x, charge_y, WHITE)
        
        # Draw battery percentage text
        text = self.font.render(f"{percent}%", True, WHITE)
        text_rect = text.get_rect(center=(x + BATTERY_WIDTH // 2 + 5, y + 45))
        screen.blit(text, text_rect)

        font_big = pygame.font.Font(None, 72)

        if(color == RED):
            txt = font_big.render("!", True, WHITE)
            tet_rect = txt.get_rect(center=(x + BATTERY_WIDTH // 2, y + BATTERY_HEIGHT // 2 + 2 - y_shift))
            screen.blit(txt, tet_rect)

    # Function to draw charging symbol with triangles
    def draw_charging_symbol(self, screen, x, y, color):
        # Draw upper triangle
        pygame.draw.polygon(screen, color, [(x - 8, y), (x + 3, y), (x, y - 18)])
        # Draw lower triangle
        pygame.draw.polygon(screen, color, [(x - 3, y-4), (x + 8, y-4), (x, y + 14)])

    def speedometer(self, screen, speed, value="V", name = "Battery Voltage", max_val = 70, x = BATTERY_X + BATTERY_WIDTH + 100, y = BATTERY_Y + BATTERY_HEIGHT // 2, fuse=0, r = 50):
        # Draw speedometer
        # pygame.draw.arc(screen, BLUE, (SPEEDOMETER_CENTER[0] - SPEEDOMETER_RADIUS, SPEEDOMETER_CENTER[1] - SPEEDOMETER_RADIUS, 2 * SPEEDOMETER_RADIUS, 2 * SPEEDOMETER_RADIUS), SPEEDOMETER_START_ANGLE, SPEEDOMETER_END_ANGLE, 2)
        txt = self.font_small.render(name, True, WHITE)
        tet_rect = txt.get_rect(center=(x , y - 56))
        screen.blit(txt, tet_rect)

        y = y + 4

        # Fill the semicircle behind the indicator
        indicator_angle = SPEEDOMETER_START_ANGLE + ((max_val-speed) / max_val) * (SPEEDOMETER_END_ANGLE - SPEEDOMETER_START_ANGLE)
        indicator_pos = (int(x + r * math.cos(indicator_angle)), int(y + r * math.sin(indicator_angle)))

        if(fuse > 0):
            indicator_angle_fuse = SPEEDOMETER_START_ANGLE + ((max_val-fuse) / max_val) * (SPEEDOMETER_END_ANGLE - SPEEDOMETER_START_ANGLE)
            indicator_pos_fuse = (int(x + r * math.cos(indicator_angle_fuse)), int(y + r * math.sin(indicator_angle_fuse)))

        # Draw indicator on speedometer based on speed
        # pygame.draw.line(screen, WHITE, SPEEDOMETER_CENTER, indicator_pos, 2)

        # Draw line for the bottom of the semicircle
        bottom_point_left = (x - r, y)
        bottom_point_right = (x + r, y)
        # pygame.draw.line(screen, BLUE, bottom_point_left, bottom_point_right, 2)

        # Calculate points along the arc
        arc_points = []
        num_points = 100
        for i in range(num_points + 1):
            angle = SPEEDOMETER_END_ANGLE + 0.07 + (indicator_angle - SPEEDOMETER_END_ANGLE) * i / num_points
            x_new = x + (SPEEDOMETER_RADIUS-2) * math.cos(angle-.1)
            y_new = y + (SPEEDOMETER_RADIUS-2) * math.sin(angle-.1)
            arc_points.append((x_new, y_new))

        # Create a polygon to fill the area between the lines
        polygon_points = [bottom_point_left, (x, y), (x, y), indicator_pos]

        if(fuse == 0):
            if(speed <= 0.5*max_val):
                color = GREEN
            elif(speed <= 0.7*max_val and speed > 0.5*max_val):
                color = YELLOW
            else:
                color = RED
        else:
            if(speed <= 0.5*fuse):
                color = GREEN
            elif(speed <= fuse and speed > 0.5*fuse):
                color = YELLOW
            else:
                color = RED

        # Fill the polygon with color
        pygame.draw.polygon(screen, color, polygon_points)
        # Create a polygon from the points and fill it
        pygame.draw.polygon(screen, color, arc_points)

        pygame.draw.arc(screen, WHITE, (x - r, y - r, 2 * r, 2 * r), SPEEDOMETER_START_ANGLE, SPEEDOMETER_END_ANGLE, 2)
        pygame.draw.line(screen, WHITE, (x,y), indicator_pos, 2)
        pygame.draw.line(screen, WHITE, bottom_point_left, bottom_point_right, 2)

        if(fuse > 0):
            pygame.draw.line(screen, RED, (x,y), indicator_pos_fuse, 4)

        # Draw speed number
        text_surface = self.font.render(str(speed) + value, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y + 20))
        screen.blit(text_surface, text_rect)

        if(fuse > 0):
            text_surface = self.font.render(str(fuse) + value, True, RED)
            text_rect = text_surface.get_rect(center=(x + 100, y - 30))
            screen.blit(text_surface, text_rect)


        font_big = pygame.font.Font(None, 72)

        if(color == RED):
            txt = font_big.render("!", True, WHITE)
            tet_rect = txt.get_rect(center=(x, y - 20))
            screen.blit(txt, tet_rect)

    def draw_thermometer(self, screen, value, text = "Battery Temperature", x = THERMOMETER_X, y = THERMOMETER_Y):
        # text
        txt = self.font_small.render(text, True, WHITE)
        tet_rect = txt.get_rect(center=(x , y))
        screen.blit(txt, tet_rect)
        
        y = y + 10
        x = x - 5

        # Thermometer outline
        pygame.draw.rect(screen, WHITE, (x, y, THERMOMETER_WIDTH, THERMOMETER_HEIGHT), 2)

        # Calculate fill height based on value
        fill_height = THERMOMETER_HEIGHT * (value / 100)

        if(value <= 0.5*100):
            color = GREEN
        elif(value <= 0.7*100 and value > 0.5*100):
            color = YELLOW
        else:
            color = RED

        # Draw speed number
        text_surface = self.font.render(str(value) + "°C", True, WHITE)
        text_rect = text_surface.get_rect(center=(x + 75 , y + 35))
        screen.blit(text_surface, text_rect)

        # Fill thermometer
        fill_rect = pygame.Rect(x + 1, y + THERMOMETER_HEIGHT - fill_height, THERMOMETER_WIDTH - 1, fill_height)
        pygame.draw.rect(screen, color, fill_rect)

    def draw_status(self, screen, on_off, x=0, y=0):
        if(on_off == 1):
            color = GREEN
        else:
            color = RED

        pygame.draw.circle(screen, color, (x, y+10), 20) 

    def draw_status_text(self, screen, name="Connection Status", x=0, y=0):
        # text
        txt = self.font_small.render(name, True, WHITE)
        tet_rect = txt.get_rect(center=(x , y-30))
        screen.blit(txt, tet_rect)

    # camera thread
    def camera_update(self):
        # get the camera feed
        while True:
            if self.cap is not None:
                ret, img = self.cap.read()
                with self.lock_cam:
                    self.img = img
            else:
                time.sleep(1)
                with self.lock_cam:
                    self.img = None

    def start_cam_thread(self):
        self.cam_thread1 = threading.Thread(target=self.camera_update)
        self.cam_thread1.daemon = True
        self.cam_thread1.start()

    # positioning
    def change_right_side(self):
        if(self.position_IMU == 0):
            self.position_IMU = 1
            self.frame2.config(text="IMU")
            self.button3.destroy()
            self.button4.destroy()
            self.cameraC.destroy()

            # calibrate IMU
            self.cameraC = Button(self.frame2, text="Calibrate IMU", bg="#FFD100", fg="black")
            self.cameraC.pack(side=LEFT, padx=self.local_w/2)
        else:
            self.position_IMU = 0
            self.cameraC.destroy()
            self.frame2.config(text="Positioning")
            # + and - for positioning
            self.button4 = Button(self.frame2, text="+", bg="#FFD100", fg="black")
            self.button4.pack(side=LEFT)
            self.button4.bind("<ButtonPress>", lambda event: self.up_p())
            self.button4.bind("<ButtonRelease>", lambda event: self.up_r())


            self.button3 = Button(self.frame2, text="-", bg="#FFD100", fg="black")
            self.button3.pack(side=LEFT)
            self.button3.bind("<ButtonPress>", lambda event: self.down_p())
            self.button3.bind("<ButtonRelease>", lambda event: self.down_r())

            # calibrate localization
            self.cameraC = Button(self.frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
            self.cameraC.pack(side=LEFT, padx=self.local_w/2.7)
            self.cameraC.bind("<ButtonPress>", lambda event: self.calibrate_map_p())
            self.cameraC.bind("<ButtonRelease>", lambda event: self.calibrate_map_r())

    def set_screen(self, width = None, height = None):
        root = Tk()
        if(width == None and height == None):
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
        else:
            self.screen_width = width
            self.screen_height = height

        # intitalizing the GUI
        self.video_w = int(self.screen_width/1.5) # 800
        self.video_h = int(self.screen_height/1.5) # 480
        self.local_w = self.screen_width - 200 - self.video_w
        self.local_h = self.video_h
        self.diag_w = self.screen_width - 40
        self.diag_h = self.screen_height - self.video_h - 160

        print(self.screen_width)
        print(self.screen_height)

        root.destroy()

        return self.video_w, self.video_h, self.local_w + 132, self.local_h

    def Main_UI(self, battery, localization, distance, rover_controls):
        self.battery = battery

        root = Tk()
        root.attributes('-fullscreen', True)
        root.geometry("{}x{}".format(self.screen_width, self.screen_height))
        root.title("Main GUI")
        root.config(bg="#2c3e50")
        # padding
        padx = 5
        pady = 5

        # Create a black image
        black_image_video = Image.new("RGB", (self.video_w, self.video_h), "black")
        black_image_right = Image.new("RGB", (self.local_w + 130, self.local_h), "black")
        black_image_diag = Image.new("RGB", (self.diag_w, self.diag_h), "black")

        # Convert the Image to PhotoImage
        black_image_video_tk = ImageTk.PhotoImage(black_image_video)
        black_image_right_tk = ImageTk.PhotoImage(black_image_right)
        black_image_diag_tk = ImageTk.PhotoImage(black_image_diag)

        # Create a frame for the first two LabelFrames and use pack (video feed and map)
        frame_container1 = Frame(root, bg="#0033A0")
        frame_container1.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # video feed
        # Create the first LabelFrame stacked horizontally using pack
        self.frame1 = LabelFrame(frame_container1, text="Camera Feed 1", padx=padx, pady=pady)
        self.frame1.pack(side=LEFT, padx=padx, pady=pady)

        label1 = Label(self.frame1, bg="black")
        label1.pack()

        label1['image'] = black_image_video_tk

        # move camera left and right
        button2 = Button(self.frame1, text="<", bg="#FFD100", fg="black", command=self.change_cam_sub)
        button2.pack(side=LEFT)

        button1 = Button(self.frame1, text=">", bg="#FFD100", fg="black", command=self.change_cam_add)
        button1.pack(side=LEFT)

        # connect camera button
        button_text = "Connect Camera"
        self.cameraB = Button(self.frame1, text=button_text, bg="#FFD100", fg="black", command=self.toggle)
        self.cameraB.pack(side=LEFT, padx=self.video_w/2.7)

        # mapping
        # Create the second LabelFrame stacked horizontally using pack
        self.frame2 = LabelFrame(frame_container1, text="Positioning", padx=padx, pady=pady)
        self.frame2.pack(side=LEFT, padx=padx, pady=pady)

        label2 = Label(self.frame2, bg="black")
        label2.pack()

        # + and - for positioning
        self.button4 = Button(self.frame2, text="+", bg="#FFD100", fg="black")
        self.button4.pack(side=LEFT)
        self.button4.bind("<ButtonPress>", lambda event: self.up_p())
        self.button4.bind("<ButtonRelease>", lambda event: self.up_r())


        self.button3 = Button(self.frame2, text="-", bg="#FFD100", fg="black")
        self.button3.pack(side=LEFT)
        self.button3.bind("<ButtonPress>", lambda event: self.down_p())
        self.button3.bind("<ButtonRelease>", lambda event: self.down_r())

        # calibrate localization
        self.cameraC = Button(self.frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
        self.cameraC.pack(side=LEFT, padx=self.local_w/2.7)
        self.cameraC.bind("<ButtonPress>", lambda event: self.calibrate_map_p())
        self.cameraC.bind("<ButtonRelease>", lambda event: self.calibrate_map_r())

        # change right side view
        button5 = Button(self.frame2, text=">", bg="#FFD100", fg="black", command=self.change_right_side)
        button5.pack(side=RIGHT)

        button6 = Button(self.frame2, text="<", bg="#FFD100", fg="black", command=self.change_right_side)
        button6.pack(side=RIGHT)

        # diagnostic data
        # Create a frame for the third LabelFrame and use pack
        frame_container2 = Frame(root, bg="#0033A0")
        frame_container2.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # Create the third LabelFrame below the first two using pack
        self.frame3 = LabelFrame(frame_container2, text="Battery Diagnostics BMS " + str(self.bms_numb), padx=padx, pady=pady, bg="white")
        self.frame3.pack(side=LEFT, padx=padx, pady=pady)

        label3 = Label(self.frame3, bg="black")
        label3.pack()

        label3['image'] = black_image_diag_tk
        
        # change battery diagnostics
        button8 = Button(self.frame3, text="<", bg="#FFD100", fg="black", command=self.change_batt)
        button8.pack(side=LEFT)

        button7 = Button(self.frame3, text=">", bg="#FFD100", fg="black", command=self.change_batt)
        button7.pack(side=LEFT)

        # start battery thread
        self.start_bat_thread()

        # start camera thread
        self.start_cam_thread()

        # camera connection
        self.start_camera_connect_thread()
    
        # battery display
        self.screenDiag = self.init_pygame()
            
        # intitalize the previous bms
        prev_bms = self.bms_numb

        # Initialize a variable to track the last time update_battery_diagnostics() was called
        last_update_time = time.time()

        first = 1

        while True: # not rover_controls.Get_Button_From_Controller():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    root.quit()

            # Select = rover_controls.Get_Button_From_Controller(stop_button="Select") # select button is pressed or not

            # print(rover_controls.Controller_To_PWM_and_DIR())

            # get the camera feed
            if self.cap is not None:
                cv_img = self.img
                if(cv_img is not None):
                    img1 = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                    img2 = cv2.resize(img1, (self.video_w, self.video_h))
                    img = ImageTk.PhotoImage(Image.fromarray(img2))
                    label1['image'] = img
                else:
                    label1['image'] = black_image_video_tk
            else:
                label1['image'] = black_image_video_tk

            # opencv image (1)
            if(self.cap1 is not None):
                if(self.img is not None):
                    opencv_img = self.img
                else:
                    opencv_img = None
            else:
                opencv_img = None

            # Check if one second has passed since the last call to update_battery_diagnostics()
            if time.time() - last_update_time >= 1 or prev_bms is not self.bms_numb or first:
                # update the battery diagnostic data
                steps = int(self.diag_w/7.5)
                down_step = int(self.diag_h/2.5)
                print(steps, down_step)
                self.draw_battery(self.screenDiag, int(self.state_of_charge[self.bms_numb]), self.charging_power[0] > 0.00, BATTERY_X + steps/5, down_step)
                self.speedometer(self.screenDiag, round(self.total_voltage[self.bms_numb], 1), "V", "Battery Voltage", 60, BATTERY_X + BATTERY_WIDTH + steps, down_step + BATTERY_HEIGHT // 2)
                self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Battery Current", 100, BATTERY_X + BATTERY_WIDTH + 2*steps, down_step + BATTERY_HEIGHT // 2)
                self.speedometer(self.screenDiag, round(self.power[self.bms_numb], 1), "W", "Battery Power", 100, BATTERY_X + BATTERY_WIDTH + 3*steps, down_step + BATTERY_HEIGHT // 2)
                self.speedometer(self.screenDiag, round(self.capacity_remaining[self.bms_numb], 1), "Ah", "Battery Capacity", 100, BATTERY_X + BATTERY_WIDTH + 4*steps, down_step + BATTERY_HEIGHT // 2)
                self.draw_thermometer(self.screenDiag, round((self.temperature_1[self.bms_numb] + self.temperature_2[self.bms_numb] + self.temperature_3[self.bms_numb]) / 3, 1), "Battery Temperature", BATTERY_X + BATTERY_WIDTH + 5*steps, down_step - 30)
                self.draw_status_text(self.screenDiag, "Connection Status", BATTERY_X + BATTERY_WIDTH + 6*steps, down_step)

                last_update_time = time.time()  # Update the last update time
                prev_bms = self.bms_numb

                first = 0

            # print(self.connection)
            self.draw_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 6*steps, down_step)

            x, y, z, dist, tags_ids, rVx, rVy, rVz = distance.aruco_tags(pic_out=False, Frame=opencv_img) # <--- if you want a picture to be dispayed.
            # get origin tag (tag at 0,0,0)
            localization.get_origin_tag(tags_ids, dist, x, y, z, rVx, rVy, rVz)

            # compute other tags (reference to other tags)
            localization.compute_tag_camera_location(tags_ids, dist, x, y, z, rVx, rVy, rVz)

            localization.handler()

            # display the tags on the map
            localization.show_tags()
            # display the camera on the map
            localization.show_camera()

            # handler and legend
            localization.legend()

            if(self.position_IMU == 0):
                end, img_2 = localization.update_pygames_screen()
                label2['image'] = img_2
            else:
                label2['image'] = black_image_right_tk

            img_3 = self.update_pygames_screen(self.screenDiag)
            label3['image'] = img_3

            # quit the program
            if distance.wait_key("q") or end:
                break

            localization.controller_handler(self.calibrateM, self.up_key, self.down_key)

            root.update()

        self.cap.release()
        root.destroy()