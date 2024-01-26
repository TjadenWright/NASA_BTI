# NASA_BTI

BTIC_Proto1: Prototype code for the rover following the aruco tag with opencv. This was upgraded to 1280x720 at 10fps from 640x480 at 5fps.\
BTIC_Proto2: Includes the addition of following aruco tags with an x offset, with the ability to see multiple tags at once. Also upgraded to lattepanda, which increased resolution to 4k at 20fps.\
BTIC_Proto3: Added localization to the autonomy code and added an rtmp camera connected to the lattepanda for autonomy.


pip install numpy\
pip install opencv-python==4.6.0.66\
pip install opencv-contrib-python==4.6.0.66\
pip install pyserial\
pip install pygame

python -m pip install --upgrade pip\
sudo apt-get update\
sudo apt-get upgrade -y\
sudo apt-get install libgl1-mesa-glx -y
