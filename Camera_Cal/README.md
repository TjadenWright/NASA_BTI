# NASA_BTI
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/Space Trajectory logo.jpg" alt="Space Trajectory" title="Space Trajectory" />

# Localization and Aruco Detection
## Table 1. Camera Files
| File Name  | Change Log | File to Run |
| ------------- | ------------- |--------------|
| run_distance_class   | This was used to calibrate cameras.  | [Camera_Cal/run_distance_class.py](https://github.com/TjadenWright/NASA_BTI/blob/main/Camera_Cal/run_distance_class.py) |
| run_distance_class_AND_localization   | This function has localization without taking into account the ArUco tags angle.  | [Camera_Cal/run_distance_class_AND_localization.py](https://github.com/TjadenWright/NASA_BTI/blob/main/Camera_Cal/run_distance_class_AND_localization.py) |
| run_distance_class_AND_localization_with_angles   | This function has localization taking into account the ArUco tags angle.  | [Camera_Cal/run_distance_class_AND_localization_with_angles.py](https://github.com/TjadenWright/NASA_BTI/blob/main/Camera_Cal/run_distance_class_AND_localization_with_angles.py) |

## ArUco Tag detection
* This was tested in the dark using the IP cameras night vision mode.
<img src="https://github.com/TjadenWright/NASA_BTI/blob/main/Media/night_vision.png" alt="night_vision" title="night_vision" />