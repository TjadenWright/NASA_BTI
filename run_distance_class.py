from distance_class import aruco_detect
import os
import math

calib_data_path = os.path.join("/", "home", "btic", "BTIC_Proto1")

a1 = aruco_detect(calib_data_path=calib_data_path, verbose=True, h=720, w=1280, fps_vid=10)

a1.take_picks(url_OR_cam_numb=0)
a1.make_calibration_table(SQUARE_SIZE=1.8)

a1.calibrated_cam_data(0)

a1.aruco_marker_dict()

def convert_position_to_direction_velocity(target_x, target_y):
    # Calculate the angle (in radians) between the current and target positions
    if(target_x != 0):
        theta = math.atan(target_y/abs(target_x)) # get theta
    else:
        theta = math.pi/2 # div by zero

    # chose left or right
    if(target_x > 0):
        sign = 1
    else:
        sign = -1

    print(-theta/(math.pi/2))

    # direction from -1 to 1
    direction = sign*(-theta/(math.pi/2)+1) # 0(when y = 0, only x) to 1 (when x = 0, y only) -(theta/pi/2)+1  (1 -> 0, 0-> 1)

    # velocity div by 
    velocity = target_y/100
    
    return direction, velocity

while True:
    x, y, z, move, __ = a1.aruco_tag(calc_aruco=True, pic_out=True)

    #print('x: ', x, 'y: ', y, 'z: ', z, 'move: ', move)

    # Example usage:
    target_x = x   # Target x position of the tag
    target_y = z   # Target y position of the tag

    direction, velocity = convert_position_to_direction_velocity(target_x, target_y)

    print(f"Direction: {direction}, Velocity: {velocity}")


    # pos x = turn right
    # neg x = turn left

    if (a1.wait_key()):
        break

a1.release()
