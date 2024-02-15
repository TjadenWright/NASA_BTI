import time
import serial.tools.list_ports
import cmath
import matplotlib.pyplot as plt

# Enable interactive mode
plt.ion()

# Initialize the figure and axis with a 10x10 plot
fig, ax = plt.subplots(figsize=(4, 4))  # Set the figure size to 10x10
dynamic_dot, = ax.plot([], [], 'ro')  # 'ro' specifies red dot markers for dynamic dot
fixed_dot1, = ax.plot([], [], 'bo')  # 'bo' specifies blue dot markers for first fixed dot
fixed_dot2, = ax.plot([], [], 'go')  # 'go' specifies green dot markers for second fixed dot

# Set the axis limits for a 10x10 plot
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

# Function to update the dot's position
def update_dot(dot, x, y):
    dot.set_data(x, y)
    plt.draw()  # Force the figure to update
    plt.pause(0.1)  # Pause to update the plot (adjust as needed)

def tag_pos(a, b, c):
    if b == 0 or c == 0:
        # Handle the case where b or c is zero to avoid division by zero
        return None, None
    
    cos_a = (b * b + c * c - a * a) / (2 * b * c)
    x = b * cos_a
    y = b * cmath.sqrt(1 - cos_a * cos_a)

    return round(x.real, 2), round(y.real, 2)

# Initialize fixed dot positions (you can change these as needed)
fixed_dot1_x = 0
fixed_dot1_y = 0
fixed_dot2_x = 1
fixed_dot2_y = 0

# Update the initial positions of the fixed dots
update_dot(fixed_dot1, fixed_dot1_x, fixed_dot1_y)
update_dot(fixed_dot2, fixed_dot2_x, fixed_dot2_y)

# Find the ESP32 port automatically (assuming there's only one Arduino connected)
esp32_port = None
ports = serial.tools.list_ports.comports()
for port in ports:
    if 'Silicon Labs CP210x' in port.description:  # Adjust the description as needed
        esp32_port = port.device
        break

if esp32_port is None:
    print("ESP32 not found. Check the connection or adjust the description.")
    exit(1)

arduinoData = serial.Serial(esp32_port, 115200)
time.sleep(1)
count = 0; data85=[]; data84=[]
a = 0; b=0
while True:
    while(arduinoData.inWaiting()==0):
        pass
    dataPacket=arduinoData.readline()
    if(dataPacket[0:2] == b'84'):
        data84 = dataPacket
        if(float(dataPacket[3:7]) >= 0):
            count+=1
            a = float(dataPacket[3:7])
    elif(dataPacket[0:2] == b'85'):
        data85 = dataPacket
        if(float(dataPacket[3:7]) >= 0):
            count+=1
            b = float(dataPacket[3:7])
    print(data84[3:7], data85[3:7])
    if(count % 2 == 0):
        [x, y] = tag_pos(a, b, 1)
        # print(x, y)
        # print('x: ', x, 'y: ', y)
        update_dot(dynamic_dot, x, y)