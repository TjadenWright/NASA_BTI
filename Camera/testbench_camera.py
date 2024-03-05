import os
import sys
import cv2
import time
from tkinter import *
from PIL import Image, ImageTk

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Camera_Class import Amcrest_Camera
from PTZ_Control_Class import ptzControl

size = 2

IP = ["http://admin:admin@192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1", "http://admin:nasabs123@192.168.166.148/cgi-bin/mjpg/video.cgi?channel=0&subtype=1", "hello", ""]

connection = [False] * size

ac2 = [Amcrest_Camera() for _ in range(size)] 
ptz = [ptzControl() for _ in range(size)]


img = [None] * size
ret = [None] * size

breakout = False

camNumb = 0
camNumbTotal = size - 1

root = Tk()
frame1 = LabelFrame(root, text="Camera Feed 1", padx=5, pady=5)
frame1.pack(side=LEFT, padx=5, pady=5)

label1 = Label(frame1, bg="black")
label1.pack()

black_image_video = Image.new("RGB", (640, 480), "black")
black_image_video_tk = ImageTk.PhotoImage(black_image_video)
label1['image'] = black_image_video_tk


while True:
    start = time.time()

    if(connection[camNumb] == False):
        connection[camNumb] = ac2[camNumb].VideoCapture(IP[camNumb])

    # if(connection[camNumb]):
    #     ptz[0].ptz_setup(IP[camNumb])

    print(time.time() - start)

    for i in range(0, 20000):
        if(connection[camNumb]):
            ret[camNumb], img[camNumb] = ac2[camNumb].read()

            if ret[camNumb]:
                img1 = cv2.cvtColor(img[camNumb], cv2.COLOR_BGR2RGB)
                imgTk = ImageTk.PhotoImage(Image.fromarray(img1))
                label1['image'] = imgTk

                if cv2.waitKey(1) == 27:
                    breakout = True
                    break
        else:
            time.sleep(0.0002)

        root.update()
        
    ac2[camNumb].destroy()
    connection[camNumb] = False
    if(camNumb == camNumbTotal):
        camNumb = 0
    else:
        camNumb = camNumb + 1

    if breakout:
        break

    # label1['image'] = black_image_video_tk
    root.update()
    
cv2.destroyAllWindows()