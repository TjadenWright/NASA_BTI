import os
import sys
import numpy as np
import time

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Distance_ClassV5 import aruco_detect

url_OR_cam_numb = "rtsp://172.168.100.39:8080/h264.sdp"                                    # <--- camera # if on usb, camera ip if over ethernet/wireless
recal_cam = False                                     # <--- if you need to recalibrate the camera set this to true (only need to do this if you change resolution/camera)
Input_Res = (3840, 2160)                              # <--- change camera resolution (if change reclaibrate)
Output_Res = (640, 480)                               # <--- output resolution
FPS_video = 15                                        # <--- change fps (no need to recalibrate)
MARKER_SIZE = 10                                       # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 2.4                    # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
images_folder = "images4kRTSP"                        # <--- folder to store images in calibration
calib_file = "MultiMatrix4kRTSP.npz"                  # <--- file that stores the matricies. Must end it .npz
DICT_MXM_L = "DICT_7X7_1000"                           # <--- dictionary used
num_threads = 12                                       # <--- number of threads used

# set maximum distance to zero to start out
max_dist = 0

# initialize the aruco detect class
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=Output_Res, fps_vid=FPS_video, calib_file=calib_file, num_threads=num_threads) # <--- sets up the class

# initialize the camera to the port used at resolution and fps
get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb)

if get_cam:
    # if you need to calibrate
    if recal_cam:
        a1.take_picks(images_folder=images_folder) # takes the pictures press 's' to save each picture and 'q' to end that processes
        a1.make_calibration_table(SQUARE_SIZE=Calibrate_sheet_square_SIZE, images_folder=images_folder) # this will automatically load the pictures and make the camera matrix and the distance coeff matrix

    # add calibrated data to camera
    a1.calibrated_cam_data()
    start = time.time()
    # set the marker dictionary
    a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

    # while loop for sensing data
    while True:
        # start = time.time()
        # # display the camera along with aruco tag tracking data.
        x, y, z, dist, tags_ids, rVx, rVy, rVz = a1.aruco_tags(pic_out=True, FPS_read=False) # <--- if you want a picture to be dispayed.
        # end = time.time()
        # print("Total Frame Time", end - start)

        # find closest tag
        if dist:
            tag_to_move_to = np.argmin(dist)
        else:
            tag_to_move_to = -1

        print("x: ", x, "y: ", y, "z: ", z, "move: ", rVx, rVy, rVz , dist, "ids: ", tags_ids) # look at the last one

        if tag_to_move_to != -1:
            dist = np.sqrt(x[tag_to_move_to] ** 2 + y[tag_to_move_to] ** 2 + z[tag_to_move_to] ** 2)
            if(dist > max_dist):
                max_dist = dist

        if (a1.wait_key()):
            break

    a1.release()

    # print("Maximum Distance: ", round(max_dist,2), " cm") # look at the last one