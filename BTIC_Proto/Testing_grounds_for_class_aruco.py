import os
import sys

# Navigate up one directory level to access the class folder
calib_data_path = os.path.dirname(os.path.abspath(__file__))
class_folder_path = os.path.join(calib_data_path, '../Python Class')
sys.path.append(class_folder_path)

from Controls_Class import Rover_Controls
from Distance_Class import aruco_detect
import numpy as np
import math

Direction = 0 # 1 -> right, -1 left
Velocity = 0 # 1 -> fastest forward, -1 -> fastest backwards

# toggle variables for selecting mode (manual vs auto)
mode = 0
Select = 0
prev_Select = 0

#### values to change ###
url_OR_cam_numb = 0                        # <--- camera # if on usb, camera ip if over ethernet/wireless
controller_numb = 0                        # <--- controller # used.
Resolution = (640, 480)                    # <--- change camera resolution (if change reclaibrate)
FPS_video = 5                              # <--- change fps (no need to recalibrate)
MARKER_SIZE = 8                            # <--- height of the whole tag in cm (or same units as in calibrate sheet)
VERBOSE = True                             # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino

# setup camera parameters
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=VERBOSE, h=Resolution[1], w=Resolution[0], fps_vid=FPS_video)

# setup camera used
a1.calibrated_cam_data(url_OR_cam_numb=url_OR_cam_numb)

# use a marker dictionary
a1.aruco_marker_dict()

# convert coordiantes to direction and velocity
def convert_position_to_direction_velocity(target_x, target_y):
    # Calculate the angle (in radians) between the current and target positions
    if(target_x != 0):
        theta = math.atan(target_y/abs(target_x)) # get theta
    else:
        theta = math.pi/2 # div by zero

    # chose left or right
    if(target_x > 0):
        sign = 1
    else:
        sign = -1

    print(-theta/(math.pi/2))

    # direction from -1 to 1
    direction = sign*(-theta/(math.pi/2)+1) # 0(when y = 0, only x) to 1 (when x = 0, y only) -(theta/pi/2)+1  (1 -> 0, 0-> 1)

    # velocity div by 
    velocity = target_y/100
    
    return direction, velocity

# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE)
rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

# setup communication with the arduino
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
        rc1.Write_message(data=rc1.Motor_PWM_controller()) # send PWM data to the arduino
        print(str(rc1.Motor_PWM_controller())  + " Manual Mode")
        #print("manual")

    if(mode == 1): # auto mode
        x, y, z, move, x_screen = a1.aruco_tag(calc_aruco=True, pic_out=True)
        
        if (a1.wait_key()):
            break
        if(move):            
            Direction_prev = Direction
            Direction = -(2*x_screen-1)
            # Direction = dir_val*angle/math.pi
            if(Direction == np.nan):
                Direction = Direction_prev
                
            Velocity = 0.7 # fixed at 70% velocity
        # if don't move set all to zero
        else:
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

# Release the VideoCapture and close all OpenCV windows
a1.release()
