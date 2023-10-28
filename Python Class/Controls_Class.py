# controls class

import pygame
import serial.tools.list_ports
import time

class Rover_Controls:
    def __init__(self, verbose = False, maximum_voltage = 255, dead_zone = 0.05, upper_loss = 0.004):
        self.verbose = verbose                       # debuggin purposes.
        self.maximum_voltage = maximum_voltage       # maximum voltage of the driving motors.
        self.dead_zone = dead_zone                   # deadzone for the joysticks.
        self.upper_loss = upper_loss                 # fix for inconsistancies in the upper values of controller.
        self.controls = None                         # set controls to none to initialize it.
        self.countR = 0
        self.countL = 0
    
    def setup_USB_Controller(self, controller_numb = 0):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(controller_numb)  # get joystick from pygame.
        self.joystick.init()                                       # initialize the joystick.

    def USB_Controller(self):
        pygame.event.get()  # Get pygame events

        # Get joystick buttons using list comprehension
        buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

        # Get joystick axes
        left_x = self.joystick.get_axis(0)
        left_y = self.joystick.get_axis(1)
        right_x = self.joystick.get_axis(3)
        right_y = self.joystick.get_axis(4)
        
        # Dpad
        dpad_up = buttons[13]
        dpad_down = buttons[14]
        dpad_left = buttons[16]
        dpad_right = buttons[15]

        # Get trigger analog
        L2_trigger = self.joystick.get_axis(2)
        R2_trigger = self.joystick.get_axis(5)

        if(self.countR == 0 and R2_trigger == 0.0): # haven't moved controller
            R2_trigger = -1.0
        elif(R2_trigger != 0.0):
            self.countR+=1
        if(self.countL == 0 and L2_trigger == 0.0):
            L2_trigger = -1.0
        elif(L2_trigger != 0.0):
            self.countL+=1

        # if you want to debug your values set verbose to True
        if self.verbose:
            print(f"Left Stick (X, Y): ({left_x}, {left_y})")
            print(f"Right Stick (X, Y): ({right_x}, {right_y})")
            print(f"Buttons: {buttons}")
            print(f"DPAD: {dpad_up, dpad_down, dpad_left, dpad_right}")
            print(f"Triggers: {L2_trigger, R2_trigger}")

        # return controller inputs for that pass-through
        return [left_x, left_y, right_x, right_y, dpad_up, dpad_down, dpad_left, dpad_right, L2_trigger, R2_trigger] + [button for idx, button in enumerate(buttons) if idx not in [6, 7, 13, 14, 15, 16]]
    
    def Motor_PWM_controller(self):
        self.controls = self.USB_Controller() # get controller input

        # right x and right trigger
        # 2      ,     9
        # -1 -> 1, -1 -> 1

        right_x = self.controls[2]
        right_t = (self.controls[9] + 1)/2
        left_t = (self.controls[8] + 1)/2

        if(right_t > left_t):
            direction = 1 # go forward
        else:
            direction = 0 # go back

        trigger = max(right_t, left_t)

        right_side_motors = self.maximum_voltage*trigger*(1.0-max(0, (right_x-self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
        left_side_motors = self.maximum_voltage*trigger*(1.0+min(0, (right_x+self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss

        return [int(left_side_motors), int(right_side_motors), direction]
    
    def Motor_PWM(self, Direction, Velocity):
        # velocity -1 to 1
        # direction -1 to 1

        if(Velocity > 0):
            direction = 1
        else:
            direction = -1

        speed = abs(Velocity)

        left_side_motors = self.maximum_voltage*speed*(1.0-max(Direction, 0))
        right_side_motors = self.maximum_voltage*speed*(1.0+min(Direction, 0))

        return [int(left_side_motors), int(right_side_motors), direction]

    def Controller_To_PWM_and_DIR(self):
        self.controls = self.USB_Controller() # get controller input

        right_y = float(self.controls[3])
        left_y = float(self.controls[1])

        right_side_motors = int(255*abs(right_y))
        left_side_motors = int(255*abs(left_y))

        right_dir = int(right_y/right_side_motors)
        left_dir = int(left_y/left_side_motors)

        return [left_side_motors, right_side_motors, left_dir, right_dir]

    def Enable_Write_arduino(self, arduino_name = 'Arduino', baud_rate = 115200):
        # Find the Arduino port automatically (assuming there's only one Arduino connected)
        arduino_port = None
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(port.device)
            if arduino_name in port.description:  # Adjust the description as needed
                arduino_port = port.device
                break

        if arduino_port is None:
            print("Arduino not found. Check the connection or adjust the description.")
            exit(1)

        # Set up the serial connection
        self.serial_inst = serial.Serial(arduino_port, baudrate=baud_rate) # connection made.
        time.sleep(1)

    def Disable_write_arduino(self):
        self.serial_inst.close()

    def Write_message(self, data):
        data_send = self.format_list(list = data)
        # Send the two integers separated by a comma and terminated with a newline character
        self.serial_inst.write(data_send.encode('utf-8'))
        self.serial_inst.flush()  # Ensure data is sent immediately

    def format_list(self, list):
        formatted_string = ",".join(map(str, list)) + "\n"
        return formatted_string
    
    def Get_Button_From_Controller(self, stop_button = 'PS_Logo'):
        #if self.controls is None:
        self.controls = self.USB_Controller()
        Home_Button = self.controls[self.Controller_Button_Map(stop_button)]
        return Home_Button
    
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
        # controls[10] = X_Button
        # controls[11] = O_Button
        # controls[12] = Triangle_Button
        # controls[13] = Square_Button
        # controls[14] = L1_Button
        # controls[15] = R1_Button
        # controls[16] = Select
        # controls[17] = Start
        # controls[18] = PS_Logo
        # controls[19] = Left_Stick_In
        # controls[20] = Right_Stick_In

        Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
                          'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
                          'X_Button', 'O_Button', 'Triangle_Button', 'Square_Button', 'L1_Button', 'R1_Button',
                          'Select', 'Start', 'PS_Logo', 'Left_Stick_In', 'Right_Stick_In']
        
        return Controls_Names.index(button_name)