from UWB_Class import UWB_Class
import numpy as np

uwb1 = UWB_Class(option=1, speed=100, anchor_x=np.array([0, 73, 2.27, 0]), anchor_y=np.array([70, 0, 1.65, 0]))
#uwb2 = UWB_Class(option=2, speed=100, anchor_x=np.array([0, 100, 2.27, 0]), anchor_y=np.array([0, 100, 1.65, 1.65]))
arduinoData1 = uwb1.serial_communication()
#arduinoData2 = uwb2.serial_communication()

while True:
    tag1 = uwb1.Graphical_display(arduinoData1, circles=True, plot=True)
    #tag2 = uwb1.Graphical_display(arduinoData2, circles=True, plot=True)

    #print("tag1: ", tag1)