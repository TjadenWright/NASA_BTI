# NASA_BTI

# Prototypes
*  **BTIC_Proto1**: Prototype code for the rover following the aruco tag with opencv. This was upgraded to 1280x720 at 10fps from 640x480 at 5fps.
*  **BTIC_Proto2**: Includes the addition of following aruco tags with an x offset, with the ability to see multiple tags at once. Also upgraded to lattepanda, which increased resolution to 4k at 20fps.
* **BTIC_Proto3**: Added localization to the autonomy code and added an rtmp camera connected to the lattepanda for autonomy.

# Installation Process
**Python Packages Installation**
* pip install numpy
* pip install opencv-python==4.6.0.66
* pip install opencv-contrib-python==4.6.0.66
* pip install pyserial
* pip install pygame
* python -m pip install --upgrade pip

**Esphome Installation/Setup**
1. pip install esphome
2. cd Arduino\esphome-jbd-bms-main
3. Open the "esp32-ble-example-multiple-devices.yaml" file and ensure that the bluetooth addresses match the batteries.
4. Connect esp32 device and run: python3 -m esphome run esp32-ble-example-multiple-devices.yaml

**Arduino Setup**
* Any custom functions make sure to put in the arduino library folder: \Documents\Arduino\libraries\

**Upload from VScode**
1. Use the global repository section: https://docs.github.com/en/get-started/getting-started-with-git/setting-your-username-in-git#setting-your-git-username-for-every-repository-on-your-computer
2. Go to the bottom left button and click open remote repository and select the one you want.
3. Select the same bottom left button again and select save a local clone.
4. Then in the terminal (cntrl + '), type in git init to initialize the git repository.
5. Upload to Github as normal through VS code.
6. If you need to delete a commit: git reset --soft HEAD~.
