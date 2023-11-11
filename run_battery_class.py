import os
import sys

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Battery_Class import Battery_class

b1 = Battery_class()

b1.get_esp32()

b1.enable_read()

while True:
    b1.read_esp32()

b1.disable_read()


