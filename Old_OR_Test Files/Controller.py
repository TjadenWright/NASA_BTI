import pygame

# Initialize Pygame and joystick module outside the function
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

def get_controller_inputs(verbose=False):
    pygame.event.get()  # Get pygame events

    # Get joystick axes
    left_x = joystick.get_axis(0)
    left_y = joystick.get_axis(1)
    right_x = joystick.get_axis(2)
    right_y = joystick.get_axis(3)

    # Get D-pad buttons
    hat = joystick.get_hat(0)
    dpad_up = max(0, hat[1])
    dpad_down = max(0, -hat[1])
    dpad_left = max(0, -hat[0])
    dpad_right = max(0, hat[0])

    # Get trigger analog
    L2_trigger = joystick.get_axis(4)
    R2_trigger = joystick.get_axis(5)

    # Get joystick buttons using list comprehension
    buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

    # if you want to debug your values set verbose to True
    if verbose:
        print(f"Left Stick (X, Y): ({left_x}, {left_y})")
        print(f"Right Stick (X, Y): ({right_x}, {right_y})")
        print(f"Buttons: {buttons}")
        print(f"DPAD: {dpad_up, dpad_down, dpad_left, dpad_right}")
        print(f"Triggers: {L2_trigger, R2_trigger}")

    # return controller inputs for that pass-through
    return [left_x, left_y, right_x, right_y, dpad_up, dpad_down, dpad_left, dpad_right, L2_trigger, R2_trigger] + buttons

## Testing grounds for the function

# import time

# start_time = time.perf_counter()
# controller_inputs = get_controller_inputs(verbose=False)
# end_time = time.perf_counter()
# print("Execution Time:", end_time - start_time)
# print ("Controller Array: ", controller_inputs)
