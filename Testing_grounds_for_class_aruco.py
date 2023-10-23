from Controls_Class import Rover_Controls
import time
import keyboard
from distance_class import aruco_detect
import os
import numpy as np
import cv2
import cv2.aruco as aruco
import math

Direction = 1 # 1 -> right, -1 left
Velocity = 0.5 # 1 -> fastest forward, -1 -> fastest backwards

# toggle variables for selecting mode (manual vs auto)
mode = 0
Select = 0
prev_Select = 0


calib_data_path = os.path.join("/", "home", "btic", "BTIC_Proto1")


a1 = aruco_detect(calib_data_path=calib_data_path, verbose=True, h=720, w=1280, fps_vid=10)

a1.calibrated_cam_data(0)

a1.aruco_marker_dict()

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
rc1 = Rover_Controls(verbose=False)
rc1.setup_USB_Controller() # pass in the controller # you want to use (default = 0)

# setup communication with the arduino
rc1.Enable_Write_arduino(baud_rate = 115200, arduino_name = 'ACM')

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


        #print('x: ', x, 'y: ', y, 'z: ', z, 'move: ', move)
        
        if (a1.wait_key()):
            break
        if(move):
            # Example usage:
            # target_x = x   # Target x position of the tag
            # target_y = z   # Target y position of the tag

            # Direction, Velocity = convert_position_to_direction_velocity(target_x, target_y)
            
            Direction_prev = Direction
            Direction = -(2*x_screen-1)
            # Direction = dir_val*angle/math.pi
            if(Direction == np.nan):
                Direction = Direction_prev
                
            Velocity = 0.7

            #print(f"Direction: {Direction}, Velocity: {Velocity}")
        else:
            Direction = 0
            Velocity = 0
            
        #print(Direction)
        rc1.Write_message(data=rc1.Motor_PWM(Direction, Velocity)) # send PWM data to the arduino
        print(str(rc1.Motor_PWM(Direction, Velocity)) + " Auto Mode")
    
    prev_Select = Select

rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # end program stop the rover
rc1.Disable_write_arduino()

# Release the VideoCapture and close all OpenCV windows
a1.release()
