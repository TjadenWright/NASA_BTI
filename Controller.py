import pygame

pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Get the first joystick (index 0)
joystick = pygame.joystick.Joystick(0)
joystick.init()

# x -> buttons[0]
# o -> buttons[1]
# square -> butttons[2]
# triangle -> buttons[3]
# left bumper -> buttons[4]
# right bumper -> buttons[5]
# select -> buttons[6]
# start -> buttons[7]
# left stick in -> buttons[8]
# right stuck in -> buttons[9]
# PS logo -> buttons[10]


while True:
    pygame.event.get()  # Get pygame events

    # Get joystick axes
    left_x = joystick.get_axis(0)
    left_y = joystick.get_axis(1)
    right_x = joystick.get_axis(2)
    right_y = joystick.get_axis(3)

    # Get D-pad buttons
    dpad_up = max(0, joystick.get_hat(0)[1])
    dpad_down = max(0, -joystick.get_hat(0)[1])
    dpad_left = max(0, -joystick.get_hat(0)[0])
    dpad_right = max(0, joystick.get_hat(0)[0])

    # Get trigger buttons
    L2_trigger = joystick.get_axis(4)
    R2_trigger = joystick.get_axis(5)

    # Get joystick buttons
    buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

    print(f"Left Stick (X, Y): ({left_x}, {left_y})")
    print(f"Right Stick (X, Y): ({right_x}, {right_y})")
    print(f"Buttons: {buttons}")
    print(f"DPAD: {dpad_up, dpad_down, dpad_left, dpad_right}")
    print(f"Triggers: {L2_trigger, R2_trigger}")

    pygame.time.delay(1000)  # Add a delay to avoid excessive printing
