import os
import sys

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from GUI_Class import GUI
from Battery_Class import Battery_class

b1 = Battery_class()

g1 = GUI()

g1.Get_Camera_IPs()

g1.Main_UI(b1)