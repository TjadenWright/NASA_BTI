# NASA_BTI

# Prototypes
| Prototype Number  | Change Log | File to Run |
| ------------- | ------------- |--------------|
| BTIC_Proto1   | Prototype code for the rover following the aruco tag with opencv. This was upgraded to 1280x720 at 10fps from 640x480 at 5fps.  | BTIC_Proto/Testing_grounds_for_class_aruco.py |
| BTIC_Proto2   | Includes the addition of following aruco tags with an x offset, with the ability to see multiple tags at once. Also upgraded to lattepanda, which increased resolution to 4k at 20fps.  | BTIC_Proto/Testing_grounds_for_class_arucoV2.py | 
| BTIC_Proto3   | Added localization to the autonomy code and added an rtmp camera connected to the lattepanda for autonomy. | BTIC_Proto/Testing_grounds_for_class_arucoV3.py | 
| BTIC_Proto4   | Added the GUI V4 to the Prototype Rover code from Prototype 3. | BTIC_Proto/Testing_grounds_for_class_arucoV4.py | 
| BTIC_Proto5*  | Currently under construction. This will be implementing the new Arduino controls compatable with the motor/actuator board and motherboard. | BTIC_Proto/Testing_grounds_for_class_arucoV5.py
# Installation Process
**Python Packages Installation**
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

**Esphome Installation/Setup**
1. pip install esphome
2. cd Arduino\esphome-jbd-bms-main
3. Open the "esp32-ble-example-multiple-devices.yaml" file and ensure that the bluetooth addresses match the batteries.
4. Connect esp32 device and run: python3 -m esphome run esp32-ble-example-multiple-devices.yaml

**Arduino Setup**
* Make sure to put any custom functions in the arduino library folder: \Documents\Arduino\libraries\
* An example of a custon function is ADS1219_code\ADS1219\

**Upload from VScode**
1. Use the global repository section: https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git#setting-your-git-username-for-every-repository-on-your-computer
2. Do this for the user.email. This is the same code but change "user.name" to "user.email".
3. Go to the bottom left button and click open remote repository and select the one you want.
4. Select the same bottom left button again and select save a local clone.
5. Then in the terminal (cntrl + '), type in git init to initialize the git repository.
6. Upload to Github as normal through VS code.
7. If you need to delete a commit: git reset --soft HEAD~.

# GUI
**V5 of the GUI**
* This is using BTIC_Proto5 code.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/GUI_V5.png" alt="GUI V5" title="GUI V5" />

# Autonomy
**V3 (Final) of the Autonomy**
* This is using BTIC_Proto3 code.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Autonomy_Localization_Video.gif" alt="Autonomy Localization Video" title="Autonomy Localization Video" />
