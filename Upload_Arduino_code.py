import subprocess
import serial.tools.list_ports
import os

# Define the path to the Arduino sketch (.ino file)
sketch_path = "C:/Users/tj10c/OneDrive/Documents/Classes/Senior/Fall 2023/EE 422/Testing Grounds/Arduino/Arduino_Communication/Arduino_Communication.ino"

# Find the Arduino port automatically
arduino_port = None
ports = serial.tools.list_ports.comports()
for port in ports:
    if 'Arduino' in port.description:
        arduino_port = port.device
        break

if arduino_port is None:
    print("Arduino not found. Check the connection or adjust the description.")
else:
    try:
        # Compile and upload the sketch
        compile_command = f"arduino-cli compile --fqbn <board_info> {sketch_path}"
        upload_command = f"arduino-cli upload -p {arduino_port} --fqbn <board_info> {sketch_path}"

        # Replace <board_info> with your specific board information (e.g., "arduino:avr:uno")

        # Change the current working directory to where the sketch is located
        sketch_directory = os.path.dirname(sketch_path)
        os.chdir(sketch_directory)

        # Compile the sketch
        subprocess.run(compile_command, shell=True, check=True)

        # Upload the sketch
        subprocess.run(upload_command, shell=True, check=True)

        print("Upload successful.")

    except subprocess.CalledProcessError as e:
        print("Upload failed.")
        print(e)