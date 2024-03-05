import os
import sys
import cv2


# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Camera_Class import Amcrest_Camera

ac2 = Amcrest_Camera()
ac2.VideoCapture()