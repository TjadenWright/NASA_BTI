import cv2
import pygame
from tkinter import *
from PIL import Image, ImageTk
import numpy as np
import os

# Set Pygame to use dummy video driver to hide the window
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Initialize Pygame
pygame.init()

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

# Initialize Pygame font
pygame_font = pygame.font.Font(None, 36)

def draw_animation(screen):
    """Draw a moving animation."""
    screen.fill((255, 255, 255))  # Fill the screen with white

    # Define initial positions
    initial_rect_pos = np.array([100, 100])
    initial_circle_pos = np.array([300, 200])

    # Update positions based on time or frame count
    time_elapsed = pygame.time.get_ticks()  # Get time elapsed since Pygame started
    rect_speed = 0.001  # Adjust speed as needed
    circle_speed = 0.001  # Adjust speed as needed
    rect_pos = initial_rect_pos + np.array([np.sin(time_elapsed * rect_speed), np.cos(time_elapsed * rect_speed)]) * 50
    circle_pos = initial_circle_pos + np.array([np.sin(time_elapsed * circle_speed), np.cos(time_elapsed * circle_speed)]) * 50

    # Draw objects with updated positions
    pygame.draw.rect(screen, (0, 0, 255), (*rect_pos, 100, 100))  # Draw a moving rectangle
    pygame.draw.circle(screen, (255, 0, 0), (int(circle_pos[0]), int(circle_pos[1])), 50)  # Draw a moving circle

    # Render text
    text_surface = pygame_font.render("Pygame Animation", True, (0, 255, 0))
    screen.blit(text_surface, (200, 300))
    
# Create a Pygame screen
pygame_screen = pygame.Surface((640, 380))

# Create a Pygame clock
clock = pygame.time.Clock()

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

def pygame_to_pil(pygame_surface):
    """Convert Pygame surface to PIL image."""
    image_str = pygame.image.tostring(pygame_surface, 'RGB')
    width, height = pygame_surface.get_size()
    return Image.frombytes('RGB', (width, height), image_str)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            root.quit()

    if cap is not None:
        img = cap.read()[1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (width_image, height_image))
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(image=img)
        label1['image'] = img
    else:
        label1['image'] = black_image_tk

    # Draw the Pygame animation
    draw_animation(pygame_screen)
    pygame_image = pygame_to_pil(pygame_screen)
    pygame_image_tk = ImageTk.PhotoImage(image=pygame_image)
    label2['image'] = pygame_image_tk

    root.update_idletasks()
    root.update()
    clock.tick(60)
