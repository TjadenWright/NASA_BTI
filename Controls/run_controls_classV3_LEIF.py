import os
import sys
import time
import threading
import numpy as np

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Controls_ClassV3_LEIF import Rover_Controls

#### values to change ###
controller_numb = 0                        # <--- controller # used.
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "Lenovo"                            # <--- PC or pi?

# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE, timing = True, PC_or_PI = PC_or_PI)
rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

rc1.Enable_Write_arduino(index = 0, arduino_name = "Uno", baud_rate = 115200)
# rc1.Enable_Write_arduino(index = 1, arduino_name = "Leonardo", baud_rate = 9600)

rc1.set_act_OR_motor(config = np.array([0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 3])) # 3 is motherboard/imu

# rc1.start_arduino_command(index = 0, HIGH_LOW = 0)
rc1.start_arduino_command(index = 0, HIGH_LOW = 1)

rc1.start_diagnostics_AND_controls_thread(index = 0)
# rc1.start_diagnostics_AND_controls_thread(index = 1)

print(rc1.get_diagnostics_array())
# run the code for manual and automatic.
while not rc1.Get_Button_From_Controller("Menu"):            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
    # print("hello world")
    # all_threads = threading.enumerate()
    # print("List of threads: ")
    # for thread in all_threads:
    #     print(thread.name)
    # time.sleep(1)
    # rc1.print_diagnostics()
    connection = rc1.handle_events()

    rc1.control_motor_OR_actutor(channel_Numb = 1, select = 1, verbose = True)

    time.sleep(0.5)