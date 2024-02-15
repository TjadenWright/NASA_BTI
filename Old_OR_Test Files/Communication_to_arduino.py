import serial.tools.list_ports
from Driving import get_side_motor
import time

# Find the Arduino port automatically (assuming there's only one Arduino connected)
arduino_port = None
ports = serial.tools.list_ports.comports()
for port in ports:
    if 'Arduino' in port.description:  # Adjust the description as needed
        arduino_port = port.device
        break

if arduino_port is None:
    print("Arduino not found. Check the connection or adjust the description.")
    exit(1)

# Set up the serial connection
serial_inst = serial.Serial(arduino_port, baudrate=115200)

while True:
    sides = get_side_motor()
    print("Left Side Voltage: ", int(sides[0]), "Right Side Voltage: ", int(sides[1]))
    # Send the two integers separated by a comma and terminated with a newline character
    data = f"{int(sides[0])},{int(sides[1])}\n"
    serial_inst.write(data.encode('utf-8'))
    serial_inst.flush()  # Ensure data is sent immediately

    # time.sleep(0.1)

