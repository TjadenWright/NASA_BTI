import pygame
import time

import sys

class ControllerManager:
    def __init__(self):
        pygame.init()
        self.joystick = None
        self.verbose = False
        self.countR = 0
        self.countL = 0
        self.controller = False
        self.PC_or_PI = "Lenovo"
        self.controller = False

    def connect_controller(self):
        if(self.controller == False):
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print("Controller connected:", self.joystick.get_name())
                self.controller = True
            else:
                print("No controller found.")
                self.controller = False

    def disconnect_controller(self):
        if(self.controller):
            if self.joystick:
                self.joystick.quit()
                self.joystick = None
                print("Controller disconnected.")
                self.controller = False

    def handle_events(self):
        connected_joysticks = pygame.joystick.get_count()
        if connected_joysticks == 1:
            self.connect_controller()
        elif connected_joysticks < 1:
            self.disconnect_controller()
            
        # Process other events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle quit event
                pygame.quit()
                sys.exit()
    
    # def handle_events():
    #     # Check for joystick device changes
    #     connected_joysticks = pygame.joystick.get_count()
    #     if connected_joysticks < 1:
    #         print("Controller removed.")
    #     elif connected_joysticks == 1:
    #         print("Controller added.")
        
        # Process other events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle quit event
                pygame.quit()
                sys.exit()


    def USB_Controller_Lenovo(self):
        if(self.controller):
            pygame.event.get()  # Get pygame events

            # Get joystick axes
            left_x = self.joystick.get_axis(0)
            left_y = self.joystick.get_axis(1)
            right_x = self.joystick.get_axis(2)
            right_y = self.joystick.get_axis(3) # self.joystick.get_axis(5)

            # Get D-pad buttons
            hat = self.joystick.get_hat(0)
            dpad_up = max(0, hat[1])
            dpad_down = max(0, -hat[1])
            dpad_left = max(0, -hat[0])
            dpad_right = max(0, hat[0])

            # Get trigger analog
            L2_trigger = self.joystick.get_axis(4) # self.joystick.get_axis(3)
            R2_trigger = self.joystick.get_axis(5) # self.joystick.get_axis(4)

            # Get joystick buttons using list comprehension
            buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

            # if you want to debug your values set verbose to True
            if self.verbose:
                print(f"Left Stick (X, Y): ({left_x}, {left_y})")
                print(f"Right Stick (X, Y): ({right_x}, {right_y})")
                print(f"Buttons: {buttons}")
                print(f"DPAD: {dpad_up, dpad_down, dpad_left, dpad_right}")
                print(f"Triggers: {L2_trigger, R2_trigger}")
                # time.sleep(1)

            print(R2_trigger)

            if(self.countR == 0 and R2_trigger == 0.0): # haven't moved controller
                R2_trigger = -1.0
            elif(R2_trigger != 0.0):
                self.countR+=1
            if(self.countL == 0 and L2_trigger == 0.0):
                L2_trigger = -1.0
            elif(L2_trigger != 0.0):
                self.countL+=1

            # controls[0] = Left_Joystick_X
            # controls[1] = Left_Joystick_Y
            # controls[2] = Right_Joystick_X
            # controls[3] = Right_Joystick_Y
            # controls[4] = Dpad_Up
            # controls[5] = Dpad_Down
            # controls[6] = Dpad_Left
            # controls[7] = Dpad_Right
            # controls[8] = L2_Trigger
            # controls[9] = R2_Trigger
            # controls[10] = A_Button (button[0])
            # controls[11] = B_Button (button[1])
            # controls[12] = Y_Button (buttons[3])
            # controls[13] = X_Button (button[2])
            # controls[14] = L1_Button (buttons[4])
            # controls[15] = R1_Button (buttons[5])
            # controls[16] = Menu (buttons[7])
            # controls[17] = Select (buttons[6])
            # controls[18] = Left_Stick_In (buttons[8])
            # controls[19] = Right_Stick_In (buttons[9])

            # return controller inputs for that pass-through
            return [left_x, left_y, right_x, right_y, dpad_up, dpad_down, dpad_left, dpad_right, L2_trigger, R2_trigger, buttons[0],
                    buttons[1], buttons[3], buttons[2], buttons[4], buttons[5], buttons[7], buttons[6], buttons[8], buttons[9]]

    def Get_Button_From_Controller(self, stop_button = 'PS_Logo'):
        if(self.controller):
            #if self.controls is None:
            if(self.PC_or_PI == "PC"):
                self.controls = self.USB_Controller_PC()
            elif(self.PC_or_PI == "Lenovo"):
                self.controls = self.USB_Controller_Lenovo()
            else:
                self.controls = self.USB_Controller_PI()

            Home_Button = self.controls[self.Controller_Button_Map(stop_button)]
            return Home_Button
        return 0

    def Controller_Button_Map(self, button_name):
        # controls[0] = Left_Joystick_X
        # controls[1] = Left_Joystick_Y
        # controls[2] = Right_Joystick_X
        # controls[3] = Right_Joystick_Y
        # controls[4] = Dpad_Up
        # controls[5] = Dpad_Down
        # controls[6] = Dpad_Left
        # controls[7] = Dpad_Right
        # controls[8] = L2_Trigger
        # controls[9] = R2_Trigger
        # controls[10] = A_Button (button[0])
        # controls[11] = B_Button (button[1])
        # controls[12] = Y_Button (buttons[3])
        # controls[13] = X_Button (button[2])
        # controls[14] = L1_Button (buttons[4])
        # controls[15] = R1_Button (buttons[5])
        # controls[16] = Menu (buttons[7])
        # controls[17] = Select (buttons[6])
        # controls[18] = Left_Stick_In (buttons[8])
        # controls[19] = Right_Stick_In (buttons[9])

        if(self.PC_or_PI == "Lenovo"):
            Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
                          'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
                          'A_Button', 'B_Button', 'Y_Button', 'X_Button', 'L1_Button', 'R1_Button',
                          'Menu', 'Select', 'Left_Stick_In', 'Right_Stick_In']
        
        # controls[0] = Left_Joystick_X
        # controls[1] = Left_Joystick_Y
        # controls[2] = Right_Joystick_X
        # controls[3] = Right_Joystick_Y
        # controls[4] = Dpad_Up
        # controls[5] = Dpad_Down
        # controls[6] = Dpad_Left
        # controls[7] = Dpad_Right
        # controls[8] = L2_Trigger
        # controls[9] = R2_Trigger
        # controls[10] = X_Button
        # controls[11] = O_Button
        # controls[12] = Triangle_Button // flip tri and square
        # controls[13] = Square_Button
        # controls[14] = L1_Button
        # controls[15] = R1_Button
        # controls[16] = Select
        # controls[17] = Start
        # controls[18] = PS_Logo
        # controls[19] = Left_Stick_In
        # controls[20] = Right_Stick_In // ps logo back 2
        
        else:
            Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
                            'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
                            'X_Button', 'O_Button', 'Triangle_Button', 'Square_Button', 'L1_Button', 'R1_Button',
                            'Select', 'Start', 'PS_Logo', 'Left_Stick_In', 'Right_Stick_In']
        
        return Controls_Names.index(button_name)


controller_manager = ControllerManager()

while True:
    controller_manager.USB_Controller_Lenovo()
    controller_manager.Controller_Button_Map("Menu")
    controller_manager.handle_events()


    # def handle_events():
    #     # Check for joystick device changes
    #     connected_joysticks = pygame.joystick.get_count()
    #     if connected_joysticks < 1:
    #         print("Controller removed.")
    #     elif connected_joysticks == 1:
    #         print("Controller added.")
        
    #     # Process other events
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             # Handle quit event
    #             pygame.quit()
    #             sys.exit()

    # pygame.init()
    # pygame.joystick.init()
    # if pygame.joystick.get_count() > 0:
    #     joystick = pygame.joystick.Joystick(0)
    #     joystick.init()
    #     print("Controller connected:", joystick.get_name())

    # while True:
    #     handle_events()
