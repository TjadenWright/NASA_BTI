import os
import sys
import numpy as np

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Distance_ClassV3 import aruco_detect
from Localization_Class import localization

url_OR_cam_numb = 0                                   # <--- camera # if on usb, camera ip if over ethernet/wireless
recal_cam = False                                     # <--- if you need to recalibrate the camera set this to true (only need to do this if you change resolution/camera)
Input_Res = (1920, 1080)                              # <--- change camera resolution (if change reclaibrate)
Output_Res = (640, 480)                               # <--- output resolution
FPS_video = 30                                        # <--- change fps (no need to recalibrate)
MARKER_SIZE = 7                                       # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 1.8                     # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
images_folder = "images1080"                          # <--- folder to store images in calibration
calib_file = "MultiMatrix1080.npz"                    # <--- file that stores the matricies. Must end it .npz
DICT_MXM_L = "DICT_7X7_100"                           # <--- dictionary used
num_threads = 8                                       # <--- number of threads used
scaling_factor = 1                                    # <--- You can change this to adjust the scaling
zoom_factor = 1.0
zoom_step = 0.1  # You can adjust the step size as needed.

# initialize the aruco detect class
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=Output_Res, fps_vid=FPS_video, calib_file=calib_file, num_threads=num_threads) # <--- sets up the class

# initialize the camera to the port used at resolution and fps
get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb)

l1 = localization(scaling_factor=scaling_factor, zoom_factor=zoom_factor, zoom_step=zoom_step, Output_Res=Output_Res)

l1.init_pygame()


if get_cam:
    # if you need to calibrate
    if recal_cam:
        a1.take_picks(images_folder=images_folder) # takes the pictures press 's' to save each picture and 'q' to end that processes
        a1.make_calibration_table(SQUARE_SIZE=Calibrate_sheet_square_SIZE, images_folder=images_folder) # this will automatically load the pictures and make the camera matrix and the distance coeff matrix

    # add calibrated data to camera
    a1.calibrated_cam_data()

    # set the marker dictionary
    a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

    while True:
        # handels different key presses
        l1.handler()
        # get location from opencv
        x, y, z, dist, tags_ids = a1.aruco_tags_threaded(pic_out=True, FPS_read = False) # <--- if you want a picture to be dispayed.

        # get origin tag (tag at 0,0,0)
        l1.get_origin_tag(a1, tags_ids, dist, x, y, z)

        # compute other tags (reference to other tags)
        l1.compute_tag_camera_location(tags_ids, dist, x, y, z)

        # display the tags on the map
        l1.show_tags()
        # display the camera on the map
        l1.show_camera()

        # quit the program
        if a1.wait_key("q") or l1.update_pygames_screen():
                break

    a1.release()