from Controller import get_controller_inputs

maximum_voltage = 255 # maximum voltage of the driving motors
dead_zone = 0.05 # deadzone for the joysticks
upper_loss = 0.004

def get_side_motor():
    controls = get_controller_inputs()

    # right x and right trigger
    # 2      ,     9
    # -1 -> 1, -1 -> 1

    right_x = controls[2]
    right_t = (controls[9] + 1)/2

    right_side_motors = maximum_voltage*right_t*(1.0-max(0, (right_x-dead_zone)*(1/(1-dead_zone)))) + upper_loss
    left_side_motors = maximum_voltage*right_t*(1.0+min(0, (right_x+dead_zone)*(1/(1-dead_zone)))) + upper_loss

    return [left_side_motors, right_side_motors]

## Test Functions

# while(1):
#     sides = get_side_motor()
#     print("Left Side Voltage: ", sides[0], "Right Side Voltage: ", sides[1])

# import time

# start_time = time.perf_counter()
# sides = get_side_motor()
# end_time = time.perf_counter()
# print("Execution Time:", end_time - start_time)