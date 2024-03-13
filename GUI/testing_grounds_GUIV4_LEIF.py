import os
import sys

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from GUI_ClassV4_LEIF import GUI
from Battery_ClassV2 import Battery_class
from Distance_ClassV6 import aruco_detect
from Localization_ClassV3 import localization
from Controls_ClassV3_LEIF import Rover_Controls

Input_Res = (1920, 1080)                              # <--- change camera resolution (if change reclaibrate)
FPS_video = 15                                        # <--- change fps (no need to recalibrate)
MARKER_SIZE = 10                                      # <--- height of the whole tag in cm (or same units as in calibrate sheet)
calib_file = "MultiMatrix1080PC.npz"                  # <--- file that stores the matricies. Must end it .npz
DICT_MXM_L = "DICT_7X7_1000"                          # <--- dictionary used
scaling_factor = 1                                    # <--- You can change this to adjust the scaling
zoom_factor = 1.0
zoom_step = 0.1  # You can adjust the step size as needed.
#### values to change ###
controller_numb = 0                        # <--- controller # used.
VERBOSE = False                            # <--- do you want diagnostic data?
baud_rate = 9600                           # <--- make this the same as the arduino
PC_or_PI = "PC"                            # <--- PC or pi?
Fake_traffic = True
img_Localization = None # start of image at nothing

# setup the rover controls class.
rc1 = Rover_Controls(verbose=VERBOSE, PC_or_PI = PC_or_PI)
# rc1.setup_USB_Controller(controller_numb=controller_numb) # pass in the controller # you want to use (default = 0)

# intialize the battery
b1 = Battery_class(verbose=VERBOSE)

if(not Fake_traffic):
    b1.get_esp32()
    b1.enable_read()

# setup GUI class
g1 = GUI()
vid_w, vid_h, local_w, local_h = g1.set_screen() #1350, 780

# intialize localization
l1 = localization(scaling_factor=scaling_factor, zoom_factor=zoom_factor, zoom_step=zoom_step, Output_Res=(local_w, local_h))
l1.init_pygame()

# initialize the aruco detect class
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=(vid_w, vid_h), fps_vid=FPS_video, calib_file=calib_file) # <--- sets up the class
# get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb) # initialize the camera to the port used at resolution and fps
a1.calibrated_cam_data()
a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

# main gui
g1.set_up_Main_UI(b1, Fake_traffic)

while True:    
    opencv_img, local_enable, calibrateM, up_key, down_key = g1.loop_Main_UI(controls=rc1, local_img=img_Localization, mode=0, imu_image=None)

    x, y, z, dist, tags_ids, rVx, rVy, rVz = a1.aruco_tags(pic_out=False, Frame=opencv_img) # <--- if you want a picture to be dispayed.
    # get origin tag (tag at 0,0,0)
    l1.get_origin_tag(tags_ids, dist, x, y, z, rVx, rVy, rVz)

    # compute other tags (reference to other tags)
    l1.compute_tag_camera_location(tags_ids, dist, x, y, z, rVx, rVy, rVz)

    l1.handler()

    # display the tags on the map
    l1.show_tags()
    # display the camera on the map
    l1.show_camera()

    # handler and legend
    l1.legend()

    end, img_Localization = l1.update_pygames_screen()

    # quit the program
    if a1.wait_key("q") or end:
        break

    l1.controller_handler(calibrateM, up_key, down_key)

g1.release_main()