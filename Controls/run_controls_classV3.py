import os
import sys
import time
import threading
import numpy as np

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Controls_ClassV3 import Rover_Controls

#### values to change ###
controller_numb = 0                        # <--- controller # used.
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "Lenovo"                            # <--- PC or pi?

# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE, verbose_control = True, timing = True, PC_or_PI = PC_or_PI)
rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

rc1.Enable_Write_arduino(index = 0, arduino_name = "Uno", baud_rate = 115200)
# rc1.Enable_Write_arduino(index = 1, arduino_name = "Leonardo", baud_rate = 9600)

rc1.set_act_OR_motor(config = np.array([1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 3])) # 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 3
# bad: 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 2, 3        ^ issue
rc1.start_arduino_command(index = 0, HIGH_LOW = 0)
# rc1.start_arduino_command(index = 1, HIGH_LOW = 1)

rc1.start_diagnostics_AND_controls_thread(index = 0)
# rc1.start_diagnostics_AND_controls_thread(index = 1)

while not rc1.Get_Button_From_Controller("Select"):            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
    # print("hello world")
    # all_threads = threading.enumerate()
    # print("List of threads: ")
    # for thread in all_threads:
    #     print(thread.name)
    # # time.sleep(1)
    # print(rc1.get_controls_array())
    # connection = rc1.handle_events()

    # if(rc1.Get_Button_From_Controller("Menu")):
    #     if(rc1.get_act_OR_motor()[0] == 0):
    #         config = np.array([act, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
    #         rc1.set_act_OR_motor(config = config)

    #         time.sleep(0.5)
    #     elif(rc1.get_act_OR_motor()[0] == 1):
    #         config = np.array([motor, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
    #         rc1.set_act_OR_motor(config = config)
    #         time.sleep(0.5)
    time.sleep(0.033)

    rc1.control_motor_OR_actutor(channel_Numb = 1, select = rc1.get_act_OR_motor()[0], verbose = True) # rc1.get_act_OR_motor()[0]


# print("reset")
# rc1.stop_thread()
# time.sleep(1)
# print("----------------------------------")
# print("1s After Stop Command")
# all_threads = threading.enumerate()
# for thread in all_threads:
#     print(thread.name)
# print("----------------------------------")
# rc1.Disable_write_arduino(index = 0)
# rc1.Disable_write_arduino(index = 1)
# print("setting up arduinos")
# rc1.Enable_Write_arduino(index = 0, arduino_name = "Uno", baud_rate = 115200)
# rc1.Enable_Write_arduino(index = 1, arduino_name = "Leonardo", baud_rate = 9600)
# rc1.set_act_OR_motor(config = np.array([1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 3]))
# print("setting up threads")
# rc1.start_arduino_command(index = 0, HIGH_LOW = 0)
# rc1.start_arduino_command(index = 1, HIGH_LOW = 1)
# # print(type(int(self.channel[0])))
# # print(type(1))
# # np.array([self.channel[0], self.channel[1], self.channel[2], self.channel[3], self.channel[4], self.channel[5], self.channel[6], self.channel[7], self.channel[8], self.channel[9], self.channel[10], self.channel[11], self.channel[12], self.channel[13], self.channel[14], self.channel[15]])
# time.sleep(0.1)
# rc1.start_diagnostics_AND_controls_thread(index = 0)
# rc1.start_diagnostics_AND_controls_thread(index = 1)
# print("end of threads")

# while not rc1.Get_Button_From_Controller("Select"):            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
#     # print("hello world")
#     # all_threads = threading.enumerate()
#     # print("List of threads: ")
#     # for thread in all_threads:
#     #     print(thread.name)
#     # # time.sleep(1)
#     # print(rc1.get_controls_array())
#     # connection = rc1.handle_events()

#     # if(rc1.Get_Button_From_Controller("Menu")):
#     #     if(rc1.get_act_OR_motor()[0] == 0):
#     #         config = np.array([act, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
#     #         rc1.set_act_OR_motor(config = config)

#     #         time.sleep(0.5)
#     #     elif(rc1.get_act_OR_motor()[0] == 1):
#     #         config = np.array([motor, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
#     #         rc1.set_act_OR_motor(config = config)
#     #         time.sleep(0.5)
#     # time.sleep(0.1)
#     time.sleep(0.033)
#     rc1.control_motor_OR_actutor(channel_Numb = 1, select = rc1.get_act_OR_motor()[0], verbose = False) # rc1.get_act_OR_motor()[0]


# motor = 0
# act = 1
# slew = 2
# mother = 3

# config = np.array([act, motor, motor, motor, motor, motor, motor, motor, act, act, act, act, act, act, slew, mother])

# # def start_reset_thread():
# #     move_on = True
# #     all_threads = threading.enumerate()
# #     for thread in all_threads:
# #         if(thread.name == "stop"):
# #             move_on = False
# #     if(move_on):
# #         stop = threading.Thread(target=reset_thread, name="stop")
# #         stop.daemon = True
# #         stop.start()

# # def reset_thread():
# #     print("stop thread")
# #     rc1.stop_thread()
# #     time.sleep(0.5)
# #     rc1.set_act_OR_motor(config = config)
# #     rc1.start_diagnostics_AND_controls_thread(index = 0)
# #     # rc1.start_diagnostics_AND_controls_thread(index = 1)

# # print(rc1.get_diagnostics_array())
# # run the code for manual and automatic.
# while not rc1.Get_Button_From_Controller("Select"):            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
#     # print("hello world")
#     # all_threads = threading.enumerate()
#     # print("List of threads: ")
#     # for thread in all_threads:
#     #     print(thread.name)
#     # # time.sleep(1)
#     print(rc1.get_controls_array())
#     connection = rc1.handle_events()

#     if(rc1.Get_Button_From_Controller("Menu")):
#         if(rc1.get_act_OR_motor()[0] == 0):
#             config = np.array([act, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
#             rc1.set_act_OR_motor(config = config)

#             time.sleep(0.5)
#         elif(rc1.get_act_OR_motor()[0] == 1):
#             config = np.array([motor, config[1], config[2], config[3], config[4], config[5], config[6], config[7], config[8], config[9], config[10], config[11], config[12], config[13], config[14], config[15]])
#             rc1.set_act_OR_motor(config = config)
#             time.sleep(0.5)
#     time.sleep(0.1)

#     rc1.control_motor_OR_actutor(channel_Numb = 9, select = rc1.get_act_OR_motor()[0], verbose = False) # rc1.get_act_OR_motor()[0]
