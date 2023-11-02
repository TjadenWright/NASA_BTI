import os
import sys
import numpy as np

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Distance_ClassV2 import aruco_detect

url_OR_cam_numb = 0                                    # <--- camera # if on usb, camera ip if over ethernet/wireless
recal_cam = True                                       # <--- if you need to recalibrate the camera set this to true (only need to do this if you change resolution/camera)
Resolution = (3840, 2160)                              # <--- change camera resolution (if change reclaibrate)
FPS_video = 30                                         # <--- change fps (no need to recalibrate)
MARKER_SIZE = 6                                        # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 1.8                      # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
images_folder = "images4k"                           # <--- folder to store images in calibration
calib_file = "MultiMatrix4k.npz"                     # <--- file that stores the matricies. Must end it .npz
scale = 0.5                                            # <--- scale of output image
DICT_MXM_L = "DICT_7X7_100"                            # <--- dictionary used

max_dist = 0

a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, h=Resolution[1], w=Resolution[0], fps_vid=FPS_video, calib_file=calib_file) # <--- sets up the class

# if you need to calibrate
if recal_cam:
    a1.take_picks(url_OR_cam_numb=url_OR_cam_numb, images_folder=images_folder) # takes the pictures press 's' to save each picture and 'q' to end that processes
    a1.make_calibration_table(SQUARE_SIZE=Calibrate_sheet_square_SIZE, images_folder=images_folder) # this will automatically load the pictures and make the camera matrix and the distance coeff matrix

# start up the camera with calibrated data and resolution and fps
a1.calibrated_cam_data(url_OR_cam_numb=url_OR_cam_numb)

a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

# a1.parallel_process_frames(num_threads=1, scale=scale)
# a1.release()

# while loop for sensing data
while True:
    # display the camera along with aruco tag tracking data.
    x, y, z, spotted, __ = a1.aruco_tag(calc_aruco=True, pic_out=True, scale=scale) # <--- if you want see the aruco tag, then if you want a picture to be dispayed.
    ## IF MOVE IS TRUE, THIS WILL TELL YOU IT SEES AN ARUCO TAG!!!!!

    dist = np.sqrt(x ** 2 + y ** 2 + z ** 2)

    if(spotted):
        if(dist > max_dist):
            max_dist = dist
    
    print("results: ", round(max_dist,2), " cm") # look at the last one

    if (a1.wait_key()):
        break

a1.release()