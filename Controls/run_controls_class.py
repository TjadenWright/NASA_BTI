import os
import sys
import time

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Controls_ClassV2 import Rover_Controls

Direction = 0 # 1 -> right, -1 left
Velocity = 0 # 1 -> fastest forward, -1 -> fastest backwards

# toggle variables for selecting mode (manual vs auto)
mode = 0
Select = 0
prev_Select = 0

#### values to change ###
controller_numb = 0                        # <--- controller # used.
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "PC"                            # <--- PC or pi?

# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE, PC_or_PI = PC_or_PI)
rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

# setup communication with the arduino
if(PC_or_PI == "PC"):
    rc1.Enable_Write_arduino(baud_rate = baud_rate, arduino_name = 'Latte')
else:
    rc1.Enable_Write_arduino(baud_rate = baud_rate, arduino_name = 'ACM')

# run the code for manual and automatic.
while not rc1.Get_Button_From_Controller():            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
    # get the button to change mode
    Select = rc1.Get_Button_From_Controller(stop_button="Select") # select button is pressed or not

    # toggle the mode
    if Select == 1 and  prev_Select == 0:
        if(mode == 0):
            mode+=1
            rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # set back to zero when changing state
        else:
            mode = 0
            rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # set back to zero when changing state

    # different modes (manual vs auto)
    if(mode == 0): # manual mode
        rc1.Write_message(data=rc1.Controller_To_PWM_and_DIR()) # send PWM data to the arduino
        print(str(rc1.Controller_To_PWM_and_DIR())  + " Manual Mode")

    if(mode == 1): # auto mode
        Direction = 0
        Velocity = 0
            
        # send out data to the arduino
        rc1.Write_message(data=rc1.Motor_PWM(Direction, Velocity)) # send PWM data to the arduino
        print(str(rc1.Motor_PWM(Direction, Velocity)) + " Auto Mode")
    
    # get the states for the button
    prev_Select = Select

# at the end make sure that the rover doesn't go flying
rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # end program stop the rover
rc1.Disable_write_arduino()