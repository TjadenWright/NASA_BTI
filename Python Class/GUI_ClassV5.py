import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import time
import threading
import math
import pygame
import numpy as np
import random
import os
from PTZ_Control_Class import ptzControl
from Camera_Class import Amcrest_Camera

current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
config_data_path = os.path.join(current_file_path, '../Config_Files')

file_name_IP = "IP_Camera_Config.txt"
file_path_IP = os.path.join(config_data_path, file_name_IP)

file_name_Channel = "Channel_Config.txt"
file_path_Channel = os.path.join(config_data_path, file_name_Channel)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

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
    def __init__(self, Camera_usb=False, number_of_cams = 6):
        # make the cameras usbs or not (default to not)
        self.Camera_usb = Camera_usb
        self.number_of_cams = number_of_cams

        # for camera stuff
        self.FirstCamIP = 0
        self.opneCVCam = 0

        self.toggleCamera = [0] * self.number_of_cams
        self.cam = [""] * self.number_of_cams

        # ptz classes
        self.ptz = None

        self.img = None
        self.imgCV = None

        self.configured_camera_IPs = False

        self.selected_camera = 0

        self.debugger = 0
        self.mode = 0

        # controls
        self.autonomy_manual = 0
        self.manual_mode = 0
        self.selected_channel = 0

        self.autonomy_manual_lock = 0
        self.manual_mode_lock = 0
        self.selected_channel_lock = 0

        # for bms stuff
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
        self.board_batt = 0
        self.board_channel = 0

        self.FirstChannelSelect = 0
        
        self.master = None
        self.masterIP = None
        self.masterPOPUP = None

        # channel selector
        self.channel = np.zeros(16, int) # 16 channels
        self.channel_options = ["Front Left Drive Motor", "Front Right Drive Motor", "Rear Left Drive Motor", "Rear Right Drive Motor", "Bucketwheel Motor", "Front Auger Motor", "Rear Auger Motor", "Pivot Slew Gear", "Vibration Motor", "Excavation Arm Lift Actuator", "Ramps Actuator", "Battery Lock 1 Actuator", "Battery Lock 2 Actuator", "Battery Push 1 Actuator", "Battery Push 1 Actuator", "Hopper Actuator", "IMU and Motherboard"]
        self.channel_option_to_arduino = [0, 0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 3]
        self.channel_config_naming = np.zeros(16, int)
                              # "Motor", "Actuator", "Slew Gear", "IMU and Motherboard"

        # threading
        self.lock_bat = threading.Lock()
        self.lock_cam = threading.Lock()
        self.lock_camCV = threading.Lock()
        self.lock_ptz = threading.Lock()
        self.lock_debounce = threading.Lock()
        self.lock_popup_clock = threading.Lock()

        self.debounce_button = 0
        self.popup_gui_key = 0

        # buttons for localization
        self.calibrateM = 0
        self.up_key = 0
        self.down_key = 0
        self.position_IMU = 0
        
        # previous popup
        self.prev_popup = -1

        # Font
        self.font = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.ui_font = ("Helvetica", 16)
        self.ui_font_debug = ("Helvetica", 16)

        # spacing
        self.reg_keys = 17.35 # 11.371
        self.reg_keys_drop = 13.5 # 14
        self.debugging_off = 19 # 18.26 # 11.97
        self.calib_local = 10 # 4.5
        self.calib_imu = 2
        self.diag_keys = 9 # 8.5
        self.diag_drop_down = 7 # 8.5

    def on_closing_popup(self):
        self.masterPOPUP.destroy()
        self.popup_gui_key = 0
        self.masterPOPUP = None

    def handle_selection_select_channel(self, event):
        selected_item = self.dropdown_3.current()
        self.selected_channel = selected_item

    def handle_selection_man_mode(self, event):
        selected_item = self.dropdown_2.current()
        self.manual_mode = selected_item

        if(self.manual_mode == 0):
            options3 = ["Channel " + str(i) + " - " + self.channel_options[self.channel_config_naming[i]] for i in range(16)]


            # Create a dropdown widget
            if(self.dropdown_3 is None):
                self.button_popup.destroy()

                self.dropdown_3 = ttk.Combobox(self.masterPOPUP, values=options3, state="readonly", font=self.ui_font_debug)
                self.dropdown_3.pack(pady=6, ipadx=self.diag_w/self.reg_keys_drop)
                self.dropdown_3.bind("<<ComboboxSelected>>", self.handle_selection_select_channel)

                self.button_popup = Button(self.masterPOPUP, text="OK", bg="#FFD100", fg="black", command=self.on_closing_popup)
                self.button_popup.pack(ipadx=150, ipady=40, pady=5)
                self.button_popup.config(font=self.ui_font_debug)
        else:
            if(self.dropdown_3):
                self.dropdown_3.destroy()

    def handle_selection_man_or_auto(self, event):
            selected_item = self.dropdown_1.current()
            self.autonomy_manual = selected_item

            if(selected_item == 0): # manual mode
                options2 = ["Individual Control", "Drive Mode", "Excavate Mode", "Place Holder"]

                if(self.dropdown_2 is None):
                    self.button_popup.destroy()

                    # Create a dropdown widget
                    self.dropdown_2 = ttk.Combobox(self.masterPOPUP, values=options2, state="readonly", font=self.ui_font_debug)
                    self.dropdown_2.pack(pady=6, ipadx=self.diag_w/self.reg_keys_drop)
                    self.dropdown_2.bind("<<ComboboxSelected>>", self.handle_selection_man_mode)

                    self.button_popup = Button(self.masterPOPUP, text="OK", bg="#FFD100", fg="black", command=self.on_closing_popup)
                    self.button_popup.pack(ipadx=150, ipady=40, pady=5)
                    self.button_popup.config(font=self.ui_font_debug)
            else:
                if(self.dropdown_3):
                    self.dropdown_3.destroy()
                if(self.dropdown_2):
                    self.dropdown_2.destroy()


            

    # popups
    def popup_gui(self):
        print("popup before: ", self.popup_gui_key)
        if(self.popup_gui_key == 0 or self.popup_gui_key == 2):
            if(self.masterPOPUP): # if we loose the window
                print("delete popup gui")
                self.masterPOPUP.destroy()
                self.masterPOPUP = None
                self.popup_gui_key = 0

            elif(self.masterPOPUP == None and self.popup_gui_key != 2):
                print("startup popup gui")
                self.masterPOPUP = Toplevel()
                self.masterPOPUP.protocol("WM_DELETE_WINDOW", self.on_closing_popup)
                self.masterPOPUP.geometry(f"{800}x{300}+{180}+{50}")
                self.masterPOPUP.title("POPUP")
                self.masterPOPUP.config(bg="#0033A0")

                # Create an entry for the camera index
                popup_label = Label(self.masterPOPUP, text="Popup Code Window" # + " " + self.binary_with_underscore(self.popup)
                                    ,bg="white", fg="black")
                popup_label.pack(ipadx=311, pady=5)
                popup_label.config(font=self.ui_font_debug)
                # self.popup_entry = Entry(self.masterPOPUP)
                # self.popup_entry.pack(ipadx=270, ipady=20)
                # self.popup_entry.config(font=self.ui_font_debug)
                options1 = ["Manual Mode", "Autonomy Mode"]

                self.masterPOPUP.option_add("*TCombobox*Listbox*Font", self.ui_font_debug)

                # Create a dropdown widget
                self.dropdown_1 = ttk.Combobox(self.masterPOPUP, values=options1, state="readonly", font=self.ui_font_debug)
                self.dropdown_1.pack(pady=6, ipadx=self.diag_w/self.reg_keys_drop)
                self.dropdown_1.bind("<<ComboboxSelected>>", self.handle_selection_man_or_auto)

                # options2 = ["Individual Control", "Drive Mode", "Excavate Mode", "Place Holder"]

                # # Create a dropdown widget
                # self.dropdown_2 = ttk.Combobox(self.masterPOPUP, values=options2, state="readonly", font=self.ui_font_debug)
                # self.dropdown_2.pack(pady=6, ipadx=self.diag_w/self.reg_keys_drop)
                # # self.dropdown_cam.bind("<<ComboboxSelected>>", self.handle_selection_cam)

                # options3 = ["Channel " + str(i) + " - " + self.channel_options[self.channel_config_naming[i]] for i in range(16)]

                # # Create a dropdown widget
                # self.dropdown_3 = ttk.Combobox(self.masterPOPUP, values=options3, state="readonly", font=self.ui_font_debug)
                # self.dropdown_3.pack(pady=6, ipadx=self.diag_w/self.reg_keys_drop)
                # self.dropdown_cam.bind("<<ComboboxSelected>>", self.handle_selection_cam)
                
                # Bind left mouse button click to open_dropdown function
                # self.dropdown_cam.bind("<Button-1>", self.open_dropdown_cam)

                self.button_popup = Button(self.masterPOPUP, text="OK", bg="#FFD100", fg="black", command=self.on_closing_popup)
                self.button_popup.pack(ipadx=150, ipady=40, pady=5)
                self.button_popup.config(font=self.ui_font_debug)

                # self.start_popup_clock_thread()

                self.popup_gui_key = 1
            
        print("popup after: ", self.popup_gui_key)

    def popup_gui_Loop(self):
        if(self.popup_gui_key == 1):
            # self.popup_entry.delete(0, 'end')
            # self.autonomy_manual = self.popup & 0x01
            # self.manual_mode = (self.popup >> 1) & 15
            # self.selected_channel = ((self.popup >> 5) & 15)  + 1
            # code               MChannel (4bits)  Mmode (4bits)   A or M (1bit)
            # if(autonomy_manual == 1): # autonomy
            #     self.popup_entry.insert(0, "Autonomy Mode Selected")
            # elif(autonomy_manual == 0): # manual
            #     if(manual_mode == 0): # mode for maunual to select individual channels
            #         self.popup_entry.insert(0, "Manual Mode Channel Selector Selected: Channel " + str(selected_channel) + " " + self.channel_options[self.channel_config_naming[selected_channel]])
            #     elif(manual_mode == 1):
            #         self.popup_entry.insert(0, "Manual Mode Drive")
            #     elif(manual_mode == 2):
            #         self.popup_entry.insert(0, "Manual Mode Excavate")
            #     elif(manual_mode == 3):
            #         self.popup_entry.insert(0, "Manual Mode Battery Swap")
            #     else:
            #         self.popup_entry.insert(0, "ME using software detected")
            self.masterPOPUP.update()

    def binary_with_underscore(self, n):
        binary = format(n, 'b')
        reversed_binary = binary[::-1]
        underscored = ''.join([reversed_binary[i] + ('_' if (i+1) % 4 == 0 else '') for i in range(len(reversed_binary))])
        return underscored[::-1]


    def popup_clk(self):
        value = 2
        for t in range (0, 500):
            time.sleep(0.01)
            if(self.popup_gui_key == 0):
                value = 0
                break

        print("times up!")
        with self.lock_popup_clock:
            self.popup_gui_key = value # Stoped by timmer

    def start_popup_clock_thread(self):
        self.popup_clock_thread = threading.Thread(target=self.popup_clk, name="popup clock thread")
        self.popup_clock_thread.daemon = True
        self.popup_clock_thread.start()

    # Functions for getting the cameras IPs
    def on_closing_IPs(self):
        self.masterIP.destroy()
        self.FirstCamIP = 0
        self.masterIP = None

    def connect(self):
        self.cam[0] = self.camera_entry1.get()
        self.cam[1] = self.camera_entry2.get()
        self.cam[2] = self.camera_entry3.get()
        self.cam[3] = self.camera_entry4.get()
        self.cam[4] = self.camera_entry5.get()
        self.cam[5] = self.camera_entry6.get()
        self.FirstCamIP = 1
        print("Camera 1: ", self.cam[0], "Camera 2: ", self.cam[1], "Camera 3: ", self.cam[2], "Camera 4: ", self.cam[3], "Camera 5: ", self.cam[4], "Camera 6: ", self.cam[5])
        self.configured_camera_IPs = True

    def write_connect(self):
        # write to file
        cam = [""] * 6
        with open(file_path_IP, 'w') as file:
            cam[0] = self.camera_entry1.get()
            cam[1] = self.camera_entry2.get()
            cam[2] = self.camera_entry3.get()
            cam[3] = self.camera_entry4.get()
            cam[4] = self.camera_entry5.get()
            cam[5] = self.camera_entry6.get()

            file.write("Camera 1: ")
            file.write(cam[0])
            file.write("\nCamera 2: ")
            file.write(cam[1])
            file.write("\nCamera 3: ")
            file.write(cam[2])
            file.write("\nCamera 4: ")
            file.write(cam[3])
            file.write("\nCamera 5: ")
            file.write(cam[4])
            file.write("\nCamera 6: ")
            file.write(cam[5])

    def read_connect(self):
        # read from file
        cam = [None] * 6
        camera_values = {}
        with open(file_path_IP, 'r') as file:
            for line in file:
                parts = line.split(": ")
                if len(parts) == 2:
                    camera_name = parts[0].strip()
                    value = parts[1].strip()
                    camera_values[camera_name] = value

        # Assign values to variables
        cam[0] = camera_values.get("Camera 1")
        cam[1] = camera_values.get("Camera 2")
        cam[2] = camera_values.get("Camera 3")
        cam[3] = camera_values.get("Camera 4")
        cam[4] = camera_values.get("Camera 5")
        cam[5] = camera_values.get("Camera 6")

        # delete previous entry
        self.camera_entry1.delete(0, 'end')  # Clear previous content
        self.camera_entry1.insert(0, cam[0])
        self.camera_entry2.delete(0, 'end')  # Clear previous content
        self.camera_entry2.insert(0, cam[1])
        self.camera_entry3.delete(0, 'end')  # Clear previous content
        self.camera_entry3.insert(0, cam[2])
        self.camera_entry4.delete(0, 'end')  # Clear previous content
        self.camera_entry4.insert(0, cam[3])
        self.camera_entry5.delete(0, 'end')  # Clear previous content
        self.camera_entry5.insert(0, cam[4])
        self.camera_entry6.delete(0, 'end')  # Clear previous content
        self.camera_entry6.insert(0, cam[5])

        # Print values
        print("Cam1:", cam[0])
        print("Cam2:", cam[1])
        print("Cam3:", cam[2])
        print("Cam4:", cam[3])
        print("Cam5:", cam[4])
        print("Cam6:", cam[5])

    def Get_Camera_IPs(self):
        self.FirstCamIP = 2

        if(self.masterIP): # if we loose the window
            self.masterIP.destroy()
            self.masterIP = None

        if(self.masterIP == None):
            self.masterIP = Toplevel()
            self.masterIP.protocol("WM_DELETE_WINDOW", self.on_closing_IPs)
            self.masterIP.geometry(f"{800}x{500}+{180}+{50}")
            self.masterIP.title("IP of Webcams")
            self.masterIP.config(bg="#0033A0")

            ipadx = 327.2
            pady = 5

            # Create an entry for the camera index
            camera_entry_label1 = Label(self.masterIP, text="Camera 1 IP", bg="white", fg="black")
            camera_entry_label1.pack(ipadx=ipadx, pady=pady)
            self.camera_entry1 = Entry(self.masterIP)
            self.camera_entry1.pack(ipadx=300, ipady=10)

            # Create an entry for the camera index
            camera_entry_label2 = Label(self.masterIP, text="Camera 2 IP", bg="white", fg="black")
            camera_entry_label2.pack(ipadx=ipadx, pady=pady)
            self.camera_entry2 = Entry(self.masterIP)
            self.camera_entry2.pack(ipadx=300, ipady=10)

            # Create an entry for the camera index
            camera_entry_label3 = Label(self.masterIP, text="Camera 3 IP", bg="white", fg="black")
            camera_entry_label3.pack(ipadx=ipadx, pady=pady)
            self.camera_entry3 = Entry(self.masterIP)
            self.camera_entry3.pack(ipadx=300, ipady=10)

            # Create an entry for the camera index
            camera_entry_label4 = Label(self.masterIP, text="Camera 4 IP", bg="white", fg="black")
            camera_entry_label4.pack(ipadx=ipadx, pady=pady)
            self.camera_entry4 = Entry(self.masterIP)
            self.camera_entry4.pack(ipadx=300, ipady=10)

            # Create an entry for the camera index
            camera_entry_label5 = Label(self.masterIP, text="Camera 5 IP", bg="white", fg="black")
            camera_entry_label5.pack(ipadx=ipadx, pady=pady)
            self.camera_entry5 = Entry(self.masterIP)
            self.camera_entry5.pack(ipadx=300, ipady=10)

            # Create an entry for the camera index
            camera_entry_label6 = Label(self.masterIP, text="Camera 6 IP", bg="white", fg="black")
            camera_entry_label6.pack(ipadx=ipadx, pady=pady)
            self.camera_entry6 = Entry(self.masterIP)
            self.camera_entry6.pack(ipadx=300, ipady=10)

            button = Button(self.masterIP, text="Save Camera IPs", bg="#FFD100", fg="black", command=self.write_connect)
            button.pack(side=LEFT, pady=20, ipadx=50, padx=50, ipady=2)

            button = Button(self.masterIP, text="Load Camera IPs", bg="#FFD100", fg="black", command=self.connect)
            button.pack(pady=20, side=LEFT, ipadx=50, ipady=2)

            button = Button(self.masterIP, text="Load Camera IPs From Save", bg="#FFD100", fg="black", command=self.read_connect)
            button.pack(side=RIGHT, pady=20, ipadx=50, padx=50, ipady=2)

    def Get_Camera_IPs_Loop(self):
        if(self.FirstCamIP == 2):
            self.masterIP.update()
        if(self.FirstCamIP == 1):
            self.masterIP.destroy()
            self.FirstCamIP = 0
            self.masterIP = None

    def ptz_controls(self):
        ptz = [ptzControl() for _ in range(self.number_of_cams)]

        ptzEnable = [False] * self.number_of_cams

        # camera selected previous
        prev_camera_selected = self.selected_camera
        current_camera_selected = self.selected_camera

        # first time through
        first = True

        while True:
            img = self.img
            # save previous
            prev_camera_selected = current_camera_selected
            # get current
            current_camera_selected = self.selected_camera

            # any time we transition we need to switch so change first to true.
            if(prev_camera_selected != current_camera_selected):
                first = True
                with self.lock_ptz:
                    self.ptz = None

            if(img is not None and first):
                ptzEnable[current_camera_selected] = ptz[current_camera_selected].ptz_setup(self.cam[current_camera_selected])
                first = False
                print("ptz setup")

                if(ptzEnable[current_camera_selected]):
                    print("ptz enable")
                    with self.lock_ptz:
                        self.ptz = ptz[current_camera_selected]
                else:
                    print("ptz disable")
                    with self.lock_ptz:
                        self.ptz = None
            elif(img is None and first):
                # print("ptz disable 1")
                with self.lock_ptz:
                    self.ptz = None

            time.sleep(0.1)

    def start_ptz_thread(self):
        self.ptz_thread = threading.Thread(target=self.ptz_controls, name="ptz_controller thread")
        self.ptz_thread.daemon = True
        self.ptz_thread.start()

    # opnecv thread
    def run_opencvCam(self):
        # connection
        connection = False
        ac = Amcrest_Camera()

        # images 
        img = None
        ret = None

        # camera selected previous
        current_camera_selected = self.selected_camera

        while True:
            # get current
            current_camera_selected = self.selected_camera

            if(self.mode == 1):
                if(current_camera_selected != self.opneCVCam):
                    # connect to camera if not already connected to the selected camera
                    if(connection == False):
                        connection = ac.VideoCapture(self.cam[self.opneCVCam])
                        print("opneCV Camera Created")
                    
                    # if connected to the camera and we are on camera zero, copy imgCV to img (both ai image and view image are the same)
                    if(connection):
                        ret, img = ac.read()
                    else:
                        ret = False


                    # if we got an image call er a day
                    if(connection):
                        if(ret):
                            with self.lock_camCV:
                                self.imgCV = img
                    else:
                        with self.lock_camCV:
                            self.imgCV = None

                        time.sleep(0.1)
                
                else:
                    if(connection):
                        ac.destroy()
                        connection = False
                    if(self.img is None):
                        img = None
                    else:
                        img = self.img.copy()
                    with self.lock_camCV:
                        self.imgCV = img

                    time.sleep(0.033) # 30fps
            else:
                with self.lock_camCV:
                    self.imgCV = None
                
                connection = False
                time.sleep(1)
                
    def start_cameraCV_thread(self):
        self.cameraCV_connect_thread = threading.Thread(target=self.run_opencvCam, name = "OpenCV thread")
        self.cameraCV_connect_thread.daemon = True
        self.cameraCV_connect_thread.start()

    # connecting to the camera and ptz
    def run_camera(self):
        # connection
        connection = [False] * self.number_of_cams
        ac = [Amcrest_Camera() for _ in range(self.number_of_cams)] 

        # images 
        img = [None] * self.number_of_cams
        ret = [None] * self.number_of_cams

        # camera selected previous
        prev_camera_selected = self.selected_camera
        current_camera_selected = self.selected_camera

        while True:
            if(self.configured_camera_IPs):
                # save previous
                prev_camera_selected = current_camera_selected
                # get current
                current_camera_selected = self.selected_camera
                # use the current and previous so that they don;t switch midway
                if(prev_camera_selected != current_camera_selected):
                    ac[prev_camera_selected].destroy()
                    connection[prev_camera_selected] = False




                # connect to camera if not already connected to the selected camera
                if(connection[current_camera_selected] == False): # connect if not connected to gui camera
                    connection[current_camera_selected] = ac[current_camera_selected].VideoCapture(self.cam[current_camera_selected])
                    print("camera created")
        




                # if connected to the camera and we are on camera zero, copy imgCV to img (both ai image and view image are the same)
                if(connection[current_camera_selected]):
                    ret[current_camera_selected], img[current_camera_selected] = ac[current_camera_selected].read()
                else:
                    ret[current_camera_selected] = False





                
                # if we got an image call er a day
                if(connection[current_camera_selected]):
                    if(ret[current_camera_selected]):
                        with self.lock_cam:
                            self.img = img[current_camera_selected]
                else:
                    with self.lock_cam:
                        self.img = None

                    time.sleep(0.1)






            else:
                with self.lock_cam:
                    self.img = None

                time.sleep(0.1)
                 

    def start_camera_thread(self):
        self.camera_connect_thread = threading.Thread(target=self.run_camera, name="camera_thread")
        self.camera_connect_thread.daemon = True
        self.camera_connect_thread.start()

    def change_cam_add(self):
        if(self.debounce_button == 0):
            if(self.selected_camera < 5):
                self.selected_camera = self.selected_camera + 1
            else:
                self.selected_camera = 0

            self.frame1.config(text="Camera Feed " + str(self.selected_camera+1))

            print("Camera Selected: ", self.selected_camera, "Camera Array: ", self.toggleCamera)

            self.debounce_button = 1
            self.start_debounce_thread() # debounce

    def change_cam_sub(self):
        if(self.debounce_button == 0):
            if(self.selected_camera > 0):
                self.selected_camera = self.selected_camera - 1
            else:
                self.selected_camera = 5

            self.frame1.config(text="Camera Feed " + str(self.selected_camera+1))

            print("Camera Selected: ", self.selected_camera, "Camera Array: ", self.toggleCamera)

            self.debounce_button = 1
            self.start_debounce_thread() # debounce

    def handle_selection_cam(self, event):
            selected_item = self.dropdown_cam.current()
            self.selected_camera = selected_item

            self.frame1.config(text="Camera Feed " + str(self.selected_camera))

            print("Camera Selected: ", self.selected_camera, "Camera Array: ", self.toggleCamera)

            print("Selected:", selected_item)

    def open_dropdown_cam(self, event=None):
        self.dropdown_cam.tk.call(self.dropdown_cam, 'set', '')  # Open the dropdown

    def debug(self):
        if(self.debounce_button == 0):
            if(self.debugger == 0):
                self.debugger = 1
            else:
                self.debugger = 0

            if(self.debugger == 1):  
                self.button2a.config(text=" Stop Debugging ")
                self.button2a.pack(ipadx=self.video_w/self.debugging_off)
            else:
                self.button2a.config(text="    Debugging    ")
                self.button2a.pack(ipadx=self.video_w/self.reg_keys)

            self.debounce_button = 1
            self.start_debounce_thread() # debounce

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
        self.battery_thread = threading.Thread(target=self.get_bat_data, name="battery_thread")
        self.battery_thread.daemon = True
        self.battery_thread.start()

    def get_bat_data_F(self):
        while True:
            total_voltage = np.array([round(random.uniform(0, 58.4), 2), round(random.uniform(0, 58.4), 2)])
            current = np.array([round(random.uniform(0, 40), 2), round(random.uniform(0, 40), 2)])
            power = self.total_voltage*self.current
            charging_power = np.array([random.choice([0, 1]), random.choice([0, 1])])
            discharging_power = self.power
            capacity_remaining = np.array([round(random.uniform(0, 100), 2), round(random.uniform(0, 100), 2)])
            nominal_capacity = 0
            charging_cycles = 0
            balancer_status_bitmask = 0
            errors_bitmask = 0
            software_version = 0
            state_of_charge = np.array([random.randint(0, 100), random.randint(0, 100)])
            operation_status_bitmask = 0
            battery_strings = 0
            temperature_1 = np.array([round(random.uniform(0, 90), 2), round(random.uniform(0, 90), 2)])
            temperature_2 = np.array([round(random.uniform(0, 90), 2), round(random.uniform(0, 90), 2)])
            temperature_3 = np.array([round(random.uniform(0, 90), 2), round(random.uniform(0, 90), 2)])
            cell_voltage_1 = 0
            cell_voltage_2 = 0
            cell_voltage_3 = 0
            cell_voltage_4 = 0
            cell_voltage_5 = 0
            cell_voltage_6 = 0
            cell_voltage_7 = 0
            cell_voltage_8 = 0
            cell_voltage_9 = 0
            cell_voltage_10 = 0
            cell_voltage_11 = 0
            cell_voltage_12 = 0
            cell_voltage_13 = 0
            cell_voltage_14 = 0
            cell_voltage_15 = 0
            cell_voltage_16 = 0
            min_cell_voltage = 0
            max_cell_voltage = 0
            max_voltage_cell = 0
            min_voltage_cell = 0
            delta_cell_voltage = 0
            average_cell_voltage = 0
            connection = np.array([random.choice([True, False]), random.choice([True, False])])

            time.sleep(0.1)

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

    def start_false_battery_thread(self):
        self.battery_thread_F = threading.Thread(target=self.get_bat_data_F, name="fake_battery_thread")
        self.battery_thread_F.daemon = True
        self.battery_thread_F.start()

    # channel select functions
    def on_closing(self):
        self.master.destroy()
        self.FirstChannelSelect = 0
        self.master = None

    def select_channels(self):
        self.FirstChannelSelect = 1
        for i in range(1, 17):
            selected_option = self.master.grid_slaves(row=(i-1)//4, column=(i-1)%4)[0].winfo_children()[1].cget("text")
            try:
                self.channel[i-1] = self.channel_option_to_arduino[int(self.channel_options.index(selected_option))]
                self.channel_config_naming[i-1] = int(self.channel_options.index(selected_option))
            except:
                self.channel[i-1] = -1
                self.channel_config_naming[i-1] = -1
        print(self.channel)
        print(self.channel_config_naming)

        if(self.board_batt == 1):
            options = ["Channel " + str(i) + " - " + self.channel_options[self.channel_config_naming[i]] for i in range(16)]
            options.append("Load Cells")

            # Create a dropdown widget
            self.dropdown.config(values=options)

        self.controls.set_act_OR_motor(config = self.channel)
        
    def write_select_channels(self):
        # write to file
        with open(file_path_Channel, 'w') as file:
            for i in range(1, 17):
                selected_option = self.master.grid_slaves(row=(i-1)//4, column=(i-1)%4)[0].winfo_children()[1].cget("text")
                file.write("Channel ")
                file.write(str(i))
                file.write(": ")
                file.write(selected_option)
                file.write("\n")

    def read_select_channels(self):
        # read from file
        channel_values = {}
        i = 0
        with open(file_path_Channel, 'r') as file:
            for line in file:
                parts = line.split(":")
                if len(parts) == 2:
                    channel_name = parts[0].strip()
                    value = parts[1].strip()
                    channel_values[i] = value
                    i = i + 1

        # Assign values to variables
        print(channel_values)

        for i in range(1, 17):
            self.selected_options[i-1].set(channel_values[i-1])
            # option_menu.children['menu'].entryconfig(0, label="IMU")

    def channel_select(self):
        self.FirstChannelSelect = 2

        if(self.master): # if we loose the window
            self.master.destroy()
            self.master = None

        if(self.master == None):
            self.master = Toplevel()
            self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.master.geometry(f"{1080}x{560}+{35}+{50}")
            self.master.title("Channel Selector")
            self.master.configure(bg="#0033A0")

            self.selected_options = [StringVar(self.master) for _ in range(16)]

            for i in range(1, 17):
                frame = Frame(self.master, borderwidth=2, relief="groove", width=300, height=300)
                frame.grid(row=(i-1)//4, column=(i-1)%4, padx=10, pady=10)

                label = Label(frame, text="Channel {}".format(i), width=15, height=6)
                label.grid(row=0, column=0)

                option_menu = OptionMenu(frame, self.selected_options[i-1], *self.channel_options)
                option_menu.grid(row=0, column=1)
                option_menu.config(width=15, height=5, bg="#FFD100")

                # Configure the font size of the dropdown menu
                popup_menu = self.master.nametowidget(option_menu.menuname)
                popup_menu.config(font=("Helvetica", 20))  # Adjust the font size as needed


            self.Save = Button(self.master, text="Save Config", command=self.write_select_channels)
            self.Save.grid(row=4, columnspan=1, pady=10)
            self.Save.config(width=20, height=2, bg="#FFD100")

            self.LOAD = Button(self.master, text="Load Config", command=self.select_channels)
            self.LOAD.grid(row=4, columnspan=4, pady=10)
            self.LOAD.config(width=20, height=2, bg="#FFD100")

            self.LOAD_Save = Button(self.master, text="Load Config From Save", command=self.read_select_channels)
            self.LOAD_Save.grid(row=4, column=3, pady=10)
            self.LOAD_Save.config(width=20, height=2, bg="#FFD100")

    def channel_select_loop(self):
        if(self.FirstChannelSelect == 2):
            self.master.update()
        if(self.FirstChannelSelect == 1):
            self.master.destroy()
            self.FirstChannelSelect = 0
            self.master = None
            # print(self.channel, "loop")
            # print(np.array([self.channel[0], self.channel[1], self.channel[2], self.channel[3], self.channel[4], self.channel[5], self.channel[6], self.channel[7], self.channel[8], self.channel[9], self.channel[10], self.channel[11], self.channel[12], self.channel[13], self.channel[14], self.channel[15]]))
            # controls.set_act_OR_motor(config = np.array([self.channel[0], self.channel[1], self.channel[2], self.channel[3], self.channel[4], self.channel[5], self.channel[6], self.channel[7], self.channel[8], self.channel[9], self.channel[10], self.channel[11], self.channel[12], self.channel[13], self.channel[14], self.channel[15]])) # have to do this otherwise weird stuff happens

    def get_channel_names(self):
        return self.channel_options
    
    def get_channel_setup_high_level(self):
        return self.channel_config_naming

    # battery stuff
    def change_batt_bard_add(self):
        if(self.debounce_button == 0):
            if(self.board_batt == 0):
                if(self.bms_numb == 0):
                    
                    self.bms_numb = 1
                else:
                    self.bms_numb = 0
                self.frame3.config(text="Battery Diagnostics BMS " + str(self.bms_numb))
                self.first = 1
            else:
                if(self.board_channel < 16):
                    self.board_channel = self.board_channel + 1
                else:
                    self.board_channel = 0

                if(self.board_channel == 16):
                    self.frame3.config(text="Load Cells")
                    self.first = 1
                else:
                    self.frame3.config(text="PCB Diagnostics Channel " + str(self.board_channel + 1) + " " + self.channel_options[self.channel_config_naming[self.board_channel]])
                    self.first = 1

            self.debounce_button = 1
            self.start_debounce_thread() # debounce

    def change_batt_bard_sub(self):
        if(self.debounce_button == 0):
            if(self.board_batt == 0):
                if(self.bms_numb == 0):
                    
                    self.bms_numb = 1
                else:
                    self.bms_numb = 0
                self.frame3.config(text="Battery Diagnostics BMS " + str(self.bms_numb))
                self.first = 1
            else:
                if(self.board_channel > 0):
                    self.board_channel = self.board_channel - 1
                else:
                    self.board_channel = 16
                
                if(self.board_channel == 16):
                    self.frame3.config(text="Load Cells")
                    self.first = 1
                else:
                    self.frame3.config(text="PCB Diagnostics Channel " + str(self.board_channel + 1) + " " + self.channel_options[self.channel_config_naming[self.board_channel]])
                    self.first = 1
            
            self.debounce_button = 1
            self.start_debounce_thread() # debounce

    def handle_selection(self, event):
            selected_item = self.dropdown.current()
            if(self.board_batt == 0):    # battery
                self.bms_numb = selected_item
                self.frame3.config(text="Battery Diagnostics BMS " + str(self.bms_numb))
                self.first = 1
            else:                       # pcb
                self.board_channel = selected_item
                
                if(self.board_channel == 16):
                    self.frame3.config(text="Load Cells")
                    self.first = 1
                else:
                    self.frame3.config(text="PCB Diagnostics Channel " + str(self.board_channel) + " " + self.channel_options[self.channel_config_naming[self.board_channel]])
                    self.first = 1
            print("Selected:", selected_item)

    def open_dropdown(self, event=None):
        self.dropdown.tk.call(self.dropdown, 'set', '')  # Open the dropdown

    def change_board_batt(self):
        if(self.debounce_button == 0):
            if(self.board_batt == 0):
                self.board_batt = 1
                options = ["Channel " + str(i) + " - " + self.channel_options[self.channel_config_naming[i]] for i in range(16)]
                options.append("Load Cells")
                # Create a dropdown widget
                self.dropdown.config(values=options)

                self.button7a.config(text="Battery")
                self.button7a.pack(ipadx=self.diag_w/self.diag_keys)
                self.button7a.config(font=self.ui_font_debug)
                self.first = 1
                if(self.board_channel == 16):
                    self.frame3.config(text="Load Cells")
                else:
                    self.frame3.config(text="PCB Diagnostics Channel " + str(self.board_channel) + " " + self.channel_options[self.channel_config_naming[self.board_channel]])
            else:
                self.board_batt = 0
                options = ["BMS 0 - dumptruck1", "BMS 1 - dumptruck2"]

                # Create a dropdown widget
                self.dropdown.config(values=options)
                self.button7a.config(text="PCB")
                self.button7a.pack(ipadx=self.diag_w/self.diag_keys)
                self.button7a.config(font=self.ui_font_debug)
                self.first = 1
                self.frame3.config(text="Battery Diagnostics BMS " + str(self.bms_numb))

            self.debounce_button = 1
            self.start_debounce_thread() # debounce

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

    def speedometer(self, screen, speed, value="V", name = "Battery Voltage", max_val = 70, high = 60, low = 40, x = BATTERY_X + BATTERY_WIDTH + 100, y = BATTERY_Y + BATTERY_HEIGHT // 2, fuse=0, r = 50):
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
            if(speed <= high):
                color = GREEN
            elif(speed <= high and speed > low):
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
        
    def speedometerINV(self, screen, speed, value="V", name = "Battery Voltage", max_val = 70, high = 60, low = 40, x = BATTERY_X + BATTERY_WIDTH + 100, y = BATTERY_Y + BATTERY_HEIGHT // 2, fuse=0, r = 50):
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
            if(speed <= low):
                color = RED
            elif(speed <= low and speed > high):
                color = YELLOW
            else:
                color = GREEN
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

    def draw_load(self, screen, value, units = "kg", text = "Battery Temperature", x = THERMOMETER_X, y = THERMOMETER_Y):
        # def draw_thermometer(self, screen, value, text = "Battery Temperature", x = THERMOMETER_X, y = THERMOMETER_Y):
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
        text_surface = self.font.render(str(value) + units, True, WHITE)
        text_rect = text_surface.get_rect(center=(x + 75 , y + 35))
        screen.blit(text_surface, text_rect)

        # Fill thermometer
        fill_rect = pygame.Rect(x + 1, y + THERMOMETER_HEIGHT - fill_height, THERMOMETER_WIDTH - 1, fill_height)
        pygame.draw.rect(screen, color, fill_rect)

    def draw_status(self, screen, on_off, x=0, y=0):
        if(on_off == 1):
            color = GREEN
        else:
            color = GRAY

        pygame.draw.circle(screen, color, (x, y+10), 20) 

    def draw_bad_status(self, screen, on_off, x=0, y=0):
        if(on_off == 1):
            color = RED
        else:
            color = GRAY

        pygame.draw.circle(screen, color, (x, y+10), 20) 

    def draw_status_text(self, screen, name="Connection Status", x=0, y=0):
        # text
        txt = self.font_small.render(name, True, WHITE)
        tet_rect = txt.get_rect(center=(x , y-30))
        screen.blit(txt, tet_rect)

    # show off battery data
    def diagnostics_data_pygames(self, diagnostics_array):
        # select numbs
        # 0 -> battery diagnostics, 1 -> motherboard, actuator, mother diagnostics

        # Check if one second has passed since the last call to update_battery_diagnostics()
        if time.time() - self.last_update_time >= 1 or self.first:
            # update the battery diagnostic data
            self.screenDiag.fill((0, 0, 0))
            if(self.board_batt == 0):
                self.draw_battery(self.screenDiag, int(self.state_of_charge[self.bms_numb]), self.charging_power[0] > 0.00, BATTERY_X + self.steps6/5, self.down_step)
                self.speedometer(self.screenDiag, round(self.total_voltage[self.bms_numb], 1), "V", "Battery Voltage", 100, 60, 40, BATTERY_X + BATTERY_WIDTH + self.steps6, self.down_step + BATTERY_HEIGHT // 2)
                self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Battery Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH + 2*self.steps6, self.down_step + BATTERY_HEIGHT // 2)
                self.speedometer(self.screenDiag, round(self.power[self.bms_numb], 1), "W", "Battery Power", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + 3*self.steps6, self.down_step + BATTERY_HEIGHT // 2)
                self.speedometerINV(self.screenDiag, round(self.capacity_remaining[self.bms_numb], 1), "Ah", "Battery Capacity", 120, 100, 50, BATTERY_X + BATTERY_WIDTH + 4*self.steps6, self.down_step + BATTERY_HEIGHT // 2)
                self.draw_thermometer(self.screenDiag, round((self.temperature_1[self.bms_numb] + self.temperature_2[self.bms_numb] + self.temperature_3[self.bms_numb]) / 3, 1), "Battery Temperature", BATTERY_X + BATTERY_WIDTH + 5*self.steps6, self.down_step - 30)
                self.draw_status_text(self.screenDiag, "Connection Status", BATTERY_X + BATTERY_WIDTH + 6*self.steps6, self.down_step)
            else:
                if(self.board_channel == 16):
                    if(self.false_traffic):
                        # 15, 14, 13, 12
                        # ALARM TEMP CURRENT OC_FAULT FEEDBACK, LOADCELL, OUT_TEMP
                        # dTempAndLC Channel# -> SPEED [#, #, #, #., ##, ###, ###, ?, ?, ?]
                        self.draw_load(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "kg", "Load Cell 1", BATTERY_X + BATTERY_WIDTH, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "kg", "Load Cell 2", BATTERY_X + BATTERY_WIDTH + self.steps3, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "kg", "Load Cell 3", BATTERY_X + BATTERY_WIDTH + 2*self.steps3, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "kg", "Load Cell 4", BATTERY_X + BATTERY_WIDTH + 3*self.steps3, self.down_step - 30)
                    else:
                        # diagnostics_array[self.board_channel, 2]
                        self.draw_load(self.screenDiag, round(diagnostics_array[12, 5], 1), "kg", "Load Cell 1", BATTERY_X + BATTERY_WIDTH, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(diagnostics_array[13, 5], 1), "kg", "Load Cell 2", BATTERY_X + BATTERY_WIDTH + self.steps3, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(diagnostics_array[14, 5], 1), "kg", "Load Cell 3", BATTERY_X + BATTERY_WIDTH + 2*self.steps3, self.down_step - 30)
                        self.draw_load(self.screenDiag, round(diagnostics_array[15, 5], 1), "kg", "Load Cell 4", BATTERY_X + BATTERY_WIDTH + 3*self.steps3, self.down_step - 30)

                elif(self.channel[self.board_channel] == 0): # motor
                    if(self.false_traffic):
                        self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Motor Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(self.power[self.bms_numb], 1), "m/s", "Motor Speed", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps5, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps5, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_1[self.bms_numb], 1), "Motor Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps5, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Motor Alarm", BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                    else:
                        # ALARM TEMP CURRENT OC_FAULT SPEED
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 2], 1), "A", "Motor Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 4], 1), "m/s", "Motor Speed", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps5, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 1], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps5, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 6], 1), "Motor Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps5, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Motor Alarm", BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, diagnostics_array[self.board_channel, 0], BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, diagnostics_array[self.board_channel, 3], BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                elif(self.channel[self.board_channel] == 1): # actuator
                    if(self.false_traffic):
                        self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Actuator Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(self.power[self.bms_numb], 1), "°", "Actuator Feedback", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps4, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps4, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_1[self.bms_numb], 1), "Actuator Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps4, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 4*self.steps4, self.down_step)
                        self.draw_bad_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 4*self.steps4, self.down_step)
                    else:
                        # TEMP CURRENT OC_FAULT FEEDBACK
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 1], 1), "A", "Actuator Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 3], 1), "°", "Actuator Feedback", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps4, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 0], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps4, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 6], 1), "Actuator Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps4, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 4*self.steps4, self.down_step)
                        self.draw_bad_status(self.screenDiag, diagnostics_array[self.board_channel, 2], BATTERY_X + BATTERY_WIDTH + 4*self.steps4, self.down_step)
                elif(self.channel[self.board_channel] == 2): # slewgear
                    if(self.false_traffic):
                        self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Slew Gear Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(self.power[self.bms_numb], 1), "°", "Slew Gear Feedback", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps5, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps5, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_1[self.bms_numb], 1), "Slew Gear Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps5, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Slew Gear Alarm", BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                    else:
                        # ALARM TEMP CURRENT OC_FAULT FEEDBACK, LOADCELL, OUT_TEMP
                        # dTempAndLC Channel# -> SPEED [#, #, #, #., ##, ###, ###, ?, ?, ?]
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 2], 1), "A", "Slew Gear Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH, self.down_step + BATTERY_HEIGHT // 2)
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 4], 1), "°", "Slew Gear Feedback", 4000, 3500, 1500, BATTERY_X + BATTERY_WIDTH + self.steps5, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 1], 1), "Board Temperature", BATTERY_X + BATTERY_WIDTH + 2*self.steps5, self.down_step - 30)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 6], 1), "Slew Gear Temperature", BATTERY_X + BATTERY_WIDTH + 3*self.steps5, self.down_step - 30)
                        self.draw_status_text(self.screenDiag, "Slew Gear Alarm", BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, diagnostics_array[self.board_channel, 0], BATTERY_X + BATTERY_WIDTH + 4*self.steps5, self.down_step)
                        self.draw_status_text(self.screenDiag, "Overcurrent Fault", BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                        self.draw_bad_status(self.screenDiag, diagnostics_array[self.board_channel, 3], BATTERY_X + BATTERY_WIDTH + 5*self.steps5, self.down_step)
                elif(self.channel[self.board_channel] == 3):
                    if(self.false_traffic):
                        # Motherboard Channel#                 you get this: ALARM TEMP CURRENT OC_FAULT
                        self.speedometer(self.screenDiag, round(self.current[self.bms_numb], 1), "A", "Motherboard Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH + self.steps1/2, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(self.temperature_2[self.bms_numb], 1), "Motherboard Temperature", BATTERY_X + BATTERY_WIDTH + self.steps1, self.down_step - 30)
                    else:
                        # Motherboard Channel#                 you get this: ALARM TEMP CURRENT OC_FAULT
                        self.speedometer(self.screenDiag, round(diagnostics_array[self.board_channel, 2], 1), "A", "Motherboard Current", 120, 100, 60, BATTERY_X + BATTERY_WIDTH + self.steps1/2, self.down_step + BATTERY_HEIGHT // 2)
                        self.draw_thermometer(self.screenDiag, round(diagnostics_array[self.board_channel, 1], 1), "Motherboard Temperature", BATTERY_X + BATTERY_WIDTH + self.steps1, self.down_step - 30)

            self.last_update_time = time.time()  # Update the last update time

            self.first = 0

        if(self.board_batt == 0):
            self.draw_status(self.screenDiag, self.connection[self.bms_numb], BATTERY_X + BATTERY_WIDTH + 6*self.steps6, self.down_step)

    # positioning
    def change_right_side(self):
        if(self.debounce_button == 0):
            if(self.position_IMU == 0):
                self.position_IMU = 1
                self.frame2.config(text="IMU")
                self.button3.destroy()
                self.button4.destroy()
                self.cameraC.destroy()

                # calibrate IMU
                self.cameraC = Button(self.frame2, text="Calibrate IMU", bg="#FFD100", fg="black")
                self.cameraC.pack(side=LEFT, ipadx=self.local_w/self.calib_imu)
                self.cameraC.config(font=self.ui_font)
            else:
                self.position_IMU = 0
                self.cameraC.destroy()
                self.frame2.config(text="Positioning")
                # + and - for positioning
                self.button4 = Button(self.frame2, text="+", bg="#FFD100", fg="black")
                self.button4.pack(side=LEFT, ipadx=self.local_w/self.reg_keys)
                self.button4.bind("<ButtonPress>", lambda event: self.up_p())
                self.button4.bind("<ButtonRelease>", lambda event: self.up_r())
                self.button4.config(font=self.ui_font)


                self.button3 = Button(self.frame2, text="-", bg="#FFD100", fg="black")
                self.button3.pack(side=LEFT, ipadx=self.local_w/self.reg_keys)
                self.button3.bind("<ButtonPress>", lambda event: self.down_p())
                self.button3.bind("<ButtonRelease>", lambda event: self.down_r())
                self.button3.config(font=self.ui_font)

                # calibrate localization
                self.cameraC = Button(self.frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
                self.cameraC.pack(side=LEFT, ipadx=self.local_w/self.calib_local)
                self.cameraC.bind("<ButtonPress>", lambda event: self.calibrate_map_p())
                self.cameraC.bind("<ButtonRelease>", lambda event: self.calibrate_map_r())
                self.cameraC.config(font=self.ui_font)
            
            self.debounce_button = 1
            self.start_debounce_thread() # debounce

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
        self.video_h = int(self.screen_height/1.43) # 480
        self.local_w = self.screen_width - 200 - self.video_w
        self.local_h = self.video_h
        self.diag_w = self.screen_width - 40
        self.diag_h = self.screen_height - self.video_h - 190

        print("Screen Width: ", self.screen_width)
        print("Screen Height: ", self.screen_height)

        print("Screen Width: ", self.video_w)
        print("Screen Height: ", self.video_h)

        print("Screen Width: ", self.local_w)
        print("Screen Height: ", self.local_h)

        root.destroy()

        return self.video_w, self.video_h, self.local_w + 132, self.local_h

    # ptz camera stuff
    def update_ptz(self, pan_right, pan_left, tilt_up, tilt_down, zoom_in, zoom_out):
        if(self.ptz is not None):
            if(self.pan_right is not pan_right or self.pan_left is not pan_left or self.tilt_up is not tilt_up or self.tilt_down is not tilt_down or self.zoom_in is not zoom_in or self.zoom_out is not zoom_out):
                if(pan_left):
                    self.ptz.move_pan(-1)
                    self.ptz.zoom(0)
                elif(pan_right):
                    self.ptz.move_pan(1)
                    self.ptz.zoom(0)
                elif(tilt_up):
                    self.ptz.move_tilt(1)
                    self.ptz.zoom(0)
                elif(tilt_down):
                    self.ptz.move_tilt(-1)
                    self.ptz.zoom(0)
                elif(zoom_in):
                    self.ptz.zoom(1)
                    self.ptz.move_tilt(0)
                    self.ptz.move_pan(0)
                elif(zoom_out):
                    self.ptz.zoom(-1)
                    self.ptz.move_tilt(0)
                    self.ptz.move_pan(0)
                else:
                    self.ptz.stop()

        self.pan_right = pan_right
        self.pan_left = pan_left
        self.tilt_up = tilt_up
        self.tilt_down = tilt_down
        self.zoom_in = zoom_in
        self.zoom_out = zoom_out

    # start_debugger
    def start_debugger(self):
        self.prev_time = time.time()

    # loop debugger
    def loop_debugger(self, img):
        # print fps on img
        curr_time = time.time()
        elapsed_time = curr_time - self.prev_time
        fps_text = "FPS: {:.2f}".format(1.0 / elapsed_time)
        cv2.putText(img, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        self.prev_time = curr_time

        # print snmp on image
        
    def debounce_buttons(self):
        time.sleep(0.05)
        with self.lock_debounce:
            self.debounce_button = 0

    def start_debounce_thread(self):
        self.debounce = threading.Thread(target=self.debounce_buttons, name="debounce thread")
        self.debounce.daemon = True
        self.debounce.start()

    # setup for main gui
    def set_up_Main_UI(self, battery, false_traffic=False, fullscreen = True):
        self.false_traffic = false_traffic
        self.battery = battery

        self.root = Tk()
        if fullscreen:
            self.root.attributes('-fullscreen', True)
        self.root.geometry("{}x{}".format(self.screen_width, self.screen_height))
        self.root.title("Main GUI")
        self.root.config(bg="#2c3e50")
        # padding
        padx = 5
        pady = 5

        # Create a black image
        self.black_image_video = Image.new("RGB", (self.video_w, self.video_h), "black")
        self.black_image_right = Image.new("RGB", (self.local_w + 130, self.local_h), "black")
        self.black_image_diag = Image.new("RGB", (self.diag_w, self.diag_h), "black")

        # Convert the Image to PhotoImage
        self.black_image_video_tk = ImageTk.PhotoImage(self.black_image_video)
        self.black_image_right_tk = ImageTk.PhotoImage(self.black_image_right)
        self.black_image_diag_tk = ImageTk.PhotoImage(self.black_image_diag)

        # Create a frame for the first two LabelFrames and use pack (video feed and map)
        frame_container1 = Frame(self.root, bg="#0033A0")
        frame_container1.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # video feed
        # Create the first LabelFrame stacked horizontally using pack
        self.frame1 = LabelFrame(frame_container1, text="Camera Feed 1", padx=padx, pady=pady)
        self.frame1.pack(side=LEFT, padx=padx, pady=pady)

        self.label1 = Label(self.frame1, bg="black")
        self.label1.pack()

        self.label1['image'] = self.black_image_video_tk

        # # move camera left and right
        # button2 = Button(self.frame1, text="        <        ", bg="#FFD100", fg="black", command=self.change_cam_sub)
        # button2.pack(side=LEFT, ipadx=self.video_w/self.reg_keys)
        # button2.config(font=self.ui_font)

        # button1 = Button(self.frame1, text="        >        ", bg="#FFD100", fg="black", command=self.change_cam_add)
        # button1.pack(side=LEFT, ipadx=self.video_w/self.reg_keys)
        # button1.config(font=self.ui_font)

        options = ["Camera 0 - Mining or Arm", "Camera 1 - Front", "Camera 2 - Back", "Camera 3 - Left", "Camera 4 - Right", "Camera 5 - Place Holder"]

        self.frame1.option_add("*TCombobox*Listbox*Font", self.ui_font_debug)

        # Create a dropdown widget
        self.dropdown_cam = ttk.Combobox(self.frame1, values=options, state="readonly", font=self.ui_font_debug)
        self.dropdown_cam.current(self.selected_camera)  # Set the default value to the first item (index 0)
        self.dropdown_cam.pack(side=LEFT, ipady=6, ipadx=self.diag_w/self.reg_keys_drop)
        self.dropdown_cam.bind("<<ComboboxSelected>>", self.handle_selection_cam)
        
        # Bind left mouse button click to open_dropdown function
        # self.dropdown_cam.bind("<Button-1>", self.open_dropdown_cam)

        self.button2a = Button(self.frame1, text="    Debugging    ", bg="#FFD100", fg="black", command=self.debug)
        self.button2a.pack(side=LEFT, ipadx=self.video_w/self.reg_keys)
        self.button2a.config(font=self.ui_font)

        self.button1a = Button(self.frame1, text="Configure Camera ", bg="#FFD100", fg="black", command=self.Get_Camera_IPs)
        self.button1a.pack(side=LEFT, ipadx=self.video_w/self.reg_keys)
        self.button1a.config(font=self.ui_font)
      
        # mapping
        # Create the second LabelFrame stacked horizontally using pack
        self.frame2 = LabelFrame(frame_container1, text="Positioning", padx=padx, pady=pady)
        self.frame2.pack(side=LEFT, padx=padx, pady=pady)

        self.label2 = Label(self.frame2, bg="black")
        self.label2.pack()

        # change right side view
        button5 = Button(self.frame2, text=">", bg="#FFD100", fg="black", command=self.change_right_side)
        button5.pack(side=RIGHT, ipadx=self.local_w/self.reg_keys)
        button5.config(font=self.ui_font)

        button6 = Button(self.frame2, text="<", bg="#FFD100", fg="black", command=self.change_right_side)
        button6.pack(side=RIGHT, ipadx=self.local_w/self.reg_keys)
        button6.config(font=self.ui_font)

        # + and - for positioning
        self.button4 = Button(self.frame2, text="+", bg="#FFD100", fg="black")
        self.button4.pack(side=LEFT, ipadx=self.local_w/self.reg_keys)
        self.button4.bind("<ButtonPress>", lambda event: self.up_p())
        self.button4.bind("<ButtonRelease>", lambda event: self.up_r())
        self.button4.config(font=self.ui_font)


        self.button3 = Button(self.frame2, text="-", bg="#FFD100", fg="black")
        self.button3.pack(side=LEFT, ipadx=self.local_w/self.reg_keys)
        self.button3.bind("<ButtonPress>", lambda event: self.down_p())
        self.button3.bind("<ButtonRelease>", lambda event: self.down_r())
        self.button3.config(font=self.ui_font)

        # calibrate localization
        self.cameraC = Button(self.frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
        self.cameraC.pack(side=LEFT, ipadx=self.local_w/self.calib_local)
        self.cameraC.bind("<ButtonPress>", lambda event: self.calibrate_map_p())
        self.cameraC.bind("<ButtonRelease>", lambda event: self.calibrate_map_r())
        self.cameraC.config(font=self.ui_font)

        # diagnostic data
        # Create a frame for the third LabelFrame and use pack
        frame_container2 = Frame(self.root, bg="#0033A0")
        frame_container2.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # Create the third LabelFrame below the first two using pack
        self.frame3 = LabelFrame(frame_container2, text="Battery Diagnostics BMS " + str(self.bms_numb), padx=padx, pady=pady, bg="white")
        self.frame3.pack(side=LEFT, padx=padx, pady=pady)

        self.label3 = Label(self.frame3, bg="black")
        self.label3.pack()

        self.label3['image'] = self.black_image_diag_tk
        
        # # change battery diagnostics
        # button8 = Button(self.frame3, text="<", bg="#FFD100", fg="black", command=self.change_batt_bard_sub)
        # button8.pack(side=LEFT, ipadx=self.diag_w/self.diag_keys)
        # button8.config(font=self.ui_font_debug)

        # button7 = Button(self.frame3, text=">", bg="#FFD100", fg="black", command=self.change_batt_bard_add)
        # button7.pack(side=LEFT, ipadx=self.diag_w/self.diag_keys)
        # button7.config(font=self.ui_font_debug)

        # Create a list of options
        options = ["BMS 0 - dumptruck1", "BMS 1 - dumptruck2"]

        self.frame3.option_add("*TCombobox*Listbox*Font", self.ui_font_debug)

        # Create a dropdown widget
        self.dropdown = ttk.Combobox(self.frame3, values=options, state="readonly", font=self.ui_font_debug)
        self.dropdown.current(self.bms_numb)
        self.dropdown.pack(side=LEFT, ipady=10, ipadx=self.diag_w/self.diag_drop_down)
        self.dropdown.bind("<<ComboboxSelected>>", self.handle_selection)
        
        # Bind left mouse button click to open_dropdown function
        # self.dropdown.bind("<Button-1>", self.open_dropdown)


        # def handle_selection(event):
        #     selected_item = dropdown.get()
        #     print("Selected:", selected_item)

        # # Create a list of options
        # options = ["Option 1", "Option 2", "Option 3", "Option 4"]

        # # Create a dropdown widget
        # dropdown = ttk.Combobox(self.frame3, values=options)
        # dropdown.pack(side=LEFT, ipady=10, ipadx=self.diag_w/self.diag_drop_down)
        # dropdown.config(font=self.ui_font_debug)
        # dropdown.bind("<<ComboboxSelected>>", handle_selection)

        self.button7a = Button(self.frame3, text="PCB", bg="#FFD100", fg="black", command=self.change_board_batt)
        self.button7a.pack(side=LEFT, ipadx=self.diag_w/self.diag_keys)
        self.button7a.config(font=self.ui_font_debug)

        button9 = Button(self.frame3, text="Channel Selector", bg="#FFD100", fg="black", command=self.channel_select)
        button9.pack(side=RIGHT, ipadx=self.diag_w/self.diag_keys)
        button9.config(font=self.ui_font_debug)

        if(not false_traffic):
            # start battery thread
            self.start_bat_thread()
        else:
            self.start_false_battery_thread()

        # start camera thread
        self.start_camera_thread()
        self.start_cameraCV_thread()
        self.start_ptz_thread()
    
        # battery display
        self.screenDiag = self.init_pygame()
            
        # intitalize the previous bms
        self.prev_bms = self.bms_numb

        # Initialize a variable to track the last time update_battery_diagnostics() was called
        self.last_update_time = time.time()

        self.first = 1

        self.steps6 = int(self.diag_w/7.5)
        self.steps5 = int(self.diag_w/6)
        self.steps4 = int(self.diag_w/5)
        self.steps3 = int(self.diag_w/4)
        self.steps1 = int(self.diag_w/2)
        self.down_step = int(self.diag_h/2.5)

        self.start_debugger()

    # loop function for main gui
    def loop_Main_UI(self, controls, local_img, mode = 0, imu_image = None, popup = 0):
        self.mode = mode
        self.controls = controls
        self.popup = popup
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.root.quit()


        # get the camera feed
        if self.img is not None:
            cv_img = self.img
            if cv_img is not None:
                img1 = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                img2 = cv2.resize(img1, (self.video_w, self.video_h))
                if self.debugger == 1:
                    self.loop_debugger(img2)
                img = ImageTk.PhotoImage(Image.fromarray(img2))
                self.label1['image'] = img
            else:
                self.label1['image'] = self.black_image_video_tk
        else:
            self.label1['image'] = self.black_image_video_tk

        # Check if one second has passed since the last call to update_battery_diagnostics()
        self.diagnostics_data_pygames(controls.get_diagnostics_array())

        # update diagnostics UI
        img_3 = self.update_pygames_screen(self.screenDiag)
        self.label3['image'] = img_3

        # choose between IMU and localization
        if(self.position_IMU == 0):
            # end, img_2 = localization.update_pygames_screen()
            self.label2['image'] = local_img
        else:
            if(imu_image == None):
                self.label2['image'] = self.black_image_right_tk
            else:
                self.label2['image'] = imu_image

        # check controls
        self.update_ptz(controls.Get_Button_From_Controller("Dpad_Right"), controls.Get_Button_From_Controller("Dpad_Left"), controls.Get_Button_From_Controller("Dpad_Up"), controls.Get_Button_From_Controller("Dpad_Down"), controls.Get_Button_From_Controller("R1_Button"), controls.Get_Button_From_Controller("L1_Button"))

        # update UI
        self.root.update()

        # update IP loop
        self.Get_Camera_IPs_Loop()

        # update channel select
        self.channel_select_loop()

        if(self.popup != self.prev_popup or self.popup_gui_key == 2):
            
            if(self.popup != self.prev_popup):
                self.popup_gui_key = 0
                self.popup_gui()
            
            # setup previous
            self.prev_popup = self.popup

            # run popups
            self.popup_gui()
        self.popup_gui_Loop()

        if(self.popup_gui_key == 0):
            self.manual_mode_lock = self.manual_mode
            self.autonomy_manual_lock = self.autonomy_manual
            self.selected_channel_lock = self.selected_channel

        return self.imgCV, self.position_IMU, self.calibrateM, self.up_key, self.down_key, self.manual_mode_lock, self.autonomy_manual_lock, self.selected_channel_lock

    def release_main(self):
        self.cap.release()
        self.root.destroy()