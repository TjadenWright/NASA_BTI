# NASA_BTI
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Space Trajectory logo.jpg" alt="Space Trajectory" title="Space Trajectory" />

# Camera Calibration Data
* Calibration is used to get the correct distances and angles from the distance function.
* The images are stored in folders and the npz files have the actual calibration data.

# How to Calibrate a Camera.
* Use [this](https://github.com/TjadenWright/NASA_BTI/blob/main/Camera_Cal/run_distance_class.py) file.
* Enter the cameras IP in the url_OR_cam_numb variable.
* Change images_folder and calib_file to something that represents your camera.
* Change the recal_cam to True and run the program. Once done change the recal_cam variable back to False to ensure that you do not overight you calibration.