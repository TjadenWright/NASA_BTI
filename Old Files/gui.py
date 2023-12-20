# import cv2
# import numpy as np
# from tkinter import *
# from PIL import Image, ImageTk

# # root = Tk("Test1")
# # root.geometry("150x300")
# # root.config(bg="light grey")

# # # Create an entry for the camera index
# # camera_entry_label1 = Label(root, text="Camera 1 IP", bg="light grey", fg="black")
# # camera_entry_label1.pack()
# # camera_entry1 = Entry(root)
# # camera_entry1.pack()

# # # Create an entry for the camera index
# # camera_entry_label2 = Label(root, text="Camera 2 IP", bg="light grey", fg="black")
# # camera_entry_label2.pack()
# # camera_entry2 = Entry(root)
# # camera_entry2.pack()

# # # Create an entry for the camera index
# # camera_entry_label3 = Label(root, text="Camera 3 IP", bg="light grey", fg="black")
# # camera_entry_label3.pack()
# # camera_entry3 = Entry(root)
# # camera_entry3.pack()

# # # Create an entry for the camera index
# # camera_entry_label4 = Label(root, text="Camera 4 IP", bg="light grey", fg="black")
# # camera_entry_label4.pack()
# # camera_entry4 = Entry(root)
# # camera_entry4.pack()

# # # Create an entry for the camera index
# # camera_entry_label5 = Label(root, text="Camera 5 IP", bg="light grey", fg="black")
# # camera_entry_label5.pack()
# # camera_entry5 = Entry(root)
# # camera_entry5.pack()

# # # Create an entry for the camera index
# # camera_entry_label6 = Label(root, text="Camera 6 IP", bg="light grey", fg="black")
# # camera_entry_label6.pack()
# # camera_entry6 = Entry(root)
# # camera_entry6.pack()

# # cam1 = None
# # cam2 = None
# # cam3 = None
# # cam4 = None
# # cam5 = None
# # cam6 = None
# # First = True

# # def connect():
# #     global cam1, cam2, cam3, cam4, cam5, cam6, First
# #     cam1 = camera_entry1.get()
# #     cam2 = camera_entry2.get()
# #     cam3 = camera_entry3.get()
# #     cam4 = camera_entry4.get()
# #     cam5 = camera_entry5.get()
# #     cam6 = camera_entry6.get()
# #     First = False

# # button_text = "Connect to Cameras"
# # button = Button(root, text=button_text, bg="white", fg="black", command=connect)
# # button.pack(pady=20)


# # while First:
# #     root.update()

# # print(cam1, cam2, cam3, cam4, cam5, cam6)

# # other one
# root = Tk("Test1")
# root.geometry("1280x720")
# root.config(bg="light grey")

# width_image = 320
# height_image = 240

# f1 = LabelFrame(root, text="Test Camera", width=width_image, height=height_image, bg="light grey", fg="black", padx=10, pady=10)
# f1.pack(side=LEFT, padx=10, pady=10)
# L1 = Label(f1, bg="black")
# L1.pack()

# f2 = LabelFrame(root, text="Localization", width=width_image, height=height_image, bg="light grey", fg="black", padx=10, pady=10)
# f2.pack(side=TOP, fill=BOTH, padx=10, pady=10)
# L2 = Label(f2, bg="black")
# L2.pack()

# f3 = LabelFrame(root, text="test", width=width_image, height=height_image, bg="light grey", fg="black", padx=10, pady=10)
# f3.pack(side=LEFT, padx=10, pady=10)

# # # # Create an entry for the camera index
# # # camera_entry_label = Label(f1, text="Camera Index", bg="white", fg="black")
# # # camera_entry_label.pack(side=LEFT)
# # # camera_entry = Entry(f1)
# # # camera_entry.pack(side=LEFT)

# # # cap = None
# # # toggleCamera = 0

# # # def toggle():
# # #     global cap, toggleCamera
# # #     camera_index = camera_entry.get()  # Get the entered string
# # #     print("Entered Camera Index:", camera_index)
    
# # #     if(toggleCamera == 0): # turn on camera
# # #         cap = cv2.VideoCapture(int(camera_index))
# # #         toggleCamera = 1
# # #         button_text = "Disconnect Camera"
# # #     else:
# # #         cap.release()
# # #         cap = None
# # #         toggleCamera = 0
# # #         button_text = "Connect Camera"

# # #     button.config(text=button_text)

# # # button_text = "Connect Camera" if toggleCamera == 0 else "Disconnect Camera"
# # # button = Button(f1, text=button_text, bg="white", fg="black", command=toggle)
# # # button.pack(side=RIGHT)

# # # button1 = Button(f1, text=">", bg="white", fg="black")
# # # button1.pack(side=RIGHT)

# # # button2 = Button(f1, text="<", bg="white", fg="black")
# # # button2.pack(side=RIGHT)

# # # # Create a black image
# black_image = Image.new("RGB", (width_image, height_image), "black")

# # # # Convert the Image to PhotoImage
# black_image_tk = ImageTk.PhotoImage(black_image)

# L2['image'] = black_image_tk


# # # # # Create an entry for the camera index
# # # # Voltage_entry_label = Label(root, text="Voltage", bg="white", fg="black")
# # # # Voltage_entry_label.pack(side=LEFT)
# # # # Voltage_entry = Entry(root)
# # # # Voltage_entry.pack(side=LEFT)


# while True:
# # #     if(cap != None):
# # #         img = cap.read()[1]
# # #         img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# # #         img = ImageTk.PhotoImage(Image.fromarray(img1))
# # #         L1['image'] = img
# # #     else:
#     L1['image'] = black_image_tk

#     root.update()

# # cap.release()

import cv2
from tkinter import *
from PIL import Image, ImageTk

root = Tk()
root.geometry("1350x720")
root.title("Main GUI")
root.config(bg="#2c3e50")

width_image = 640
height_image = 380
padx = 5
pady = 5

# Create a black image
black_image = Image.new("RGB", (width_image, height_image), "black")

# Convert the Image to PhotoImage
black_image_tk = ImageTk.PhotoImage(black_image)

cap = None
toggleCamera = 0

def toggle():
    global cap, toggleCamera
    
    if(toggleCamera == 0): # turn on camera
        cap = cv2.VideoCapture(0)
        toggleCamera = 1
        button_text = "Disconnect Camera"
    else:
        cap.release()
        cap = None
        toggleCamera = 0
        button_text = "Connect Camera"

    cameraB.config(text=button_text)

# Function to handle button clicks
def button_click(frame_number):
    print(f"Button clicked in Frame {frame_number}")

# Create a frame for the first two LabelFrames and use pack
frame_container1 = Frame(root, bg="#0033A0")
frame_container1.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

# Create the first LabelFrame stacked horizontally using pack
frame1 = LabelFrame(frame_container1, text="Camera Feed", padx=padx, pady=pady)
frame1.pack(side=LEFT, padx=padx, pady=pady)

label1 = Label(frame1, bg="black")
label1.pack()

button2 = Button(frame1, text="<", bg="#FFD100", fg="black")
button2.pack(side=LEFT)

button1 = Button(frame1, text=">", bg="#FFD100", fg="black")
button1.pack(side=LEFT)

button_text = "Connect Camera" if toggleCamera == 0 else "Disconnect Camera"
cameraB = Button(frame1, text=button_text, bg="#FFD100", fg="black", command=toggle)
cameraB.pack(side=LEFT, padx=230)

# Create the second LabelFrame stacked horizontally using pack
frame2 = LabelFrame(frame_container1, text="Positioning", padx=padx, pady=pady)
frame2.pack(side=LEFT, padx=padx, pady=pady)

label2 = Label(frame2, bg="black")
label2.pack()

label1['image'] = black_image_tk
label2['image'] = black_image_tk

# Create a frame for the third LabelFrame and use pack
frame_container2 = Frame(root, bg="#0033A0")
frame_container2.pack(side=TOP, fill=BOTH, padx=padx, pady=pady)

button4 = Button(frame2, text="+", bg="#FFD100", fg="black")
button4.pack(side=LEFT)

button3 = Button(frame2, text="-", bg="#FFD100", fg="black")
button3.pack(side=LEFT)

cameraC = Button(frame2, text="Calibrate Localization", bg="#FFD100", fg="black")
cameraC.pack(side=LEFT, padx=230)

# Create the third LabelFrame below the first two using pack
frame3 = LabelFrame(frame_container2, text="Battery Diagnostics", padx=padx, pady=pady, bg="#0033A0", fg="white")
frame3.pack(side=LEFT, padx=padx, pady=pady)

# Define the number of rows and columns
num_rows = 3
num_columns = 9

def format_voltage(value):
    return f"{value:.3f} V"

def format_temperature(value):
    return f"{value:.3f} C"

def format_current(value):
    return f"{value:.3f} A"

def format_power(value):
    return f"{value:.3f} W"

def format_capacity(value):
    return f"{value:.3f} Ah"

def format_percent(value):
    return f"{value:.3f} %"

def format_unitless(value):
    return f"{value:.0f}"


# StringVar to hold the value
voltage_var = StringVar()
voltage_var.set(format_voltage(0.0))  # Set the default value with units

# StringVar to hold the value
temp_var = StringVar()
temp_var.set(format_temperature(0.0))  # Set the default value with units

# StringVar to hold the value
cur_var = StringVar()
cur_var.set(format_current(0.0))  # Set the default value with units

# StringVar to hold the value
pow_var = StringVar()
pow_var.set(format_power(0.0))  # Set the default value with units

# StringVar to hold the value
capac_var = StringVar()
capac_var.set(format_capacity(0.0))  # Set the default value with units

# StringVar to hold the value
perc_var = StringVar()
perc_var.set(format_percent(0.0))  # Set the default value with units

uless_var = StringVar()
uless_var.set(format_unitless(0.0))  # Set the default value with units

# Create LabelFrames and Entries in a grid layout
label_frames = [
    ("Total Voltage: ", voltage_var),
    ("Current: ", cur_var),
    ("Power: ", pow_var),
    ("Charging Power: ", pow_var),
    ("Discharging Power: ", pow_var),
    ("Capacity Remaining: ", capac_var),
    ("Nominal Capacity: ", capac_var),
    ("Charging Cycles: ", uless_var),
    ("State of Charge: ", perc_var),
    ("Temperature 1: ", temp_var),
    ("Temperature 2: ", temp_var),
    ("Temperature 3: ", temp_var),
    ("Cell Voltage 1: ", voltage_var),
    ("Cell Voltage 2: ", voltage_var),
    ("Cell Voltage 3: ", voltage_var),
    ("Cell Voltage 4: ", voltage_var),
    ("Cell Voltage 5: ", voltage_var),
    ("Cell Voltage 6: ", voltage_var),
    ("Cell Voltage 7: ", voltage_var),
    ("Cell Voltage 8: ", voltage_var),
    ("Cell Voltage 9: ", voltage_var),
    ("Cell Voltage 10: ", voltage_var),
    ("Cell Voltage 11: ", voltage_var),
    ("Cell Voltage 12: ", voltage_var),
    ("Cell Voltage 13: ", voltage_var),
    ("Cell Voltage 14: ", voltage_var),
    ("Cell Voltage 15: ", voltage_var),
    ("Cell Voltage 16: ", voltage_var),
    ("Min Cell Voltage: ", voltage_var),
    ("Max Cell Voltage: ", voltage_var),
    ("Max Voltage Cell: ", voltage_var),
    ("Min Voltage Cell: ", voltage_var),
    ("Delta Cell Voltage: ", voltage_var),
    ("Average Cell Voltage: ", voltage_var),
]

for i, (label_text, text_var) in enumerate(label_frames):
    row_num = i // num_columns
    col_num = i % num_columns

    label_frame = LabelFrame(frame3, text=label_text, padx=padx, pady=pady)
    label_frame.grid(row=row_num, column=col_num, padx=padx, pady=pady, sticky="nsew")

    entry = Entry(label_frame, textvariable=text_var)
    entry.pack()

# Configure row and column weights to make the grid layout expandable
for i in range(num_rows):
    frame3.grid_rowconfigure(i, weight=1)

for i in range(num_columns):
    frame3.grid_columnconfigure(i, weight=1)

button6 = Button(frame3, text="<", bg="#FFD100", fg="black")
button6.grid(row=3, column=7, padx=padx, pady=pady, sticky="nsew")

button5 = Button(frame3, text=">", bg="#FFD100", fg="black")
button5.grid(row=3, column=8, padx=padx, pady=pady, sticky="nsew")

while True:
    if(cap != None):
        img = cap.read()[1]
        img1 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img2 = cv2.resize(img1, (width_image, height_image))
        img = ImageTk.PhotoImage(Image.fromarray(img2))
        label1['image'] = img
    else:
        label1['image'] = black_image_tk

    root.update()

root.mainloop()

