# NASA_BTI
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Space Trajectory logo.jpg" alt="Space Trajectory" title="Space Trajectory" />

# Prototypes
| Prototype Number  | Change Log | File to Run |
| ------------- | ------------- |--------------|
| BTIC_Proto1   | Prototype code for the rover following the aruco tag with opencv. This was upgraded to 1280x720 at 10fps from 640x480 at 5fps.  | [BTIC_Proto/Testing_grounds_for_class_aruco.py](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto/Testing_grounds_for_class_aruco.py) |
| BTIC_Proto2   | Includes the addition of following aruco tags with an x offset, with the ability to see multiple tags at once. Also upgraded to lattepanda, which increased resolution to 4k at 20fps.  | [BTIC_Proto/Testing_grounds_for_class_arucoV2.py](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto/Testing_grounds_for_class_arucoV2.py) | 
| BTIC_Proto3   | Added localization to the autonomy code and added an rtmp camera connected to the lattepanda for autonomy. | [BTIC_Proto/Testing_grounds_for_class_arucoV3.py](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto/Testing_grounds_for_class_arucoV3.py) | 
| BTIC_Proto4   | Added the GUI V4 to the Prototype Rover code from Prototype 3. | [BTIC_Proto/Testing_grounds_for_class_arucoV4.py](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto/Testing_grounds_for_class_arucoV4.py) | 
| BTIC_Proto5*  | Currently under construction. This will be implementing the new Arduino controls compatable with the motor/actuator board and motherboard. | [BTIC_Proto/Testing_grounds_for_class_arucoV5.py](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto/Testing_grounds_for_class_arucoV5.py) |

# Installation Process
## Python Packages Installation
* pip install numpy
* pip install opencv-python==4.6.0.66
* pip install opencv-contrib-python==4.6.0.66
* pip install pyserial
* pip install pygame
* python -m pip install --upgrade pip
* pip install tkinter
* pip install Pillow
* pip install scipy
* pip install onvif-zeep

## Esphome Installation/Setup
1. pip install esphome
2. cd Arduino\esphome-jbd-bms-main
3. Open the "esp32-ble-example-multiple-devices.yaml" file and ensure that the bluetooth addresses match the batteries.
4. Connect esp32 device and run: python3 -m esphome run esp32-ble-example-multiple-devices.yaml
5. **Never save the make files to this Github**

## Arduino Setup
* Make sure to put any custom functions in the arduino library folder: \Documents\Arduino\libraries\
* More information on how to do this can be found [here](https://github.com/TjadenWright/NASA_BTI/tree/main/Arduino/README.md).

## Upload from VScode
1. Use the global repository section: https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git#setting-your-git-username-for-every-repository-on-your-computer
2. Do this for the user.email. This is the same code but change "user.name" to "user.email".
3. Go to the bottom left button and click open remote repository and select the one you want.
4. Select the same bottom left button again and select save a local clone.
5. Then in the terminal (cntrl + '), type in git init to initialize the git repository.
6. Upload to Github as normal through VS code.
7. If you need to delete a commit: git reset --soft HEAD~.

## GitHub Repositories Used
* https://github.com/RichardoMrMu/python-onvif
* https://github.com/syssi/esphome-jbd-bms
* https://github.com/gregsrabian/MCP41HVX1
* https://github.com/PatrickBaus/Arduino-TMP1075
* https://github.com/DocSunset/ADS1219
* https://github.com/LizardByte/Sunshine
* https://github.com/adafruit/Adafruit_MCP9600
* https://github.com/adafruit/Adafruit_NAU7802
* https://github.com/adafruit/Adafruit_BusIO

# Software Architecture
## This is the software architecture as of 3/18/24
* This does not include the Autonomous Excavation, Autonomous Docking, IMU diagnostics, and SNMP diagnostics.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Software%20Architecture.png" alt="Software Architecture" title="Software Architecture" />

# Camera
## The camera used for this project is the [Amcrest IP2M-866EW](https://amcrest.com/2mp-poe-camera-ptz-optical-zoom-ip2m-866ew.html).
* The configuration of the cameras can be found [here](https://github.com/TjadenWright/NASA_BTI/tree/main/Config_Files/README.md).
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/amcrest_camera.png" alt="amcrest_camera" title="amcrest_camera" />

# GUI
## The GUI is ran on the [Latte Panda](https://www.lattepanda.com/lattepanda-sigma) and streamed to the [Lenovo Legion Go](https://www.bestbuy.com/site/lenovo-legion-go-8-8-144hz-wqxga-gaming-handheld-amd-ryzen-z1-extreme-16gb-with-1-tb-ssd-shadow-black/6559604.p?skuId=6559604&extStoreId=17&utm_source=feed&ref=212&loc=20677102012&gad_source=1&gclid=Cj0KCQjw-_mvBhDwARIsAA-Q0Q5JStR1fjypDxy6wOrAogh6heojWA5ad6dLaR_N4Ziuy7XByfNrB-caApVPEALw_wcB&gclsrc=aw.ds) through [Sunshine](https://github.com/LizardByte/Sunshine) Games Stream
* This is the main GUI used for the NASA BTIC project.
* The diagnostics data, video feed, and localization/imu viewer are located on this GUI.
* More detail of the GUI can be found [here](https://github.com/TjadenWright/NASA_BTI/tree/main/GUI).
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/lenovo_with_GUI.png" alt="lenovo_with_GUI" title="lenovo_with_GUI" />

# Autonomy and Localization
## V3 (Final) of the Autonomy and Localization
* This video shows the Autonomy and Localization of the Prototype rover. The rover uses ArUco tags and OpenCV in Python to track the positioning of the rover and autonomously move to the next ArUco tag. This was using BTIC_Proto3 code.
* More detail of the Autonomy and Localization can be found at [Camera_Cal](https://github.com/TjadenWright/NASA_BTI/tree/main/Camera_Cal) and [BTIC_Proto](https://github.com/TjadenWright/NASA_BTI/tree/main/BTIC_Proto).
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Autonomy_Localization_Video.gif" alt="Autonomy Localization Video" title="Autonomy Localization Video" />

# Controls
## V3 of the controls
* Visual representation of the communication between Arduino and Python.
* More detail of the Controls can be found [here](https://github.com/TjadenWright/NASA_BTI/tree/main/Controls).
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/controls_architecture.png" alt="Controls Architecture" title="Controls Architecture" />
