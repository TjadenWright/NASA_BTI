# controls class

import pygame
import pygame.joystick
import serial.tools.list_ports
import time
from pygame.locals import *
import sys
import numpy as np
import threading

class Rover_Controls:
    def __init__(self, verbose = False, timing = False, maximum_voltage = 255, dead_zone = 0.05, upper_loss = 0.004, PC_or_PI = "PC"):
        # print out stuff
        self.verbose = verbose                       # debuggin purposes.
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
        self.controls_vals = np.zeros((16, 10), int)

        # diagnostics
        self.diagnostics_vals = np.zeros((16, 10))
        self.diagnostic_select = np.zeros(16)
        self.diagnostic_lock = [threading.Lock(), threading.Lock()]

        # more diagnostics
        self.start = [0] * 2

    
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
        time.sleep(1)

    def Disable_write_arduino(self, index = 0):
        self.arduino[index].close()

    def write_read(self, data, index = 0):
        # send a command with a \n at the end
        self.arduino[index].write(bytes(data + "\n", 'utf-8'))
        
        # Read from the serial port until data is received
        data = self.arduino[index].readline().decode('utf-8').strip()
        return str(data)
    
    def set_act_OR_motor(self, config=np.zeros(15)):
        self.act_OR_motor = config

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

        if(self.verbose):
            print(motor_control_command)
            print(self.write_read(motor_control_command, index))
        else:
            self.write_read(motor_control_command, index)

    def control_actuator_arduino_command(self, Channel_Numb, EN_EFUSE, PWM, FR, index = 0):
        actuator_control_command = "cActuator " + str(Channel_Numb) + " " + str(EN_EFUSE) + " " + str(FR) + " " + str(PWM)

        if(self.verbose):
            print(actuator_control_command)
            print(self.write_read(actuator_control_command, index))
        else:
            self.write_read(actuator_control_command, index)

    def start_motor_current_arduino_command(self, Channel_Numb, index = 0):
        motor_start_current_command = "sMotorCurrent " + str(Channel_Numb)

        if(self.verbose):
            print(motor_start_current_command)
            print(self.write_read(motor_start_current_command, index))
        else:
            self.write_read(motor_start_current_command, index)

    def diagnostic_motor_arduino_command(self, Channel_Numb, index = 0):
        motor_diagnostic_command = "dMotor " + str(Channel_Numb)
        data = self.write_read(motor_diagnostic_command, index)

        if(self.verbose):
            print(motor_diagnostic_command)
            print(data)

        # turn data int variables
        numbers = data.split()
        float_numb = [float(num) for num in numbers]
        left = min(len(float_numb), self.diagnostics_vals.shape[1])

        with self.diagnostic_lock[index]:
            self.diagnostics_vals[Channel_Numb-1, :left] = float_numb[:left]

    def start_motor_speed_arduino_command(self, Channel_Numb, index = 0):
        start_motor_diagnostic_speed_command = "sMotrSpeed " + str(Channel_Numb)

        if(self.verbose):
            print(start_motor_diagnostic_speed_command)
            print(self.write_read(start_motor_diagnostic_speed_command, index))
        else:
            self.write_read(start_motor_diagnostic_speed_command, index)

    def diagnostic_motor_speed_arduino_command(self, Channel_Numb, index = 0):
        motor_diagnostic_speed_command = "dMotrSpeed " + str(Channel_Numb)
        data = self.write_read(motor_diagnostic_speed_command, index)

        if(self.verbose):
            print(motor_diagnostic_speed_command)
            print(data)

        # turn data int variables
        numbers = data.split()
        float_numb = [float(num) for num in numbers]

        with self.diagnostic_lock[index]:
            self.diagnostics_vals[Channel_Numb-1, 4] = float_numb[0]

    def start_actuator_current_arduino_command(self, Channel_Numb, index = 0):
        start_actuator_diagnostic_current_command = "sActuatorCurrent " + str(Channel_Numb)

        if(self.verbose):
            print(start_actuator_diagnostic_current_command)
            print(self.write_read(start_actuator_diagnostic_current_command, index))
        else:
            self.write_read(start_actuator_diagnostic_current_command, index)

    def diagnostic_actuator_arduino_command(self, Channel_Numb, index = 0):
        actuator_diagnostic_command = "dActuator " + str(Channel_Numb)
        data = self.write_read(actuator_diagnostic_command, index)

        if(self.verbose):
            print(actuator_diagnostic_command)
            print(data)

        # turn data int variables
        numbers = data.split()
        float_numb = [float(num) for num in numbers]
        left = min(len(float_numb), self.diagnostics_vals.shape[1])

        with self.diagnostic_lock[index]:
            self.diagnostics_vals[Channel_Numb-1, :left] = float_numb[:left]

    def start_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb, index = 0):
        start_actuator_feedback_command = "sActuatrFeeback " + str(Channel_Numb)

        if(self.verbose):
            print(start_actuator_feedback_command)
            print(self.write_read(start_actuator_feedback_command, index))
        else:
            self.write_read(start_actuator_feedback_command, index)

    def diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb, index = 0):
        actuator_feedback_command = "dActuatrFeeback " + str(Channel_Numb)
        data = self.write_read(actuator_feedback_command, index)

        if(self.verbose):
            print(actuator_feedback_command)
            print(data)

        # turn data int variables
        numbers = data.split()
        float_numb = [float(num) for num in numbers]

        with self.diagnostic_lock[index]:
            self.diagnostics_vals[Channel_Numb-1, 4] = float_numb[0]

    def select_controls(self, index = 0):
        # print(self.controls_channel, )
        if(self.act_OR_motor[self.controls_channel[index]-1] == 0 or self.act_OR_motor[self.controls_channel[index]-1] == 2): # motor or slewgear
            self.control_motor_arduino_command(self.controls_channel[index], self.controls_vals[self.controls_channel[index]-1][0], self.controls_vals[self.controls_channel[index]-1][1], self.controls_vals[self.controls_channel[index]-1][2], self.controls_vals[self.controls_channel[index]-1][3], self.controls_vals[self.controls_channel[index]-1][4], index)
        elif(self.act_OR_motor[self.controls_channel[index]-1] == 1): # actuator
            self.control_actuator_arduino_command(self.controls_channel[index], self.controls_vals[self.controls_channel[index]-1][0], self.controls_vals[self.controls_channel[index]-1][2], self.controls_vals[self.controls_channel[index]-1][3], index)
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
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel[index]-1] == 3): # motherboard
            if(self.diagnostic_select[self.diagnostics_channel[index]-1] == 0):
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 1):
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 2):
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 3    
            elif(self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                self.diagnostic_select[self.diagnostics_channel[index]-1] = 0
                
        # end of debug timing
        if(self.timing):
            if(self.diagnostics_channel[index] == self.diagnostics_channel_total[index] and self.diagnostic_select[self.diagnostics_channel[index]-1] == 3):
                print(self.diagnostics_channel[index], self.diagnostic_select[self.diagnostics_channel[index]-1])
                print("Time of ", threading.current_thread().name, " is ", time.time() - self.start[index])

    def start_diagnostic_AND_controls(self, index = 0):
        # only worry about 8 channels
        while True:
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

    def index_0_thread(self):
        self.start_diagnostic_AND_controls(index = 0)

    def index_1_thread(self):
        self.start_diagnostic_AND_controls(index = 1)

    def start_diagnostics_AND_controls_thread(self, index):
        if(index == 0):
            self.d_and_c = threading.Thread(target=self.index_0_thread, name="Arduino Mega Thread")
            self.d_and_c.daemon = True
            self.d_and_c.start()
        else:
            self.d_and_c1 = threading.Thread(target=self.index_1_thread, name="LattePanda Thread")
            self.d_and_c1.daemon = True
            self.d_and_c1.start()

    def print_diagnostics(self):
        print(self.diagnostics_vals)

    # def control_motor_OR_actutor(self):
        # def control_motor_arduino_command(self, Channel_Numb, EN, EN_EFUSE, PWM, FR, BRAKE, index):
        # def control_actuator_arduino_command(self, Channel_Numb, EN_EFUSE, PWM, FR, index = 0):

        # Both - channel number, EN_EFUSE, PWM, FR
        # motor - EN motor, break
