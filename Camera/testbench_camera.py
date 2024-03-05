import os
import sys
import cv2
import time


# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Camera_Class import Amcrest_Camera
from PTZ_Control_Class import ptzControl

size = 4

IP = ["http://admin:admin@192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1", "http://admin:admin@192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1", "hello", ""]

connection = [False] * size

ac2 = [Amcrest_Camera()] * size
ptz = [ptzControl()] * size


img = [None] * size
ret = [None] * size

breakout = False

camNumb = 0
camNumbTotal = size - 1


while True:
    cv2.destroyAllWindows()

    start = time.time()
    connection[camNumb] = ac2[camNumb].VideoCapture(IP[camNumb])

    # if(connection[camNumb]):
    #     ptz[0].ptz_setup(IP[camNumb])

    print(time.time() - start)

    for i in range(0, 20000):
        if(connection[camNumb]):
            ret[camNumb], img[camNumb] = ac2[camNumb].read()

            if ret[camNumb]:
                cv2.imshow('image', img[camNumb])

                if cv2.waitKey(1) == 27:
                    breakout = True
                    break
        else:
            time.sleep(0.0002)
        
    ac2[camNumb].destroy()
    if(camNumb == camNumbTotal):
        camNumb = 0
    else:
        camNumb = camNumb + 1

    if breakout:
        break
    
        

cv2.destroyAllWindows()