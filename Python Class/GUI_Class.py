import cv2
from tkinter import *
from PIL import Image, ImageTk
import time
import threading
import os
import pygame
import numpy as np

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
        self.toggleCamera = 0

        self.cap1 = None
        self.cap2 = None
        self.cap3 = None
        self.cap4 = None
        self.cap5 = None
        self.cap6 = None

        self.img1 = None
        self.img2 = None
        self.img3 = None
        self.img4 = None
        self.img5 = None
        self.img6 = None

        self.first_camera = 0

        self.total_voltage = 0
        self.current = 0
        self.power = 0
        self.charging_power = 0
        self.discharging_power = 0
        self.capacity_remaining = 0
        self.nominal_capacity = 0
        self.charging_cycles = 0
        self.balancer_status_bitmask = 0
        self.errors_bitmask = 0
        self.software_version = 0
        self.state_of_charge = 0
        self.operation_status_bitmask = 0
        self.battery_strings = 0
        self.temperature_1 = 0
        self.temperature_2 = 0
        self.temperature_3 = 0
        self.cell_voltage_1 = 0
        self.cell_voltage_2 = 0
        self.cell_voltage_3 = 0
        self.cell_voltage_4 = 0
        self.cell_voltage_5 = 0
        self.cell_voltage_6 = 0
        self.cell_voltage_7 = 0
        self.cell_voltage_8 = 0
        self.cell_voltage_9 = 0
        self.cell_voltage_10 = 0
        self.cell_voltage_11 = 0
        self.cell_voltage_12 = 0
        self.cell_voltage_13 = 0
        self.cell_voltage_14 = 0
        self.cell_voltage_15 = 0
        self.cell_voltage_16 = 0
        self.min_cell_voltage = 0
        self.max_cell_voltage = 0
        self.max_voltage_cell = 0
        self.min_voltage_cell = 0
        self.delta_cell_voltage = 0
        self.average_cell_voltage = 0

        self.lock_bat = threading.Lock()
        self.lock_cam1 = threading.Lock()
        self.lock_cam2 = threading.Lock()
        self.lock_cam3 = threading.Lock()
        self.lock_cam4 = threading.Lock()
        self.lock_cam5 = threading.Lock()
        self.lock_cam6 = threading.Lock()

    def Get_Camera_IPs(self):
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
            
        print(self.cam1, self.cam2, self.cam3, self.cam4, self.cam5, self.cam6)

        root.destroy()

    def Main_UI(self, battery, localization, distance):
        # intitalizing the GUI
        root = Tk()
        root.geometry("1350x720")
        root.title("Main GUI")
        root.config(bg="#2c3e50")

        # window size
        width_image = 640
        height_image = 380
        padx = 5
        pady = 5

        # Create a black image
        black_image = Image.new("RGB", (width_image, height_image), "black")

        # Convert the Image to PhotoImage
        black_image_tk = ImageTk.PhotoImage(black_image)

        def toggle():   
            if(self.toggleCamera == 0): # turn on camera
                if(self.first_camera == 0):
                    self.cap1 = cv2.VideoCapture(int(self.cam1))
                    self.cap = self.cap1
                elif(self.first_camera == 1):
                    self.cap2 = cv2.VideoCapture(int(self.cam2))
                    self.cap = self.cap2
                elif(self.first_camera == 2):
                    self.cap3 = cv2.VideoCapture(self.cam3)
                    self.cap = self.cap3
                elif(self.first_camera == 3):
                    self.cap4 = cv2.VideoCapture(self.cam4)
                    self.cap = self.cap4
                elif(self.first_camera == 4):
                    self.cap5 = cv2.VideoCapture(self.cam5)
                    self.cap = self.cap5
                else:
                    self.cap6 = cv2.VideoCapture(self.cam6)
                    self.cap = self.cap6
                # toggle stuff
                self.toggleCamera = 1
                button_text = "Disconnect Camera"
            else:
                # self.cap.release()
                self.cap = None
                self.toggleCamera = 0
                button_text = "Connect Camera"

            cameraB.config(text=button_text)

        def change_cam_add():
            if(self.first_camera < 5):
                self.first_camera = self.first_camera + 1
            else:
                self.first_camera = 0

            if(self.first_camera == 0):
                self.cap = self.cap1
            elif(self.first_camera == 1):
                self.cap = self.cap2
            elif(self.first_camera == 2):
                self.cap = self.cap3
            elif(self.first_camera == 3):
                self.cap = self.cap4
            elif(self.first_camera == 4):
                self.cap = self.cap5
            else:
                self.cap = self.cap6

            if(self.cap is None):
                cameraB.config(text="Connect Camera")
                self.toggleCamera = 0
            else:
                cameraB.config(text="Disconnect Camera")
                self.toggleCamera = 1

            frame1.config(text="Camera Feed " + str(self.first_camera+1))

            print(self.first_camera, self.toggleCamera)

        def change_cam_sub():
            if(self.first_camera > 0):
                self.first_camera = self.first_camera - 1
            else:
                self.first_camera = 5

            if(self.first_camera == 0):
                self.cap = self.cap1
            elif(self.first_camera == 1):
                self.cap = self.cap2
            elif(self.first_camera == 2):
                self.cap = self.cap3
            elif(self.first_camera == 3):
                self.cap = self.cap4
            elif(self.first_camera == 4):
                self.cap = self.cap5
            else:
                self.cap = self.cap6

            if(self.cap is None):
                cameraB.config(text="Connect Camera")
                self.toggleCamera = 0
            else:
                cameraB.config(text="Disconnect Camera")
                self.toggleCamera = 1

            frame1.config(text="Camera Feed " + str(self.first_camera+1))

            print(self.first_camera, self.toggleCamera)

        # Create a frame for the first two LabelFrames and use pack (video feed and map)
        frame_container1 = Frame(root, bg="#0033A0")
        frame_container1.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # video feed
        # Create the first LabelFrame stacked horizontally using pack
        frame1 = LabelFrame(frame_container1, text="Camera Feed 1", padx=padx, pady=pady)
        frame1.pack(side=LEFT, padx=padx, pady=pady)

        label1 = Label(frame1, bg="black")
        label1.pack()

        label1['image'] = black_image_tk

        # move camera left and right
        button2 = Button(frame1, text="<", bg="#FFD100", fg="black", command=change_cam_sub)
        button2.pack(side=LEFT)

        button1 = Button(frame1, text=">", bg="#FFD100", fg="black", command=change_cam_add)
        button1.pack(side=LEFT)

        # connect camera button
        button_text = "Connect Camera" if self.toggleCamera == 0 else "Disconnect Camera"
        cameraB = Button(frame1, text=button_text, bg="#FFD100", fg="black", command=toggle)
        cameraB.pack(side=LEFT, padx=230)

        self.calibrateM = 0

        def calibrate_map_p():
            self.calibrateM = 1

        def calibrate_map_r():
            self.calibrateM = 0

        self.up_key = 0

        def up_p():
            self.up_key = 1
        
        def up_r():
            self.up_key = 0

        self.down_key = 0

        def down_p():
            self.down_key = 1
        
        def down_r():
            self.down_key = 0
            
        # mapping
        # Create the second LabelFrame stacked horizontally using pack
        frame2 = LabelFrame(frame_container1, text="Positioning", padx=padx, pady=pady)
        frame2.pack(side=LEFT, padx=padx, pady=pady)

        label2 = Label(frame2, bg="black")
        label2.pack()

        # + and - for positioning
        button4 = Button(frame2, text="+", bg="#FFD100", fg="black")
        button4.pack(side=LEFT)
        button4.bind("<ButtonPress>", lambda event: up_p())
        button4.bind("<ButtonRelease>", lambda event: up_r())


        button3 = Button(frame2, text="-", bg="#FFD100", fg="black")
        button3.pack(side=LEFT)
        button3.bind("<ButtonPress>", lambda event: down_p())
        button3.bind("<ButtonRelease>", lambda event: down_r())

        # calibrate localization
        cameraC = Button(frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
        cameraC.pack(side=LEFT, padx=230)
        cameraC.bind("<ButtonPress>", lambda event: calibrate_map_p())
        cameraC.bind("<ButtonRelease>", lambda event: calibrate_map_r())

        # diagnostic data
        # Create a frame for the third LabelFrame and use pack
        frame_container2 = Frame(root, bg="#0033A0")
        frame_container2.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

        # Create the third LabelFrame below the first two using pack
        frame3 = LabelFrame(frame_container2, text="Battery Diagnostics", padx=padx, pady=pady, bg="#0033A0", fg="white")
        frame3.pack(side=LEFT, padx=padx, pady=pady)

        # Define the number of rows and columns
        num_rows = 3
        num_columns = 9

        def format_voltage(value):
            return f"{value:.3f} V"

        def format_temperature(value):
            return f"{value:.1f} °C"

        def format_current(value):
            return f"{value:.3f} A"

        def format_power(value):
            return f"{value:.3f} W"

        def format_capacity(value):
            return f"{value:.2f} Ah"

        def format_percent(value):
            return f"{value:.0f} %"

        def format_unitless(value):
            return f"{value:.0f}"

        def print_out(float_val, type_val=None):
            value = StringVar()
            if(type_val == "V"):
                value.set(format_voltage(float_val))
            elif(type_val == "T"):
                value.set(format_temperature(float_val))
            elif(type_val == "I"):
                value.set(format_current(float_val))
            elif(type_val == "W"):
                value.set(format_power(float_val))
            elif(type_val == "C"):
                value.set(format_capacity(float_val))
            elif(type_val == "P"):
                value.set(format_percent(float_val))
            else:
                value.set(format_unitless(float_val))

            return value

        # Create LabelFrames and Entries in a grid layout
        label_frames = [
            ("Total Voltage: ", print_out(self.total_voltage, "V")),
            ("Current: ", print_out(self.current, "I")),
            ("Power: ", print_out(self.power, "W")),
            ("Charging Power: ", print_out(self.charging_power, "W")),
            ("Discharging Power: ", print_out(self.discharging_power, "W")),
            ("Capacity Remaining: ", print_out(self.capacity_remaining, "C")),
            ("Nominal Capacity: ", print_out(self.nominal_capacity, "C")),
            ("Charging Cycles: ", print_out(self.charging_cycles)),
            ("State of Charge: ", print_out(self.state_of_charge, "P")),
            ("Temperature 1: ", print_out(self.temperature_1, "T")),
            ("Temperature 2: ", print_out(self.temperature_2, "T")),
            ("Temperature 3: ", print_out(self.temperature_3, "T")),
            ("Cell Voltage 1: ", print_out(self.cell_voltage_1, "V")),
            ("Cell Voltage 2: ", print_out(self.cell_voltage_2, "V")),
            ("Cell Voltage 3: ", print_out(self.cell_voltage_3, "V")),
            ("Cell Voltage 4: ", print_out(self.cell_voltage_4, "V")),
            ("Cell Voltage 5: ", print_out(self.cell_voltage_5, "V")),
            ("Cell Voltage 6: ", print_out(self.cell_voltage_6, "V")),
            ("Cell Voltage 7: ", print_out(self.cell_voltage_7, "V")),
            ("Cell Voltage 8: ", print_out(self.cell_voltage_8, "V")),
            ("Cell Voltage 9: ", print_out(self.cell_voltage_9, "V")),
            ("Cell Voltage 10: ", print_out(self.cell_voltage_10, "V")),
            ("Cell Voltage 11: ", print_out(self.cell_voltage_11, "V")),
            ("Cell Voltage 12: ", print_out(self.cell_voltage_12, "V")),
            ("Cell Voltage 13: ", print_out(self.cell_voltage_13, "V")),
            ("Cell Voltage 14: ", print_out(self.cell_voltage_14, "V")),
            ("Cell Voltage 15: ", print_out(self.cell_voltage_15, "V")),
            ("Cell Voltage 16: ", print_out(self.cell_voltage_16, "V")),
            ("Min Cell Voltage: ", print_out(self.min_cell_voltage, "V")),
            ("Max Cell Voltage: ", print_out(self.max_cell_voltage, "V")),
            ("Max Voltage Cell: ", print_out(self.max_voltage_cell, "V")),
            ("Min Voltage Cell: ", print_out(self.min_voltage_cell, "V")),
            ("Delta Cell Voltage: ", print_out(self.delta_cell_voltage, "V")),
            ("Average Cell Voltage: ", print_out(self.average_cell_voltage, "V")),
        ]

        self.entrys = []

        for i, (label_text, text_var) in enumerate(label_frames):
            row_num = i // num_columns
            col_num = i % num_columns

            label_frame = LabelFrame(frame3, text=label_text, padx=padx, pady=pady)
            label_frame.grid(row=row_num, column=col_num, padx=padx, pady=pady, sticky="nsew")

            entry = Entry(label_frame, textvariable=text_var)
            entry.pack()

            self.entrys.append(entry)

        # Configure row and column weights to make the grid layout expandable
        for i in range(num_rows):
            frame3.grid_rowconfigure(i, weight=1)

        for i in range(num_columns):
            frame3.grid_columnconfigure(i, weight=1)

        # change between different diagnostic data
        button6 = Button(frame3, text="<", bg="#FFD100", fg="black")
        button6.grid(row=3, column=7, padx=padx, pady=pady, sticky="nsew")

        button5 = Button(frame3, text=">", bg="#FFD100", fg="black")
        button5.grid(row=3, column=8, padx=padx, pady=pady, sticky="nsew")

        ## setup battery stuff
        def update_battery_diagnostics():
            label_frames = [
                ("Total Voltage: ", print_out(self.total_voltage, "V")),
                ("Current: ", print_out(self.current, "I")),
                ("Power: ", print_out(self.power, "W")),
                ("Charging Power: ", print_out(self.charging_power, "W")),
                ("Discharging Power: ", print_out(self.discharging_power, "W")),
                ("Capacity Remaining: ", print_out(self.capacity_remaining, "C")),
                ("Nominal Capacity: ", print_out(self.nominal_capacity, "C")),
                ("Charging Cycles: ", print_out(self.charging_cycles)),
                ("State of Charge: ", print_out(self.state_of_charge, "P")),
                ("Temperature 1: ", print_out(self.temperature_1, "T")),
                ("Temperature 2: ", print_out(self.temperature_2, "T")),
                ("Temperature 3: ", print_out(self.temperature_3, "T")),
                ("Cell Voltage 1: ", print_out(self.cell_voltage_1, "V")),
                ("Cell Voltage 2: ", print_out(self.cell_voltage_2, "V")),
                ("Cell Voltage 3: ", print_out(self.cell_voltage_3, "V")),
                ("Cell Voltage 4: ", print_out(self.cell_voltage_4, "V")),
                ("Cell Voltage 5: ", print_out(self.cell_voltage_5, "V")),
                ("Cell Voltage 6: ", print_out(self.cell_voltage_6, "V")),
                ("Cell Voltage 7: ", print_out(self.cell_voltage_7, "V")),
                ("Cell Voltage 8: ", print_out(self.cell_voltage_8, "V")),
                ("Cell Voltage 9: ", print_out(self.cell_voltage_9, "V")),
                ("Cell Voltage 10: ", print_out(self.cell_voltage_10, "V")),
                ("Cell Voltage 11: ", print_out(self.cell_voltage_11, "V")),
                ("Cell Voltage 12: ", print_out(self.cell_voltage_12, "V")),
                ("Cell Voltage 13: ", print_out(self.cell_voltage_13, "V")),
                ("Cell Voltage 14: ", print_out(self.cell_voltage_14, "V")),
                ("Cell Voltage 15: ", print_out(self.cell_voltage_15, "V")),
                ("Cell Voltage 16: ", print_out(self.cell_voltage_16, "V")),
                ("Min Cell Voltage: ", print_out(self.min_cell_voltage, "V")),
                ("Max Cell Voltage: ", print_out(self.max_cell_voltage, "V")),
                ("Max Voltage Cell: ", print_out(self.max_voltage_cell, "V")),
                ("Min Voltage Cell: ", print_out(self.min_voltage_cell, "V")),
                ("Delta Cell Voltage: ", print_out(self.delta_cell_voltage, "V")),
                ("Average Cell Voltage: ", print_out(self.average_cell_voltage, "V")),
            ]

            for i, (_, text_var) in enumerate(label_frames):
                self.entrys[i].delete(0, END)
                self.entrys[i].insert(0, text_var.get())

        def get_bat_data():
            while True:
                battery.read_esp32()
                total_voltage, current, power, charging_power, discharging_power, capacity_remaining, nominal_capacity, charging_cycles, balancer_status_bitmask, errors_bitmask, software_version, state_of_charge, operation_status_bitmask, battery_strings, temperature_1, temperature_2, temperature_3, cell_voltage_1, cell_voltage_2, cell_voltage_3, cell_voltage_4, cell_voltage_5, cell_voltage_6, cell_voltage_7, cell_voltage_8, cell_voltage_9, cell_voltage_10, cell_voltage_11, cell_voltage_12, cell_voltage_13, cell_voltage_14, cell_voltage_15, cell_voltage_16, min_cell_voltage, max_cell_voltage, max_voltage_cell, min_voltage_cell, delta_cell_voltage, average_cell_voltage = battery.parse_data()
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
                    
        def start_bat_thread():
            self.battery_thread = threading.Thread(target=get_bat_data)
            self.battery_thread.daemon = True
            self.battery_thread.start()

        start_bat_thread()

        # camera stuff
        def camera_update1():
            # get the camera feed
            while True:
                if self.cap1 is not None:
                    ret, img1 = self.cap1.read()
                    with self.lock_cam1:
                        self.img1 = img1
                else:
                    time.sleep(1)
                    with self.lock_cam1:
                        self.img1 = None
                      
        def camera_update2():
            # get the camera feed
            while True:
                if self.cap2 is not None:
                    ret, img2 = self.cap2.read()
                    with self.lock_cam2:
                        self.img2 = img2
                else:
                    time.sleep(1)
                    with self.lock_cam2:
                        self.img2 = None                   

        def camera_update3():
            # get the camera feed
            while True:
                if self.cap3 is not None:
                    ret, img3 = self.cap3.read()
                    with self.lock_cam3:
                        self.img3 = img3
                else:
                    time.sleep(1)
                    with self.lock_cam3:
                        self.img3 = None

        def camera_update4():
            # get the camera feed
            while True:
                if self.cap4 is not None:
                    ret, img4 = self.cap4.read()
                    with self.lock_cam4:
                        self.img4 = img4
                else:
                    time.sleep(1)
                    with self.lock_cam4:
                        self.img4 = None

        def camera_update5():
            # get the camera feed
            while True:
                if self.cap5 is not None:
                    ret, img5 = self.cap5.read()
                    with self.lock_cam5:
                        self.img5 = img5
                else:
                    time.sleep(1)
                    with self.lock_cam5:
                        self.img5 = None

        def camera_update6():
            # get the camera feed
            while True:
                if self.cap6 is not None:
                    ret, img6 = self.cap6.read()
                    with self.lock_cam6:
                        self.img6 = img6
                else:
                    time.sleep(1)
                    with self.lock_cam6:
                        self.img6 = None
            
        def start_cam_thread():
            self.cam_thread1 = threading.Thread(target=camera_update1)
            self.cam_thread1.daemon = True
            self.cam_thread1.start()

            self.cam_thread2 = threading.Thread(target=camera_update2)
            self.cam_thread2.daemon = True
            self.cam_thread2.start()

            self.cam_thread3 = threading.Thread(target=camera_update3)
            self.cam_thread3.daemon = True
            self.cam_thread3.start()

            self.cam_thread4 = threading.Thread(target=camera_update4)
            self.cam_thread4.daemon = True
            self.cam_thread4.start()

            self.cam_thread5 = threading.Thread(target=camera_update5)
            self.cam_thread5.daemon = True
            self.cam_thread5.start()

            self.cam_thread6 = threading.Thread(target=camera_update6)
            self.cam_thread6.daemon = True
            self.cam_thread6.start()

        start_cam_thread()

        def camera_image():
            if(self.first_camera == 0):
                img = self.img1
            elif(self.first_camera == 1):
                img = self.img2
            elif(self.first_camera == 2):
                img = self.img3
            elif(self.first_camera == 3):
                img = self.img4
            elif(self.first_camera == 4):
                img = self.img5
            else:
                img = self.img6

            return img
            

        # Initialize a variable to track the last time update_battery_diagnostics() was called
        last_update_time = time.time()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    root.quit()

            # get the camera feed
            if self.cap is not None:
                cv_img = camera_image()
                if(cv_img is not None):
                    img1 = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                    img2 = cv2.resize(img1, (width_image, height_image))
                    img = ImageTk.PhotoImage(Image.fromarray(img2))
                    label1['image'] = img
                else:
                    label1['image'] = black_image_tk
            else:
                label1['image'] = black_image_tk

            # opencv image (1)
            if(self.cap1 is not None):
                if(self.img1 is not None):
                    opencv_img = self.img1
                else:
                    opencv_img = None
            else:
                opencv_img = None

            # Check if one second has passed since the last call to update_battery_diagnostics()
            if time.time() - last_update_time >= 1:
                # update the battery diagnostic data
                update_battery_diagnostics()
                last_update_time = time.time()  # Update the last update time
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

            end, img_2 = localization.update_pygames_screen()
            label2['image'] = img_2

            # quit the program
            if distance.wait_key("q") or end:
                break

            localization.controller_handler(self.calibrateM, self.up_key, self.down_key)

            root.update()

        self.cap.release()
        root.destroy()