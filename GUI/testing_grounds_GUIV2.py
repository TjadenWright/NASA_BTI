import os
import sys

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from GUI_ClassV2 import GUI
from Battery_ClassV2 import Battery_class
from Distance_ClassV6 import aruco_detect
from Localization_ClassV3 import localization
from Controls_ClassV2 import Rover_Controls

url_OR_cam_numb = 0 # "rtsp://172.168.100.39:8080/h264.sdp"                                   # <--- camera # if on usb, camera ip if over ethernet/wireless
recal_cam = False                                     # <--- if you need to recalibrate the camera set this to true (only need to do this if you change resolution/camera)
Input_Res = (1920, 1080)                              # <--- change camera resolution (if change reclaibrate)
Output_Res = (800, 480)                               # <--- output resolution
FPS_video = 15                                        # <--- change fps (no need to recalibrate)
MARKER_SIZE = 10                                       # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 2.4                     # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
images_folder = "images1080PC"                        # <--- folder to store images in calibration
calib_file = "MultiMatrix1080PC.npz"                  # <--- file that stores the matricies. Must end it .npz
DICT_MXM_L = "DICT_7X7_1000"                          # <--- dictionary used
num_threads = 8                                       # <--- number of threads used
scaling_factor = 1                                    # <--- You can change this to adjust the scaling
zoom_factor = 1.0
zoom_step = 0.1  # You can adjust the step size as needed.
#### values to change ###
controller_numb = 0                        # <--- controller # used.
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "PC"                            # <--- PC or pi?


# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE, PC_or_PI = PC_or_PI)
# rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

# intialize the battery
b1 = Battery_class(verbose=VERBOSE)
b1.get_esp32()
b1.enable_read()
g1 = GUI()

# intialize localization
l1 = localization(scaling_factor=scaling_factor, zoom_factor=zoom_factor, zoom_step=zoom_step, Output_Res=((1350 - 70 - 800), 480))
l1.init_pygame()

# initialize the aruco detect class
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=Output_Res, fps_vid=FPS_video, calib_file=calib_file, num_threads=num_threads) # <--- sets up the class
# get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb) # initialize the camera to the port used at resolution and fps
a1.calibrated_cam_data()
a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

# camera IP gui
g1.Get_Camera_IPs(skip = True)

# main gui
g1.Main_UI(b1, l1, a1, rc1)