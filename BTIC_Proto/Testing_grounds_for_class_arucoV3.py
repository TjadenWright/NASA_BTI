import os
import sys
import math
import time 
import numpy as np

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up       

from Controls_ClassV2 import Rover_Controls
from Distance_ClassV4 import aruco_detect
from Localization_ClassV2 import localization

# Initialize your variables
move = 0

# toggle variables for selecting mode (manual vs auto)
mode = 0
Select = 0
prev_Select = 0

#### values to change ###
url_OR_cam_numb = "rtsp://admin:nasabs123@192.168.166.148:554/cam/realmonitor?channel=1&subtype=0"    # <--- camera # if on usb, camera ip if over ethernet/wireless
controller_numb = 0                        # <--- controller # used.
Input_Res = (1920, 1080)                    # <--- change camera resolution (if change reclaibrate)
Output_Res = (640, 480)                    # <--- output resolution
FPS_video = 30                             # <--- change fps (no need to recalibrate)
MARKER_SIZE = 18.6                            # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 1.8          # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
calib_file = "MultiMatrix1080Amcrest.npz"          # <--- file that stores the matricies. Must end it .npz
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "PC"                            # <--- PC or pi?
Center_spot = 50                           # <--- how many cm from the aruco tag right or left side do you want the rover to drive to?
time_delay_not_seeing_tag = 0.5            # <--- how much time do you want to account for not seeing a tag (makes it less jerky)
DICT_MXM_L = "DICT_7X7_100"                # <--- dictionary used
num_threads = 8                            # <--- number of threads used
scaling_factor = 1                         # <--- You can change this to adjust the scaling
zoom_factor = 1.0
zoom_step = 0.1  # You can adjust the step size as needed.
Vmax = 0.5

# setup camera parameters
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=Output_Res, fps_vid=FPS_video, calib_file=calib_file, num_threads=num_threads) # <--- sets up the class

# start up the camera with calibrated data and resolution and fps
get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb)

l1 = localization(scaling_factor=scaling_factor, zoom_factor=zoom_factor, zoom_step=zoom_step, Output_Res=Output_Res)

l1.init_pygame()

if get_cam:
    # add calibrated data to camera
    a1.calibrated_cam_data()
    
    # use a marker dictionary
    a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L)

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

    def scale_range(value, old_min, old_max, new_min, new_max):
        # Check if the value is within the old range
        if value < old_min or value > old_max:
            raise ValueError("Value is outside the old range")

        # Calculate the scaling factor
        old_range = old_max - old_min
        new_range = new_max - new_min
        scaling_factor = new_range / old_range

        # Scale the value to the new range
        scaled_value = new_min + (value - old_min) * scaling_factor

        return scaled_value

    # setup the rover controls class.
    rc1 = Rover_Controls(verbose=VERBOSE, PC_or_PI = PC_or_PI)
    rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

    # setup communication with the arduino
    if(PC_or_PI == "PC"):
        rc1.Enable_Write_arduino(baud_rate = baud_rate, arduino_name = 'Arduino Mega 2560')
    else:
        rc1.Enable_Write_arduino(baud_rate = baud_rate, arduino_name = 'ACM')

    calib = False
    calibrate = False

    # run the code for manual and automatic.
    while not rc1.Get_Button_From_Controller():            # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
        # handels different key presses
        l1.handler()

        # # get location from opencv
        x_calc, y_calc, z_calc, dist, ids, rVx, rVy, rVz = a1.aruco_tags_threaded(pic_out=True, FPS_read = False) # <--- if you want a picture to be dispayed.

        prev_calib = calib

        # get origin tag (tag at 0,0,0)
        calib = l1.get_origin_tag(a1, ids, dist, x_calc, y_calc, z_calc)

        if(prev_calib == False and calib == True):
            calibrate = True

        # compute other tags (reference to other tags)
        l1.compute_tag_camera_location(ids, dist, x_calc, y_calc, z_calc, rVx, rVy, rVz)

        # get the button to change mode
        Select = rc1.Get_Button_From_Controller(stop_button="Select") # select button is pressed or not

        # toggle the mode
        if Select == 1 and prev_Select == 0:
            if(mode == 0):
                mode+=1
                rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # set back to zero when changing state
                last_spotted_time = time.time()
                prev_spotted = 1
                x_prev = 0
                y_prev = 0
                Velocity = 0
                first_time = True
                calibrate = False
            else:
                mode = 0
                rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # set back to zero when changing state

        # different modes (manual vs auto)
        if(mode == 0): # manual mode
            rc1.Write_message(data=rc1.Controller_To_PWM_and_DIR()) # send PWM data to the arduino
            print(str(rc1.Controller_To_PWM_and_DIR())  + " Manual Mode")
            #print("manual")

        elif(mode == 1): # auto mode
            
            l1.controller_handler(rc1.Get_Button_From_Controller("Start"), rc1.Get_Button_From_Controller("Dpad_Up"), rc1.Get_Button_From_Controller("Dpad_Down"))

            if(calibrate):
                # find closest tag
                if dist:
                    tag_to_move_to = np.argmin(dist)
                    spotted = True
                else:
                    tag_to_move_to = -1
                    spotted = False

                if(tag_to_move_to != -1):
                    x_new = x_calc[tag_to_move_to]
                    y_new = y_calc[tag_to_move_to]

                # Calculate the time difference
                time_difference = time.time() - last_spotted_time

                if(spotted):
                    # Update the timestamp
                    last_spotted_time = time.time()
                    x = x_new
                    y = y_new
                    Velocity = Vmax
                    first_time = False

                elif(time_difference <= time_delay_not_seeing_tag and not first_time):
                    # Use the previous values of x and z if spotted is False and it's been less than 0.5 seconds
                    x = x_prev
                    y = y_prev
                    Velocity = Vmax
                else:
                    # Reset x and z if it's been 0.5 seconds or more since the last True spotted value
                    x = 0
                    y = 0
                    Velocity = 0

                # Calculate the angle to the target (in radians)
                angle = math.atan2(y, x-Center_spot) # find the angle
                # 1.18 to 1.96

                # max and min of angles
                if(angle > 1.96):
                    angle = 1.96
                elif(angle < 1.18):
                    angle = 1.18

                unit = scale_range(angle, 1.18, 1.96, -1, 1)

                Direction = unit

                print("x: ", round(x-Center_spot,2), "y: ", round(y,2), "angle: ", round(angle,2), "dir: ", round(Direction,2), "vel", round(Velocity,2), "ids: ", ids)

                # send out data to the arduino
                rc1.Write_message(data=rc1.Motor_PWM(Direction, Velocity)) # send PWM data to the arduino
                #print(str(rc1.Motor_PWM(Direction, Velocity)) + " Auto Mode")
                prev_spotted = spotted
                x_prev = x
                y_prev = y

        # get the states for the button
        prev_Select = Select

        # display the tags on the map
        l1.show_tags()
        # display the camera on the map
        l1.show_camera()

        l1.legend()

        # quit the program
        if a1.wait_key("q") or l1.update_pygames_screen():
            break

    # at the end make sure that the rover doesn't go flying
    rc1.Write_message(data=rc1.Motor_PWM(0, 0)) # end program stop the rover
    rc1.Disable_write_arduino()

    # Release the VideoCapture and close all OpenCV windows
    a1.release()