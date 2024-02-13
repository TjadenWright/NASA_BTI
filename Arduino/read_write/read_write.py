import serial
import time
import threading
from queue import Queue

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

def user_input_thread(input_queue):
    while True:
        num = input_queue.get()  # Get the num value from the main thread
        value = write_read(num)
        print(value)

# Initializing Arduino Serial Connection
arduino = serial.Serial(port='COM7', baudrate=115200, timeout=.1)

# Creating a Queue for communication between threads
input_queue = Queue()

# Creating a separate thread for user input and passing the Queue
input_thread = threading.Thread(target=user_input_thread, args=(input_queue,))

# Starting the threads
input_thread.start()

# Main thread continues to run the Arduino communication
while True:
    # Your main loop for other tasks related to Arduino communication
    num = input("Enter a number (In main thread): ")
    input_queue.put(num)  # Put the num value into the Queue for the user_input_thread
