# controls class

import pygame
import pygame.joystick
import serial.tools.list_ports
import time
from pygame.locals import *
import sys
import numpy as np
import threading
from PIL import Image, ImageTk

class Rover_Controls:
    def __init__(self, verbose = False, verbose_control = False, verbose_diagnostics = False, timing = True, maximum_voltage = 255, dead_zone = 0.05, upper_loss = 0.004, PC_or_PI = "PC"):
        # print out stuff
        self.verbose = verbose                       # debuggin purposes.
        self.verbose_control = verbose_control
        self.verbose_diagnostics = verbose_diagnostics
        self.timing = timing

        # controls stuff
        self.maximum_voltage = maximum_voltage       # maximum voltage of the driving motors.
        self.dead_zone = dead_zone                   # deadzone for the joysticks.
        self.upper_loss = upper_loss                 # fix for inconsistancies in the upper values of controller.
        self.controls = None                         # set controls to none to initialize it.
        self.countR = 0
        self.countL = 0
        self.PC_or_PI = PC_or_PI
        self.controller = False
        self.joystick = None
        pygame.init()

        # arduino stuff
        self.arduino = [None] * 2

        # make a list of things that need to happen
        self.act_OR_motor = np.zeros(16) # 0 is a motor, 1 is an actuator, 2 is slew gear, 3 is motherboard

        # setup channels
        self.diagnostics_channel = [1, 9]
        self.controls_channel = self.diagnostics_channel.copy()

        self.diagnostics_channel_total = [8, 16]
        self.controls_channel_total = self.diagnostics_channel_total.copy()
        
        self.diagnostics_channel_reset = [1, 9]
        self.controls_channel_reset = self.diagnostics_channel_reset.copy()

        # controls
        self.controls_vals = np.zeros((16, 6), int)
        self.timing_flag = np.zeros(16, int)
        self.timing_count = np.zeros(16, int)
        self.PWM_numb = np.zeros(16, int)
        self.dir_numb = np.zeros(16, int)

        # diagnostics
        self.diagnostics_vals = np.zeros((16, 10))
        self.diagnostic_select = np.zeros(16)
        self.diagnostic_lock = [threading.Lock(), threading.Lock()]

        # more diagnostics
        self.start = [0] * 2

        self.last_flip_time = 0  # Track the time of the last flip

        self.auger_or_bucket = 1 # default to bucketwheel
        self.first_time_setup = 1

    
    def setup_USB_Controller(self, controller_numb = 0):
        if(self.controller == False):
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(controller_numb)
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
            self.setup_USB_Controller()
        elif connected_joysticks < 1:
            self.disconnect_controller()
            
        # Process other events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Handle quit event
                pygame.quit()
                sys.exit()

        return self.controller

    def USB_Controller_PC(self):
        pygame.event.get()  # Get pygame events

        # Get joystick axes
        left_x = self.joystick.get_axis(0)
        left_y = self.joystick.get_axis(1)
        right_x = self.joystick.get_axis(2)
        right_y = self.joystick.get_axis(3) #self.joystick.get_axis(5)

        # Get trigger analog
        L2_trigger = self.joystick.get_axis(4) #self.joystick.get_axis(3)
        R2_trigger = self.joystick.get_axis(5) #self.joystick.get_axis(4)

        # Get joystick buttons using list comprehension
        buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

        # dpad
        dpad_up = buttons[11]
        dpad_down = buttons[12]
        dpad_left = buttons[13]
        dpad_right = buttons[14]

        # if you want to debug your values set verbose to True
        if self.verbose:
            print(f"Left Stick (X, Y): ({left_x}, {left_y})")
            print(f"Right Stick (X, Y): ({right_x}, {right_y})")
            print(f"Buttons: {buttons}")
            print(f"DPAD: {dpad_up, dpad_down, dpad_left, dpad_right}")
            print(f"Triggers: {L2_trigger, R2_trigger}")
            time.sleep(1)

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

        # return controller inputs for that pass-through
        return [left_x, left_y, right_x, right_y, dpad_up, dpad_down, dpad_left, dpad_right, L2_trigger, R2_trigger, buttons[0],
                buttons[1], buttons[3], buttons[2], buttons[9], buttons[10], buttons[4], buttons[6], buttons[5], buttons[8], buttons[7]]

    def USB_Controller_Lenovo(self):
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
            time.sleep(1)

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

    def USB_Controller_PI(self):
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
        if(self.controller): # if the controller is connected
            if(self.PC_or_PI == "PC"):
                self.controls = self.USB_Controller_PC() # get controller input
            elif(self.PC_or_PI == "Lenovo"):
                self.controls = self.USB_Controller_Lenovo()
            else:
                self.controls = self.USB_Controller_PI() # get controller input

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
        return [0, 0, 0] # stop the rover!!!!
    
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
        if(self.controller): # if the controller is connected
            if(self.PC_or_PI == "PC"):
                self.controls = self.USB_Controller_PC() # get controller input
            elif(self.PC_or_PI == "Lenovo"):
                self.controls = self.USB_Controller_Lenovo()
            else:
                self.controls = self.USB_Controller_PI() # get controller input

            right_y = -float(self.controls[3])
            left_y = -float(self.controls[1])

            right_side_motors = int(255*(abs(right_y)))
            left_side_motors = int(255*(abs(left_y)))

            if(right_side_motors != 0):
                right_dir = int(255*right_y/right_side_motors)
                if(right_dir < 0):
                    right_dir = 0
            else:
                right_dir = 0

            if(left_side_motors != 0):
                left_dir = int(255*left_y/left_side_motors)
                if(left_dir < 0):
                    left_dir = 0
            else:
                left_dir = 0

            # dead zone
            if(right_side_motors <= 255*self.dead_zone):
                right_side_motors = 0
            if(left_side_motors <= 255*self.dead_zone):
                left_side_motors = 0

            return [left_side_motors, right_side_motors, left_dir, right_dir]
        return [0, 0, 0]
    
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

    # arduino
    def Enable_Write_arduino(self, index = 0, arduino_name = 'Arduino', baud_rate = 115200):
        # Find the Arduino port automatically (assuming there's only one Arduino connected)
        arduino_port = None
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(port.description)
            if arduino_name in port.description:  # Adjust the description as needed
                arduino_port = port.device
                break

        if arduino_port is None:
            print("Arduino not found. Check the connection or adjust the description.")
            exit(1)

        print(arduino_port)
        # Set up the serial connection
        self.arduino[index] = serial.Serial(arduino_port, baudrate=baud_rate) # connection made.
        self.arduino[index].timeout = 0.1
        time.sleep(10)

    # def Disable_write_arduino(self, index = 0):
    #     # self.arduino[index].close()
    #     # self.arduino[index].send_break(duration=1)
    #     data = "reset"
    #     self.arduino[index].write(bytes(data + "\n", 'utf-8'))
    #     time.sleep(1)
    #     self.arduino[index].flushInput()
    #     # self.arduino[index].setDTR(False)
    #     self.arduino[index].close()
    #     self.arduino[index] = None
 

    def write_read(self, data, index = 0):
        # send a command with a \n at the end
        self.arduino[index].write(bytes(data + "\n", 'utf-8'))

        data_get = None

        # Read from the serial port
        while not data_get:
            data_get = self.arduino[index].readline().decode('utf-8').strip()
            if(not data_get):
                print("Got Stuck on: " + str(index) + ": " + data)
                with open("error_log.txt", "a") as error_file:
                    error_file.write("Got Stuck on: " + str(index) + ": " + data + ": " + data_get + "\n")
        return str(data_get)
    
    def set_act_OR_motor(self, config=np.zeros(16)):
        self.act_OR_motor = config

    def set_act_OR_motor_single(self, index, val):
        self.act_OR_motor[index] = val

    def get_act_OR_motor(self):
        return self.act_OR_motor

    def start_arduino_command(self, HIGH_LOW, index = 0):
        if(HIGH_LOW == 1):
            self.diagnostics_channel[index] = 9
            self.controls_channel[index] = self.diagnostics_channel[index]

            self.diagnostics_channel_total[index] = 16
            self.controls_channel_total[index] = self.diagnostics_channel_total[index]
            
            self.diagnostics_channel_reset[index] = 9
            self.controls_channel_reset[index] = self.diagnostics_channel_reset[index]
            high_low_str = "high"
        else:
            self.diagnostics_channel[index] = 1
            self.controls_channel[index] = self.diagnostics_channel[index]

            self.diagnostics_channel_total[index] = 8
            self.controls_channel_total[index] = self.diagnostics_channel_total[index]
            
            self.diagnostics_channel_reset[index] = 1
            self.controls_channel_reset[index] = self.diagnostics_channel_reset[index]
            high_low_str = "low"

        start_command = "startup " + high_low_str
        if(self.verbose):
            print(start_command)
            print(self.write_read(start_command, index))
        else:
            self.write_read(start_command, index)

    def control_motor_arduino_command(self, Channel_Numb, EN, EN_EFUSE, PWM, FR, BRAKE, index):
        motor_control_command = "cMotor " + str(Channel_Numb) + " " + str(EN) + " " + str(EN_EFUSE) + " " + str(PWM) + " " + str(FR) + " " + str(BRAKE)

        if(self.verbose_control):
            print(motor_control_command)
            print(self.write_read(motor_control_command, index))
        else:
            self.write_read(motor_control_command, index)

    def control_actuator_arduino_command(self, Channel_Numb, EN_EFUSE, PWM, FR, disable, index = 0):
        if(disable):
            PWM = 0
        actuator_control_command = "cActuator " + str(Channel_Numb) + " " + str(EN_EFUSE) + " " + str(FR) + " " + str(PWM)

        if(self.verbose_control):
            print(actuator_control_command)
            print(self.write_read(actuator_control_command, index))
        else:
            self.write_read(actuator_control_command, index)

    def start_motor_current_arduino_command(self, Channel_Numb, index = 0):
        motor_start_current_command = "sMotorCurrent " + str(Channel_Numb)

        if(self.verbose_diagnostics):
            print(motor_start_current_command)
            print(self.write_read(motor_start_current_command, index))
        else:
            self.write_read(motor_start_current_command, index)

    def diagnostic_motor_arduino_command(self, Channel_Numb, index = 0):
        motor_diagnostic_command = "dMotor " + str(Channel_Numb)
        data = self.write_read(motor_diagnostic_command, index)

        try:
            if(self.verbose_diagnostics):
                print(motor_diagnostic_command)
                print(data)

            # turn data int variables
            numbers = data.split()
            float_numb = [float(num) for num in numbers]
            left = min(len(float_numb), self.diagnostics_vals.shape[1])

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, :left] = float_numb[:left]
        except Exception as e:
            print("Error: " + motor_diagnostic_command + ": " + str(e))

        # dMotor Channel# -> ALARM TEMP CURRENT OC_FAULT [#, #, #, #, ?, ?, ?, ?, ?, ?]

    def start_motor_speed_arduino_command(self, Channel_Numb, index = 0):
        start_motor_diagnostic_speed_command = "sMotrSpeed " + str(Channel_Numb)

        if(self.verbose_diagnostics):
            print(start_motor_diagnostic_speed_command)
            print(self.write_read(start_motor_diagnostic_speed_command, index))
        else:
            self.write_read(start_motor_diagnostic_speed_command, index)

    def diagnostic_motor_speed_arduino_command(self, Channel_Numb, index = 0):
        motor_diagnostic_speed_command = "dMotrSpeed " + str(Channel_Numb)
        data = self.write_read(motor_diagnostic_speed_command, index)

        try:
            if(self.verbose_diagnostics):
                print(motor_diagnostic_speed_command)
                print(data)

            # turn data int variables
            numbers = data.split()
            float_numb = [float(num) for num in numbers]

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, 4] = float_numb[0]
        except Exception as e:
            print("Error: " + motor_diagnostic_speed_command + ": " + str(e))

        # dMotrSpeed Channel# -> SPEED [#, #, #, #, ##, ?, ?, ?, ?, ?]

    def start_actuator_current_arduino_command(self, Channel_Numb, index = 0):
        start_actuator_diagnostic_current_command = "sActuatorCurrent " + str(Channel_Numb)

        if(self.verbose_diagnostics):
            print(start_actuator_diagnostic_current_command)
            print(self.write_read(start_actuator_diagnostic_current_command, index))
        else:
            self.write_read(start_actuator_diagnostic_current_command, index)

    def diagnostic_actuator_arduino_command(self, Channel_Numb, index = 0):
        actuator_diagnostic_command = "dActuator " + str(Channel_Numb)
        data = self.write_read(actuator_diagnostic_command, index)

        try:
            if(self.verbose_diagnostics):
                print(actuator_diagnostic_command)
                print(data)

            # turn data int variables
            numbers = data.split()
            float_numb = [float(num) for num in numbers]
            left = min(len(float_numb), self.diagnostics_vals.shape[1])

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, :left] = float_numb[:left]
        except Exception as e:
            print("Error: " + actuator_diagnostic_command + ": " + str(e))

        # dActuator Channel#  -> TEMP CURRENT OC_FAULT [#, #, #, ?, ?, ?, ?, ?, ?, ?]

    def start_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb, index = 0):
        start_actuator_feedback_command = "sActuatrFeeback " + str(Channel_Numb)

        if(self.verbose_diagnostics):
            print(start_actuator_feedback_command)
            print(self.write_read(start_actuator_feedback_command, index))
        else:
            self.write_read(start_actuator_feedback_command, index)

    def diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb, index = 0):
        actuator_feedback_command = "dActuatrFeeback " + str(Channel_Numb)
        data = self.write_read(actuator_feedback_command, index)


        try:
            if(self.verbose_diagnostics):
                print(actuator_feedback_command)
                print(data)

            # turn data int variables
            numbers = data.split()
            float_numb = [float(num) for num in numbers]

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, 4] = float_numb[0]
        except Exception as e:
            print("Error: " + actuator_feedback_command + ": " + str(e))
        
        # dActuatrFeeback Channel#  -> FEEDBACK [#, #, #, ?, ##, ?, ?, ?, ?, ?]

    def diagnostics_load_cell_temperature_off_board(self, Channel_Numb, index = 0):
        diagnostics_load_cell_temperature_off_board_command = "dTempAndLC " + str(Channel_Numb)
        data = self.write_read(diagnostics_load_cell_temperature_off_board_command, index)

        if(self.verbose_diagnostics):
            print(diagnostics_load_cell_temperature_off_board_command)
            print(data)

        try:
            # turn data int variables
            numbers = data.split()
            float_numb = []

            float_numb = [float(num) for num in numbers]
            # print("temp and LC diagnostics [", Channel_Numb, "]: ", data)

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, 5] = float_numb[0]
                self.diagnostics_vals[Channel_Numb-1, 6] = float_numb[1]
        except Exception as e:
            print("Error: " + diagnostics_load_cell_temperature_off_board_command + ": " + str(e))

        # dTempAndLC Channel# -> SPEED [#, #, #, #., ##, ###, ###, ?, ?, ?]
            
    # dMotherboard Channel#                 you get this: ALARM TEMP CURRENT OC_FAULT
    def diagnostic_motherboard_arduino_command(self, Channel_Numb, index = 0):
        motherboard_diagnostic_command = "dMotherboard " + str(Channel_Numb)
        data = self.write_read(motherboard_diagnostic_command, index)

        if(self.verbose_diagnostics):
            print(motherboard_diagnostic_command)
            print(data)

        try:
            # turn data int variables
            numbers = data.split()
            float_numb = [float(num) for num in numbers]
            left = min(len(float_numb), self.diagnostics_vals.shape[1])

            with self.diagnostic_lock[index]:
                self.diagnostics_vals[Channel_Numb-1, :left] = float_numb[:left]
        except Exception as e:
            print("Error: " + motherboard_diagnostic_command + ": " + str(e))

    def timing_actuator(self, index = 0):
        if(index == 0):
            low = 0
            high = 7
        elif(index == 1):
            low = 8
            high = 15

        for i in range(low, high):
            if(self.timing_flag[i] == 0):
                self.timing_count[i] = pygame.time.get_ticks()
            elif(self.timing_flag[i] == 1):
                if(pygame.time.get_ticks() - self.timing_count[i] >= 1000):
                    self.timing_flag[i] = 0


    def select_controls(self, index = 0):
        # print(self.controls_channel, )
        if(self.act_OR_motor[self.controls_channel[index]-1] == 0 or self.act_OR_motor[self.controls_channel[index]-1] == 2): # motor or slewgear
            self.control_motor_arduino_command(self.controls_channel[index], self.controls_vals[self.controls_channel[index]-1][0], self.controls_vals[self.controls_channel[index]-1][1], self.controls_vals[self.controls_channel[index]-1][2], self.controls_vals[self.controls_channel[index]-1][3], self.controls_vals[self.controls_channel[index]-1][4], index)
        elif(self.act_OR_motor[self.controls_channel[index]-1] == 1): # actuator
            if(self.PWM_numb[self.controls_channel[index]-1] != self.controls_vals[self.controls_channel[index]-1][1] and self.controls_vals[self.controls_channel[index]-1][1] == 0):
                self.timing_flag[self.controls_channel[index]-1] = 1 # start timer
            elif(self.PWM_numb[self.controls_channel[index]-1] != self.controls_vals[self.controls_channel[index]-1][1] and self.controls_vals[self.controls_channel[index]-1][1] != 0 and self.dir_numb[self.controls_channel[index]-1] == self.controls_vals[self.controls_channel[index]-1][2]):
                self.timing_flag[self.controls_channel[index]-1] = 0 # start timer
            self.control_actuator_arduino_command(self.controls_channel[index], self.controls_vals[self.controls_channel[index]-1][0], self.controls_vals[self.controls_channel[index]-1][1], self.controls_vals[self.controls_channel[index]-1][2], self.timing_flag[self.controls_channel[index]-1], index)
            self.PWM_numb[self.controls_channel[index]-1] = self.controls_vals[self.controls_channel[index]-1][1]
            self.dir_numb[self.controls_channel[index]-1] = self.controls_vals[self.controls_channel[index]-1][2]

            self.timing_actuator(index)
        # elif(self.act_OR_motor[self.controls_channel-1] == 3): # motherboard
            
    def select_diagnostic(self, index = 0):
        
        # debug timming
        if(self.timing):
            if(self.diagnostics_channel[index] == self.diagnostics_channel_reset[index] and self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                print("start of ", threading.current_thread().name)
                self.start[index] = time.time()

        # actual diagnstoic data retrival
        if(self.act_OR_motor[self.diagnostics_channel[index]-1] == 0): # motor
            if(self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                self.start_motor_current_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 1):
                self.diagnostic_motor_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 2):
                self.start_motor_speed_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                self.diagnostic_motor_speed_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel[index]-1] == 1): # actuator
            if(self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                self.start_actuator_current_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 1):
                self.diagnostic_actuator_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 2):
                self.start_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                self.diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel[index]-1] == 2): # slewgear
            if(self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                self.start_motor_current_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 1):
                self.diagnostic_motor_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 2):
                self.start_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                self.diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel[index]-1] == 3): # motherboard
            if(self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                self.diagnostic_motherboard_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 1):
                self.diagnostic_motherboard_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 2):
                self.diagnostic_motherboard_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 3    
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                self.diagnostic_motherboard_arduino_command(self.diagnostics_channel[index], index)
                self.diagnostics_load_cell_temperature_off_board(self.diagnostics_channel[index], index)
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0
                
        # end of debug timing
        if(self.timing):
            if(self.diagnostics_channel[index] == self.diagnostics_channel_total[index] and self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                print(self.diagnostics_channel[index], self.diagnostic_select[self.diagnostics_channel[index]-1])
                print("Time of ", threading.current_thread().name, " is ", time.time() - self.start[index])

    def start_diagnostic_AND_controls(self, index = 0):
        # only worry about 8 channels
        while self.run_thread:
            if(self.verbose_control):
                print("----------------------------")
            self.select_diagnostic(index)
            self.diagnostics_channel[index] = self.diagnostics_channel[index] + 1
            if(self.diagnostics_channel[index] >= self.diagnostics_channel_total[index] + 1):
                self.diagnostics_channel[index] = self.diagnostics_channel_reset[index]
            self.select_controls(index)
            self.controls_channel[index] = self.controls_channel[index] + 1
            self.select_controls(index)
            self.controls_channel[index] = self.controls_channel[index] + 1
            self.select_controls(index)
            self.controls_channel[index] = self.controls_channel[index] + 1
            self.select_controls(index)
            self.controls_channel[index] = self.controls_channel[index] + 1
            if(self.controls_channel[index] >= self.controls_channel_total[index]):
                self.controls_channel[index] = self.controls_channel_reset[index]

            if(self.verbose_control):
                time.sleep(1)

    def index_0_thread(self):
        self.start_diagnostic_AND_controls(index = 0)

    def index_1_thread(self):
        self.start_diagnostic_AND_controls(index = 1)

    def start_diagnostics_AND_controls_thread(self, index):
        if(index == 0):
            self.run_thread = True
            self.d_and_c = None
            self.d_and_c = threading.Thread(target=self.index_0_thread, name="Arduino Mega Thread")
            self.d_and_c.daemon = True
            self.d_and_c.start()
        else:
            self.run_thread = True
            self.d_and_c1 = None
            self.d_and_c1 = threading.Thread(target=self.index_1_thread, name="LattePanda Thread")
            self.d_and_c1.daemon = True
            self.d_and_c1.start()

    def get_diagnostics_array(self):
        return self.diagnostics_vals
    
    def reset_controls_array(self):
        self.controls_vals = np.zeros((16, 6), int)
        self.first_time_setup = 1

    def stop_thread(self):
        self.run_thread = False

    def init_pygame(self, Output_Res=(1280, 720)):
        self.Output_Res = Output_Res
        self.screen = pygame.Surface(self.Output_Res)
        self.font = pygame.font.Font(None, 36)
        self.small = pygame.font.Font(None, 26)

        # Initialize Pygame screen
        self.screen.fill((0, 0, 0))

        self.clock = pygame.time.Clock()

    def update_pygames_screen(self):
        # Update Pygame screen
        # pygame.display.flip()
        """Convert Pygame surface to PIL image."""
        image_str = pygame.image.tostring(self.screen, 'RGB')
        width, height = self.screen.get_size()
        img = Image.frombytes('RGB', (width, height), image_str)
        img_tk = ImageTk.PhotoImage(image=img)

        self.clock.tick(60)
        # end program 
        return img_tk
    
    def handler(self): 
        # clear pygame screen
        self.screen.fill((0, 0, 0))

    def can_flip(self):
        # Check if at least 100 milliseconds have passed since the last flip
        return pygame.time.get_ticks() - self.last_flip_time >= 200

    def control_motor_OR_actutor(self, channel_Numb, select, channel_names, verbose = False):
        # def control_motor_arduino_command(self, Channel_Numb, EN, EN_EFUSE, PWM, FR, BRAKE, index):
        # def control_actuator_arduino_command(self, Channel_Numb, EN_EFUSE, PWM, FR, index = 0):

        # Both - channel number, EN_EFUSE, PWM, FR
        # motor - EN motor, bake

        # Motor:
        # self.controls_vals[0] = Motor Enable
        # self.controls_vals[1] = ENable EFUSE
        # self.controls_vals[2] = PWM
        # self.controls_vals[3] = FR
        # self.controls_vals[4] = BRAKE

        right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
        left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2

        if(right_t > left_t):
            direction = 1 # go forward
        elif(right_t < left_t):
            direction = 0 # go back
        else:
            direction = 1
        

        trigger = max(right_t, left_t)

        left = 0

        bucket_wheel = 1

        for i, name in enumerate(channel_names):
           if "Drive Motor" in name:
               if(i == channel_Numb - 1):
                   bucket_wheel = 0
                   break

        for i, name in enumerate(channel_names):
           if "Left Drive Motor" in name:
               if(i == channel_Numb - 1):
                   left = 1
                   break

        motor_speed = self.maximum_voltage*trigger

        if(select == 0 or select == 2):
            if(self.controller): # if the controller is connected
                if(bucket_wheel):
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('X_Button')):
                            self.controls_vals[channel_Numb-1][1] = not self.controls_vals[channel_Numb-1][1]
                            self.controls_vals[channel_Numb-1][0] = not self.controls_vals[channel_Numb-1][1]
                            self.last_flip_time = pygame.time.get_ticks()
                    if(self.Get_Button_From_Controller('Y_Button')):
                        self.controls_vals[channel_Numb-1][2] = motor_speed
                        self.controls_vals[channel_Numb-1][3] = direction
                    self.controls_vals[channel_Numb-1][4] = self.Get_Button_From_Controller('B_Button')
                    if(self.controls_vals[channel_Numb-1][4]):
                        self.controls_vals[channel_Numb-1][2] = 0
                    # self.controls_vals[channel_Numb-1][0] = not self.controls_vals[channel_Numb-1][3]
                else:
                    # if self.can_flip():
                    #     if(self.Get_Button_From_Controller('X_Button')):
                    #         self.controls_vals[channel_Numb-1][1] = not self.controls_vals[channel_Numb-1][1]
                    #         self.last_flip_time = pygame.time.get_ticks()
                    self.controls_vals[channel_Numb-1][2] = motor_speed
                    if(left == 0):
                        self.controls_vals[channel_Numb-1][3] = direction
                    else:
                        self.controls_vals[channel_Numb-1][3] = not direction
                    self.controls_vals[channel_Numb-1][4] = not self.Get_Button_From_Controller('B_Button')
                    if(self.controls_vals[channel_Numb-1][4] == 0):
                        self.controls_vals[channel_Numb-1][2] = 0
                    self.controls_vals[channel_Numb-1][0] = not self.controls_vals[channel_Numb-1][3]
            else:
                self.controls_vals[channel_Numb-1][0] = 0
                self.controls_vals[channel_Numb-1][1] = 0
                self.controls_vals[channel_Numb-1][2] = 0
                self.controls_vals[channel_Numb-1][3] = 1
                self.controls_vals[channel_Numb-1][4] = 1
        
            if(verbose):
                print("-----------------------------")
                print("EN: ", self.controls_vals[channel_Numb-1][0])
                print("EN EFUSE: ", self.controls_vals[channel_Numb-1][1])
                print("PWM: ", self.controls_vals[channel_Numb-1][2])
                print("FR: ", self.controls_vals[channel_Numb-1][3])
                print("BRAKE: ", self.controls_vals[channel_Numb-1][4])
                print("-----------------------------")

            signals = ['MODE', 'CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = [bucket_wheel, channel_Numb - 1, self.controls_vals[channel_Numb-1][0], self.controls_vals[channel_Numb-1][2], self.controls_vals[channel_Numb-1][3], self.controls_vals[channel_Numb-1][4]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.font.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.font.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 50

        # Actuator:
        # self.controls_vals[0] = ENable EFUSE
        # self.controls_vals[1] = PWM
        # self.controls_vals[2] = FR
        # self.control_actuator_arduino_command(self.controls_channel[index], self.controls_vals[self.controls_channel[index]-1][0], self.controls_vals[self.controls_channel[index]-1][1], self.controls_vals[self.controls_channel[index]-1][2], index)
                
        elif(select == 1):
            if(self.controller): # if the controller is connected
                if self.can_flip():
                    if(self.Get_Button_From_Controller('X_Button')):
                        self.controls_vals[channel_Numb-1][0] = not self.controls_vals[channel_Numb-1][0]
                        self.last_flip_time = pygame.time.get_ticks()
                self.controls_vals[channel_Numb-1][1] = motor_speed
                self.controls_vals[channel_Numb-1][2] = direction
            else:
                self.controls_vals[channel_Numb-1][0] = 0
                self.controls_vals[channel_Numb-1][1] = 0
                self.controls_vals[channel_Numb-1][2] = 0

            if(verbose):
                print("-----------------------------")
                print("EN: ", self.controls_vals[channel_Numb-1][0])
                print("PWM: ", self.controls_vals[channel_Numb-1][1])
                print("FR: ", self.controls_vals[channel_Numb-1][2])
                print("-----------------------------")

            signals = ['CHANNEL', 'PWM', 'FR', 'STOP']
            signal_states = [channel_Numb - 1, self.controls_vals[channel_Numb-1][1], self.controls_vals[channel_Numb-1][2], self.timing_flag[channel_Numb-1]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.font.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.font.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 50

    def get_controls_array(self):
        return self.controls_vals
    
    def drive_controls(self, channel_names):
        driveFR = None
        driveFL = None
        driveRR = None
        driveRL = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Front Left Drive Motor" in name:
                driveFL = i
            elif "Front Right Drive Motor" in name:
                driveFR = i
            elif "Rear Left Drive Motor" in name:
                driveRL = i
            elif "Rear Right Drive Motor" in name:
                driveRR = i

        print(channel_names)

        print("driveFL: ", driveFL)
        print("driveFR: ", driveFR)
        print("driveRL: ", driveRL)
        print("driveRR: ", driveRR)

        if(driveFR is not None and driveFL is not None and driveRR is not None and driveRL is not None):

            if(self.first_time_setup):
                # set mode to 0
                self.controls_vals[driveFL][5] = 0 # one to behold the slow fast key
                self.first_time_setup = 0 

            if self.can_flip():
                if(self.Get_Button_From_Controller('X_Button')):
                    self.controls_vals[driveFL][5] = not self.controls_vals[driveFL][5]
                    self.last_flip_time = pygame.time.get_ticks()

            # Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
            #                   'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
            #                   'A_Button', 'B_Button', 'Y_Button', 'X_Button', 'L1_Button', 'R1_Button',
            #                   'Menu', 'Select', 'Left_Stick_In', 'Right_Stick_In']

            right_x = self.Get_Button_From_Controller('Right_Joystick_X')
            # right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
            # left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2
            left_y = self.Get_Button_From_Controller('Left_Joystick_Y')

            print(left_y)


            if(left_y > 0):
                direction = 1 # go forward
            else:
                direction = 0 # go back

            trigger = max(0, (abs(left_y)-self.dead_zone)*(1/(1-self.dead_zone)))

            if(self.controls_vals[driveFL][5]):
                left_side_motors = self.maximum_voltage*trigger*(1.0-max(0, (right_x-self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
                right_side_motors = self.maximum_voltage*trigger*(1.0+min(0, (right_x+self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
            else:
                left_side_motors = 75*trigger*(1.0-max(0, (right_x-self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
                right_side_motors = 75*trigger*(1.0+min(0, (right_x+self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss

            if(right_side_motors > left_side_motors): # moving direction
                if(right_side_motors/3 > left_side_motors):
                    left_side_motors = right_side_motors/3
            elif(right_side_motors < left_side_motors):
                if(right_side_motors < left_side_motors/3):
                    right_side_motors = left_side_motors/3


            # Motor:
            # self.controls_vals[0] = Motor Enable
            # self.controls_vals[1] = ENable EFUSE
            # self.controls_vals[2] = PWM
            # self.controls_vals[3] = FR
            # self.controls_vals[4] = BRAKE

            # right
            # front
            if(self.controller): 
                # self.controls_vals[driveFR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFR][3] = direction
                self.controls_vals[driveFR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFR][4] == 0):
                    self.controls_vals[driveFR][2] = 0
                else:
                    self.controls_vals[driveFR][2] = right_side_motors
                self.controls_vals[driveFR][0] = not self.controls_vals[driveFR][3]

                # rear
                # self.controls_vals[driveRR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRR][3] = direction
                self.controls_vals[driveRR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRR][4] == 0):
                    self.controls_vals[driveRR][2] = 0
                else:
                    self.controls_vals[driveRR][2] = right_side_motors
                self.controls_vals[driveRR][0] = not self.controls_vals[driveRR][3]

                # left
                # front
                # self.controls_vals[driveFL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFL][3] = not direction
                self.controls_vals[driveFL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFL][4] == 0):
                    self.controls_vals[driveFL][2] = 0
                else:
                    self.controls_vals[driveFL][2] = left_side_motors
                self.controls_vals[driveFL][0] = not self.controls_vals[driveFL][3]

                # rear
                # self.controls_vals[driveRL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRL][3] = not direction
                self.controls_vals[driveRL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRL][4] == 0):
                    self.controls_vals[driveRL][2] = 0
                else:
                    self.controls_vals[driveRL][2] = left_side_motors
                self.controls_vals[driveRL][0] = not self.controls_vals[driveRL][3]
            else:
                self.controls_vals[driveFR][0] = 0
                self.controls_vals[driveFR][1] = 1
                self.controls_vals[driveFR][2] = 0
                self.controls_vals[driveFR][3] = 1
                self.controls_vals[driveFR][4] = 1 

                self.controls_vals[driveRR][0] = 0
                self.controls_vals[driveRR][1] = 1
                self.controls_vals[driveRR][2] = 0
                self.controls_vals[driveRR][3] = 1
                self.controls_vals[driveRR][4] = 1 

                self.controls_vals[driveFL][0] = 0
                self.controls_vals[driveFL][1] = 1
                self.controls_vals[driveFL][2] = 0
                self.controls_vals[driveFL][3] = 1
                self.controls_vals[driveFL][4] = 1 

                self.controls_vals[driveRL][0] = 0
                self.controls_vals[driveRL][1] = 1
                self.controls_vals[driveRL][2] = 0
                self.controls_vals[driveRL][3] = 1
                self.controls_vals[driveRL][4] = 1 

            # bucketwheel
            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFR], self.controls_vals[driveFR][0], self.controls_vals[driveFR][2], self.controls_vals[driveFR][3], self.controls_vals[driveFR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRR], self.controls_vals[driveRR][0], self.controls_vals[driveRR][2], self.controls_vals[driveRR][3], self.controls_vals[driveRR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 240

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFL], self.controls_vals[driveFL][0], self.controls_vals[driveFL][2], self.controls_vals[driveFL][3], self.controls_vals[driveFL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 380

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRL], self.controls_vals[driveRL][0], self.controls_vals[driveRL][2], self.controls_vals[driveRL][3], self.controls_vals[driveRL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 520

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
        else:
            # bucketwheel
            signals = ['drive_front_right', 'drive_rear_right', 'drive_front_left', 'drive_rear_left']
            signal_states = [driveFR is not None, driveRR is not None, driveFL is not None, driveRL is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

    def reverse_drive_controls(self, channel_names):
        driveFR = None
        driveFL = None
        driveRR = None
        driveRL = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Front Left Drive Motor" in name:
                driveFL = i
            elif "Front Right Drive Motor" in name:
                driveFR = i
            elif "Rear Left Drive Motor" in name:
                driveRL = i
            elif "Rear Right Drive Motor" in name:
                driveRR = i

        print(channel_names)

        print("driveFL: ", driveFL)
        print("driveFR: ", driveFR)
        print("driveRL: ", driveRL)
        print("driveRR: ", driveRR)

        if(driveFR is not None and driveFL is not None and driveRR is not None and driveRL is not None):

            if(self.first_time_setup):
                # set mode to 0
                self.controls_vals[driveFL][5] = 0 # one to behold the slow fast key
                self.first_time_setup = 0 

            if self.can_flip():
                if(self.Get_Button_From_Controller('X_Button')):
                    self.controls_vals[driveFL][5] = not self.controls_vals[driveFL][5]
                    self.last_flip_time = pygame.time.get_ticks()

            # Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
            #                   'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
            #                   'A_Button', 'B_Button', 'Y_Button', 'X_Button', 'L1_Button', 'R1_Button',
            #                   'Menu', 'Select', 'Left_Stick_In', 'Right_Stick_In']

            right_x = self.Get_Button_From_Controller('Right_Joystick_X')
            # right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
            # left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2
            left_y = self.Get_Button_From_Controller('Left_Joystick_Y')

            print(left_y)


            if(left_y > 0):
                direction = 1 # go forward
            else:
                direction = 0 # go back

            trigger = max(0, (abs(left_y)-self.dead_zone)*(1/(1-self.dead_zone)))

            if(self.controls_vals[driveFL][5]):
                left_side_motors = self.maximum_voltage*trigger*(1.0-max(0, (right_x-self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
                right_side_motors = self.maximum_voltage*trigger*(1.0+min(0, (right_x+self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
            else:
                left_side_motors = 75*trigger*(1.0-max(0, (right_x-self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss
                right_side_motors = 75*trigger*(1.0+min(0, (right_x+self.dead_zone)*(1/(1-self.dead_zone)))) + self.upper_loss

            if(right_side_motors > left_side_motors): # moving direction
                if(right_side_motors/3 > left_side_motors):
                    left_side_motors = right_side_motors/3
            elif(right_side_motors < left_side_motors):
                if(right_side_motors < left_side_motors/3):
                    right_side_motors = left_side_motors/3


            # Motor:
            # self.controls_vals[0] = Motor Enable
            # self.controls_vals[1] = ENable EFUSE
            # self.controls_vals[2] = PWM
            # self.controls_vals[3] = FR
            # self.controls_vals[4] = BRAKE

            # right
            # front
            if(self.controller): 
                # self.controls_vals[driveFR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFR][3] = not direction
                self.controls_vals[driveFR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFR][4] == 0):
                    self.controls_vals[driveFR][2] = 0
                else:
                    self.controls_vals[driveFR][2] = left_side_motors
                self.controls_vals[driveFR][0] = not self.controls_vals[driveFR][3]

                # rear
                # self.controls_vals[driveRR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRR][3] = not direction
                self.controls_vals[driveRR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRR][4] == 0):
                    self.controls_vals[driveRR][2] = 0
                else:
                    self.controls_vals[driveRR][2] = left_side_motors
                self.controls_vals[driveRR][0] = not self.controls_vals[driveRR][3]

                # left
                # front
                # self.controls_vals[driveFL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFL][3] = direction
                self.controls_vals[driveFL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFL][4] == 0):
                    self.controls_vals[driveFL][2] = 0
                else:
                    self.controls_vals[driveFL][2] = right_side_motors
                self.controls_vals[driveFL][0] = not self.controls_vals[driveFL][3]

                # rear
                # self.controls_vals[driveRL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRL][3] = direction
                self.controls_vals[driveRL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRL][4] == 0):
                    self.controls_vals[driveRL][2] = 0
                else:
                    self.controls_vals[driveRL][2] = right_side_motors
                self.controls_vals[driveRL][0] = not self.controls_vals[driveRL][3]
            else:
                self.controls_vals[driveFR][0] = 0
                self.controls_vals[driveFR][1] = 1
                self.controls_vals[driveFR][2] = 0
                self.controls_vals[driveFR][3] = 1
                self.controls_vals[driveFR][4] = 1 

                self.controls_vals[driveRR][0] = 0
                self.controls_vals[driveRR][1] = 1
                self.controls_vals[driveRR][2] = 0
                self.controls_vals[driveRR][3] = 1
                self.controls_vals[driveRR][4] = 1 

                self.controls_vals[driveFL][0] = 0
                self.controls_vals[driveFL][1] = 1
                self.controls_vals[driveFL][2] = 0
                self.controls_vals[driveFL][3] = 1
                self.controls_vals[driveFL][4] = 1 

                self.controls_vals[driveRL][0] = 0
                self.controls_vals[driveRL][1] = 1
                self.controls_vals[driveRL][2] = 0
                self.controls_vals[driveRL][3] = 1
                self.controls_vals[driveRL][4] = 1 

            # bucketwheel
            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFR], self.controls_vals[driveFR][0], self.controls_vals[driveFR][2], self.controls_vals[driveFR][3], self.controls_vals[driveFR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRR], self.controls_vals[driveRR][0], self.controls_vals[driveRR][2], self.controls_vals[driveRR][3], self.controls_vals[driveRR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 240

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFL], self.controls_vals[driveFL][0], self.controls_vals[driveFL][2], self.controls_vals[driveFL][3], self.controls_vals[driveFL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 380

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRL], self.controls_vals[driveRL][0], self.controls_vals[driveRL][2], self.controls_vals[driveRL][3], self.controls_vals[driveRL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 520

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
        else:
            # bucketwheel
            signals = ['drive_front_right', 'drive_rear_right', 'drive_front_left', 'drive_rear_left']
            signal_states = [driveFR is not None, driveRR is not None, driveFL is not None, driveRL is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

    def tank_drive_controls(self, channel_names):
        driveFR = None
        driveFL = None
        driveRR = None
        driveRL = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Front Left Drive Motor" in name:
                driveFL = i
            elif "Front Right Drive Motor" in name:
                driveFR = i
            elif "Rear Left Drive Motor" in name:
                driveRL = i
            elif "Rear Right Drive Motor" in name:
                driveRR = i

        print(channel_names)

        print("driveFL: ", driveFL)
        print("driveFR: ", driveFR)
        print("driveRL: ", driveRL)
        print("driveRR: ", driveRR)

        if(driveFR is not None and driveFL is not None and driveRR is not None and driveRL is not None):

            if(self.first_time_setup):
                # set mode to 0
                self.controls_vals[driveFL][5] = 0 # one to behold the slow fast key
                self.first_time_setup = 0 

            if self.can_flip():
                if(self.Get_Button_From_Controller('X_Button')):
                    self.controls_vals[driveFL][5] = not self.controls_vals[driveFL][5]
                    self.last_flip_time = pygame.time.get_ticks()

            # Controls_Names = ['Left_Joystick_X', 'Left_Joystick_Y', 'Right_Joystick_X', 'Right_Joystick_Y',
            #                   'Dpad_Up', 'Dpad_Down', 'Dpad_Left', 'Dpad_Right', 'L2_Trigger', 'R2_Trigger',
            #                   'A_Button', 'B_Button', 'Y_Button', 'X_Button', 'L1_Button', 'R1_Button',
            #                   'Menu', 'Select', 'Left_Stick_In', 'Right_Stick_In']

            right_y = self.Get_Button_From_Controller('Right_Joystick_Y')
            # right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
            # left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2
            left_y = self.Get_Button_From_Controller('Left_Joystick_Y')

            print(left_y)


            if(left_y > 0):
                direction_l = 1 # go forward
            else:
                direction_l = 0 # go back

            if(right_y > 0):
                direction_r = 1 # go forward
            else:
                direction_r = 0 # go back

            if(self.controls_vals[driveFL][5]):
                trig_right = self.maximum_voltage*abs(right_y)
                trig_left = self.maximum_voltage*abs(left_y)
            else:
                trig_right = 75*abs(right_y)
                trig_left = 75*abs(left_y)


            # Motor:
            # self.controls_vals[0] = Motor Enable
            # self.controls_vals[1] = ENable EFUSE
            # self.controls_vals[2] = PWM
            # self.controls_vals[3] = FR
            # self.controls_vals[4] = BRAKE

            # right
            # front
            if(self.controller): 
                # self.controls_vals[driveFR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFR][3] = direction_r
                self.controls_vals[driveFR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFR][4] == 0):
                    self.controls_vals[driveFR][2] = 0
                else:
                    self.controls_vals[driveFR][2] = trig_right
                self.controls_vals[driveFR][0] = not self.controls_vals[driveFR][3]

                # rear
                # self.controls_vals[driveRR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRR][3] = direction_r
                self.controls_vals[driveRR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRR][4] == 0):
                    self.controls_vals[driveRR][2] = 0
                else:
                    self.controls_vals[driveRR][2] = trig_right
                self.controls_vals[driveRR][0] = not self.controls_vals[driveRR][3]

                # left
                # front
                # self.controls_vals[driveFL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFL][3] = not direction_l
                self.controls_vals[driveFL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFL][4] == 0):
                    self.controls_vals[driveFL][2] = 0
                else:
                    self.controls_vals[driveFL][2] = trig_left
                self.controls_vals[driveFL][0] = not self.controls_vals[driveFL][3]

                # rear
                # self.controls_vals[driveRL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRL][3] = not direction_l
                self.controls_vals[driveRL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRL][4] == 0):
                    self.controls_vals[driveRL][2] = 0
                else:
                    self.controls_vals[driveRL][2] = trig_left
                self.controls_vals[driveRL][0] = not self.controls_vals[driveRL][3]
            else:
                self.controls_vals[driveFR][0] = 0
                self.controls_vals[driveFR][1] = 1
                self.controls_vals[driveFR][2] = 0
                self.controls_vals[driveFR][3] = 1
                self.controls_vals[driveFR][4] = 1 

                self.controls_vals[driveRR][0] = 0
                self.controls_vals[driveRR][1] = 1
                self.controls_vals[driveRR][2] = 0
                self.controls_vals[driveRR][3] = 1
                self.controls_vals[driveRR][4] = 1 

                self.controls_vals[driveFL][0] = 0
                self.controls_vals[driveFL][1] = 1
                self.controls_vals[driveFL][2] = 0
                self.controls_vals[driveFL][3] = 1
                self.controls_vals[driveFL][4] = 1 

                self.controls_vals[driveRL][0] = 0
                self.controls_vals[driveRL][1] = 1
                self.controls_vals[driveRL][2] = 0
                self.controls_vals[driveRL][3] = 1
                self.controls_vals[driveRL][4] = 1 

            # bucketwheel
            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFR], self.controls_vals[driveFR][0], self.controls_vals[driveFR][2], self.controls_vals[driveFR][3], self.controls_vals[driveFR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRR], self.controls_vals[driveRR][0], self.controls_vals[driveRR][2], self.controls_vals[driveRR][3], self.controls_vals[driveRR][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 240

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveFL], self.controls_vals[driveFL][0], self.controls_vals[driveFL][2], self.controls_vals[driveFL][3], self.controls_vals[driveFL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 380

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK', 'MODE']
            signal_states = [channel_names[driveRL], self.controls_vals[driveRL][0], self.controls_vals[driveRL][2], self.controls_vals[driveRL][3], self.controls_vals[driveRL][4], self.controls_vals[driveFL][5]]  # Example states, modify as needed

            y = 520

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
        else:
            # bucketwheel
            signals = ['drive_front_right', 'drive_rear_right', 'drive_front_left', 'drive_rear_left']
            signal_states = [driveFR is not None, driveRR is not None, driveFL is not None, driveRL is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

    def mine_controls(self, channel_names):
        bucket_wheel = None
        front_auger = None
        arm_lift = None
        slew_gear = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Front Auger Motor" in name:
                front_auger = i
            elif "Bucketwheel Motor" in name:
                bucket_wheel = i
            elif "Excavation Arm Lift Actuator" in name:
                arm_lift = i
            elif "Pivot Slew Gear" in name:
                slew_gear = i

        # print(channel_names)

        # print("bucket_wheel: ", bucket_wheel)
        # print("front_auger: ", front_auger)
        # print("arm_lift: ", arm_lift)

        if(front_auger is not None and bucket_wheel is not None and arm_lift is not None and slew_gear is not None):

            # right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
            # left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2

            # if(right_t > left_t):
            #     direction = 1 # go forward
            # elif(right_t < left_t):
            #     direction = 0 # go back
            # else:
            #     direction = 1
            

            # trigger = max(right_t, left_t)

            # motor_speed = self.maximum_voltage*trigger

            # actuator
            right_y = self.Get_Button_From_Controller('Right_Joystick_Y')
            # print("RIGHT_Y", right_y)
            if(right_y < 0):
                direction_act = 1 # go forward
            else:
                direction_act = 0 # go back
            trigger_act = 100*max(0, (abs(right_y)-self.dead_zone)*(1/(1-self.dead_zone)))
            # print("trigger_act", trigger_act)
            
            # slew
            left_x = self.Get_Button_From_Controller('Left_Joystick_Y')

            # print("LEFT_X", left_x)

            if(left_x > 0):
                direction_slew = 1 # go forward
            else:
                direction_slew = 0 # go back

            trigger_slew = 127*max(0, (abs(left_x)-self.dead_zone)*(1/(1-self.dead_zone)))

            if(self.controller):
                # select between auger and bucketwheel
                if(self.first_time_setup):
                    # bucketwheel speed: 75 
                    self.controls_vals[bucket_wheel][2] = 75
                    self.controls_vals[bucket_wheel][3] = 0 # forward
                    self.controls_vals[bucket_wheel][0] = 1 # disable motor
                    self.controls_vals[front_auger][2] = 30
                    self.controls_vals[front_auger][3] = 0 # forward
                    self.controls_vals[front_auger][0] = 1 # disable motor
                    self.first_time_setup = 0 
                if self.can_flip():
                    if(self.Get_Button_From_Controller('Menu')):
                        self.auger_or_bucket = not self.auger_or_bucket
                        self.last_flip_time = pygame.time.get_ticks()

                # control bucketwheel
                if(self.auger_or_bucket):
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('A_Button')):
                            self.controls_vals[bucket_wheel][1] = not self.controls_vals[bucket_wheel][1]
                            self.controls_vals[bucket_wheel][0] = not self.controls_vals[bucket_wheel][1]
                            self.last_flip_time = pygame.time.get_ticks()
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('Y_Button')):
                            if(self.controls_vals[bucket_wheel][2] < 255):
                                self.controls_vals[bucket_wheel][2] = self.controls_vals[bucket_wheel][2] + 5
                                self.last_flip_time = pygame.time.get_ticks()
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('X_Button')):
                            if(self.controls_vals[bucket_wheel][2] > 0):
                                self.controls_vals[bucket_wheel][2] = self.controls_vals[bucket_wheel][2] - 5
                                self.last_flip_time = pygame.time.get_ticks()
                            
                    self.controls_vals[bucket_wheel][4] = 0 # active high break?
                else:
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('A_Button')):
                            self.controls_vals[front_auger][1] = not self.controls_vals[front_auger][1]
                            self.controls_vals[front_auger][0] = not self.controls_vals[front_auger][1]
                            self.last_flip_time = pygame.time.get_ticks()
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('Y_Button')):
                            if(self.controls_vals[front_auger][2] < 255):
                                self.controls_vals[front_auger][2] = self.controls_vals[front_auger][2] + 5
                                self.last_flip_time = pygame.time.get_ticks()
                    if self.can_flip():
                        if(self.Get_Button_From_Controller('X_Button')):
                            if(self.controls_vals[front_auger][2] > 0):
                                self.controls_vals[front_auger][2] = self.controls_vals[front_auger][2] - 5
                                self.last_flip_time = pygame.time.get_ticks()
                            
                    self.controls_vals[front_auger][4] = 0 # active high break?

                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[bucket_wheel][1] = 0
                    self.controls_vals[bucket_wheel][0] = 1
                    self.controls_vals[bucket_wheel][4] = 1 # active high break?
                else:
                    self.controls_vals[bucket_wheel][4] = 0 # active high break?

                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[front_auger][1] = 0
                    self.controls_vals[front_auger][0] = 1
                    self.controls_vals[front_auger][4] = 1 # active high break?
                else:
                    self.controls_vals[front_auger][4] = 0 # active high break?

                # control of lift actuator
                self.controls_vals[arm_lift][0] = 1
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[arm_lift][1] = 0
                else:
                    self.controls_vals[arm_lift][1] = trigger_act
                self.controls_vals[arm_lift][2] = direction_act

                # turn off slew gear
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[slew_gear][0] = 1 # disable
                    self.controls_vals[slew_gear][1] = 0
                    self.controls_vals[slew_gear][2] = 0
                    self.controls_vals[slew_gear][3] = direction_slew
                    self.controls_vals[slew_gear][4] = 1 # break 
                else:
                    self.controls_vals[slew_gear][0] = 0
                    self.controls_vals[slew_gear][1] = 1
                    self.controls_vals[slew_gear][2] = trigger_slew
                    self.controls_vals[slew_gear][3] = direction_slew
                    self.controls_vals[slew_gear][4] = 0 # no break 

            else:
                # turn off bucketwheel
                self.controls_vals[bucket_wheel][0] = 0
                self.controls_vals[bucket_wheel][1] = 1
                self.controls_vals[bucket_wheel][2] = 0
                self.controls_vals[bucket_wheel][3] = 1
                self.controls_vals[bucket_wheel][4] = 1

                # mirror auger
                self.controls_vals[front_auger][0] = 0
                self.controls_vals[front_auger][1] = 1
                self.controls_vals[front_auger][2] = 0
                self.controls_vals[front_auger][3] = 1
                self.controls_vals[front_auger][4] = 1 
            
                # turn off acutator
                self.controls_vals[arm_lift][0] = 0
                self.controls_vals[arm_lift][1] = 0
                self.controls_vals[arm_lift][2] = 0

                # turn off slew gear
                self.controls_vals[slew_gear][0] = 0
                self.controls_vals[slew_gear][1] = 1
                self.controls_vals[slew_gear][2] = 0
                self.controls_vals[slew_gear][3] = 1
                self.controls_vals[slew_gear][4] = 1 

            # bucketwheel
            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = [channel_names[bucket_wheel], self.controls_vals[bucket_wheel][0], self.controls_vals[bucket_wheel][2], self.controls_vals[bucket_wheel][3], self.controls_vals[bucket_wheel][4]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = [channel_names[front_auger], self.controls_vals[front_auger][0], self.controls_vals[front_auger][2], self.controls_vals[front_auger][3], self.controls_vals[front_auger][4]]  # Example states, modify as needed

            y = 310

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30

            #  actuator
            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[arm_lift], self.controls_vals[arm_lift][1], self.controls_vals[arm_lift][2]]  # Example states, modify as needed

            y = 520

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30

            #  slew gear
            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = [channel_names[slew_gear], self.controls_vals[slew_gear][0], self.controls_vals[slew_gear][2], self.controls_vals[slew_gear][3], self.controls_vals[slew_gear][4]]  # Example states, modify as needed

            y = 730

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30

            # Draw the open box
            # bucketwheel selected
            if(self.auger_or_bucket):
                pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(200, 60, 400, 210), 2)  # Green open box
            # auger selected
            else:
                pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(200, 270, 400, 210), 2)  # Green open box

        else:
            # front_auger is not None and bucket_wheel is not None and arm_lift is not None
            signals = ['front_auger', 'bucket_wheel', 'arm_lift', 'slew_gear']
            signal_states = [front_auger is not None, bucket_wheel is not None, arm_lift is not None, slew_gear is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
    
    def docking_excavator(self, channel_names):
        rear_auger = None
        lower_ramp_act = None
        batter_locking_act_1 = None
        batter_locking_act_2 = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Ramps Actuator" in name:
                lower_ramp_act = i
            elif "Battery Lock 1 Actuator" in name:
                batter_locking_act_1 = i
            elif "Battery Lock 2 Actuator" in name:
                batter_locking_act_2 = i
            elif "Rear Auger Motor" in name:
                rear_auger = i

        driveFR = None
        driveFL = None
        driveRR = None
        driveRL = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Front Left Drive Motor" in name:
                driveFL = i
            elif "Front Right Drive Motor" in name:
                driveFR = i
            elif "Rear Left Drive Motor" in name:
                driveRL = i
            elif "Rear Right Drive Motor" in name:
                driveRR = i

        print(channel_names)

        print("driveFL: ", driveFL)
        print("driveFR: ", driveFR)
        print("driveRL: ", driveRL)
        print("driveRR: ", driveRR)

        if(lower_ramp_act is not None and batter_locking_act_1 is not None and batter_locking_act_2 is not None and rear_auger is not None and driveFR is not None and driveFL is not None and driveRR is not None and driveRL is not None):

            if(self.first_time_setup):
                self.controls_vals[rear_auger][2] = 30
                self.controls_vals[rear_auger][3] = 1 # forward
                self.controls_vals[rear_auger][0] = 1 # disable motor
                self.first_time_setup = 0 

            # ramp actuator
            left_y = self.Get_Button_From_Controller('Left_Joystick_Y')
            # print("RIGHT_Y", right_y)
            if(left_y < 0):
                direction_act_ramp = 1 # go forward
            else:
                direction_act_ramp = 0 # go back
            trigger_act_ramp = self.maximum_voltage*max(0, (abs(left_y)-self.dead_zone)*(1/(1-self.dead_zone)))
            # print("trigger_act", trigger_act)
            
            # battery locking
            right_y = self.Get_Button_From_Controller('Right_Joystick_Y')

            # print("LEFT_X", left_x)

            if(right_y > 0):
                direction_act_lock = 1 # go forward
            else:
                direction_act_lock = 0 # go back

            trigger_act_lock = self.maximum_voltage*max(0, (abs(right_y)-self.dead_zone)*(1/(1-self.dead_zone)))

            right_t = (self.Get_Button_From_Controller('R2_Trigger') + 1)/2
            left_t = (self.Get_Button_From_Controller('L2_Trigger') + 1)/2

            trig_drive = 75*max(right_t, left_t)

            if right_t > left_t:
                direction = 1
            else:
                direction = 0


            if(self.controller): 
                # control bucketwheel
                if self.can_flip():
                    if(self.Get_Button_From_Controller('A_Button')):
                        self.controls_vals[rear_auger][1] = not self.controls_vals[rear_auger][1]
                        self.controls_vals[rear_auger][0] = not self.controls_vals[rear_auger][1]
                        self.last_flip_time = pygame.time.get_ticks()
                if self.can_flip():
                    if(self.Get_Button_From_Controller('Y_Button')):
                        if(self.controls_vals[rear_auger][2] < 255):
                            self.controls_vals[rear_auger][2] = self.controls_vals[rear_auger][2] + 5
                            self.last_flip_time = pygame.time.get_ticks()
                # if self.can_flip():
                    # self.last_flip_time = pygame.time.get_ticks
                if self.can_flip():
                    if(self.Get_Button_From_Controller('X_Button')):
                        if(self.controls_vals[rear_auger][2] > 0):
                            self.controls_vals[rear_auger][2] = self.controls_vals[rear_auger][2] - 5
                            self.last_flip_time = pygame.time.get_ticks()
                        
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[rear_auger][1] = 0
                    self.controls_vals[rear_auger][0] = 1
                    self.controls_vals[rear_auger][4] = 1
                else:
                    self.controls_vals[rear_auger][4] = 0 # active high break?

                # ramp act
                self.controls_vals[lower_ramp_act][0] = 0
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[lower_ramp_act][1] = 0 
                else:
                    self.controls_vals[lower_ramp_act][1] = trigger_act_ramp
                self.controls_vals[lower_ramp_act][2] = direction_act_ramp

                # lock 1
                self.controls_vals[batter_locking_act_1][0] = 0
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[batter_locking_act_1][1] = 0
                else:
                    self.controls_vals[batter_locking_act_1][1] = trigger_act_lock
                self.controls_vals[batter_locking_act_1][2] = direction_act_lock

                # lock 2
                self.controls_vals[batter_locking_act_2][0] = 0
                if(self.Get_Button_From_Controller('B_Button')):
                    self.controls_vals[batter_locking_act_2][1] = 0
                else:
                    self.controls_vals[batter_locking_act_2][1] = trigger_act_lock
                self.controls_vals[batter_locking_act_2][2] = direction_act_lock

                # right
                # front
                # self.controls_vals[driveFR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFR][3] = direction
                self.controls_vals[driveFR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFR][4] == 0):
                    self.controls_vals[driveFR][2] = 0
                else:
                    self.controls_vals[driveFR][2] = trig_drive
                self.controls_vals[driveFR][0] = not self.controls_vals[driveFR][3]

                # rear
                # self.controls_vals[driveRR][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRR][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRR][3] = direction
                self.controls_vals[driveRR][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRR][4] == 0):
                    self.controls_vals[driveRR][2] = 0
                else:
                    self.controls_vals[driveRR][2] = trig_drive
                self.controls_vals[driveRR][0] = not self.controls_vals[driveRR][3]

                # left
                # front
                # self.controls_vals[driveFL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveFL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveFL][3] = not direction
                self.controls_vals[driveFL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveFL][4] == 0):
                    self.controls_vals[driveFL][2] = 0
                else:
                    self.controls_vals[driveFL][2] = trig_drive
                self.controls_vals[driveFL][0] = not self.controls_vals[driveFL][3]

                # rear
                # self.controls_vals[driveRL][0] = not self.Get_Button_From_Controller('X_Button')
                # self.controls_vals[driveRL][1] = not self.Get_Button_From_Controller('X_Button')
                self.controls_vals[driveRL][3] = not direction
                self.controls_vals[driveRL][4] = not self.Get_Button_From_Controller('B_Button')
                if(self.controls_vals[driveRL][4] == 0):
                    self.controls_vals[driveRL][2] = 0
                else:
                    self.controls_vals[driveRL][2] = trig_drive
                self.controls_vals[driveRL][0] = not self.controls_vals[driveRL][3]
            else:
                # mirror auger
                self.controls_vals[rear_auger][0] = 0
                self.controls_vals[rear_auger][1] = 1
                self.controls_vals[rear_auger][2] = 0
                self.controls_vals[rear_auger][3] = 1
                self.controls_vals[rear_auger][4] = 1 

                # turn off acutator
                self.controls_vals[lower_ramp_act][0] = 0
                self.controls_vals[lower_ramp_act][1] = 0
                self.controls_vals[lower_ramp_act][2] = 0

                # turn off acutator
                self.controls_vals[batter_locking_act_1][0] = 0
                self.controls_vals[batter_locking_act_1][1] = 0
                self.controls_vals[batter_locking_act_1][2] = 0

                # turn off acutator
                self.controls_vals[batter_locking_act_2][0] = 0
                self.controls_vals[batter_locking_act_2][1] = 0
                self.controls_vals[batter_locking_act_2][2] = 0
        
                # drive
                self.controls_vals[driveFR][0] = 0
                self.controls_vals[driveFR][1] = 1
                self.controls_vals[driveFR][2] = 0
                self.controls_vals[driveFR][3] = 1
                self.controls_vals[driveFR][4] = 1 

                self.controls_vals[driveRR][0] = 0
                self.controls_vals[driveRR][1] = 1
                self.controls_vals[driveRR][2] = 0
                self.controls_vals[driveRR][3] = 1
                self.controls_vals[driveRR][4] = 1 

                self.controls_vals[driveFL][0] = 0
                self.controls_vals[driveFL][1] = 1
                self.controls_vals[driveFL][2] = 0
                self.controls_vals[driveFL][3] = 1
                self.controls_vals[driveFL][4] = 1 

                self.controls_vals[driveRL][0] = 0
                self.controls_vals[driveRL][1] = 1
                self.controls_vals[driveRL][2] = 0
                self.controls_vals[driveRL][3] = 1
                self.controls_vals[driveRL][4] = 1 

            #  actuator
            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[lower_ramp_act], self.controls_vals[lower_ramp_act][1], self.controls_vals[lower_ramp_act][2]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
            
            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[batter_locking_act_1], self.controls_vals[batter_locking_act_1][1], self.controls_vals[batter_locking_act_1][2]]  # Example states, modify as needed

            y = 240

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[batter_locking_act_2], self.controls_vals[batter_locking_act_2][1], self.controls_vals[batter_locking_act_2][2]]  # Example states, modify as needed

            y = 380

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = [channel_names[rear_auger], self.controls_vals[rear_auger][0], self.controls_vals[rear_auger][2], self.controls_vals[rear_auger][3], self.controls_vals[rear_auger][4]]  # Example states, modify as needed

            y = 520

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

            signals = ['CHANNEL', 'EN', 'PWM', 'FR', 'BREAK']
            signal_states = ["Drive Motors", self.controls_vals[driveFR][0], self.controls_vals[driveFR][2], self.controls_vals[driveFR][3], self.controls_vals[driveFR][4]]  # Example states, modify as needed

            y = 660

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

        else:
            # front_auger is not None and bucket_wheel is not None and arm_lift is not None
            signals = ['lower_ramp_act', 'batter_locking_act_1', 'batter_locking_act_2', 'rear_auger', 'driveFR', 'driveFL', 'driveRR', 'driveRL']
            signal_states = [lower_ramp_act is not None, batter_locking_act_1 is not None, batter_locking_act_2 is not None, rear_auger is not None, not None, driveFR is not None, driveFL is not None, driveRR is not None, driveRL is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20

    def docking_dumptruck(self, channel_names):
        hopper_act_1 = None
        hopper_act_2 = None

        # get the channel number 
        for i, name in enumerate(channel_names):
            if "Hopper Tip 1 Actuator" in name:
                hopper_act_1 = i
            elif "Hopper Tip 2 Actuator" in name:
                hopper_act_2 = i

        if(hopper_act_1 is not None and hopper_act_2 is not None):
            # ramp actuator
            left_y = self.Get_Button_From_Controller('Left_Joystick_Y')
            # print("RIGHT_Y", right_y)
            if(left_y < 0):
                direction_act_hopper = 1 # go forward
            else:
                direction_act_hopper = 0 # go back
            trigger_act_hopper = self.maximum_voltage*max(0, (abs(left_y)-self.dead_zone)*(1/(1-self.dead_zone)))
            # print("trigger_act", trigger_act)

            if(self.controller):

                #hopper 1
                self.controls_vals[hopper_act_1][0] = 0
                self.controls_vals[hopper_act_1][1] = trigger_act_hopper
                self.controls_vals[hopper_act_1][2] = direction_act_hopper

                # hopper 2
                self.controls_vals[hopper_act_2][0] = 0
                self.controls_vals[hopper_act_2][1] = trigger_act_hopper
                self.controls_vals[hopper_act_2][2] = direction_act_hopper

            else:

                # turn off acutator
                self.controls_vals[hopper_act_1][0] = 0
                self.controls_vals[hopper_act_1][1] = 0
                self.controls_vals[hopper_act_1][2] = 0

                # turn off acutator
                self.controls_vals[hopper_act_2][0] = 0
                self.controls_vals[hopper_act_2][1] = 0
                self.controls_vals[hopper_act_2][2] = 0
        
            #  actuator
            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[hopper_act_1], self.controls_vals[hopper_act_1][1], self.controls_vals[hopper_act_1][2]]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30
            
            signals = ['CHANNEL', 'PWM', 'FR']
            signal_states = [channel_names[hopper_act_2], self.controls_vals[hopper_act_2][1], self.controls_vals[hopper_act_2][2]]  # Example states, modify as needed

            y = 310

            for signal, state in zip(signals, signal_states):
                # Render text
                if signal == 'PWM' or signal == 'CHANNEL':
                    text = self.small.render(f"{signal}: {state}", True, (255, 255, 255))
                else:
                    text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                    if state:
                        pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                    else:
                        pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 30

        else:
            # front_auger is not None and bucket_wheel is not None and arm_lift is not None
            signals = ['hopper_act_1', 'hopper_act_2']
            signal_states = [hopper_act_1 is not None, hopper_act_2 is not None]  # Example states, modify as needed

            y = 100

            for signal, state in zip(signals, signal_states):
                # Render text
                text = self.small.render(f"{signal}: ", True, (255, 255, 255))
                if state:
                    pygame.draw.circle(self.screen, (0, 255, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Green circle
                else:
                    pygame.draw.circle(self.screen, (255, 0, 0), (self.Output_Res[0] // 2 + 100, y), 10)  # Red circle
                text_rect = text.get_rect(center=(self.Output_Res[0] // 2, y))
                self.screen.blit(text, text_rect)
                y += 20
        
