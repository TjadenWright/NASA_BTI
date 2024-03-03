import serial
import time
import threading
import numpy as np

# Commands
# startup LOW_HIGH
# cMotor Channel# EN EN_EFUSE PWM FR BREAK 
# cActuator Channel# EN_EFUSE FR PWM
# sMotorCurrent Channel#                (starts the current conversion)
# dMotor Channel#                       you get this: ALARM TEMP CURRENT OC_FAULT
# sMotrSpeed Channel#                   (starts the speed conversion)
# dMotrSpeed Channel#                   you get this: SPEED
# sActuatorCurrent Channel#             (starts the current conversion)
# dActuator Channel#                    you get this: TEMP CURRENT OC_FAULT
# sActuatrFeeback Channel#              (starts the feedback conversion)
# dActuatrFeeback Channel# FEEBACK      you get this: FEEDBACK

class Controls_Diagnostics:
    def __init__(self, buadrate=2000000, verbose=False):
        self.baudrate = buadrate
        self.verbose = verbose

        # make a list of things that need to happen
        self.act_OR_motor = np.zeros(16) # 0 is a motor, 1 is an actuator, 2 is slew gear, 3 is motherboard

        # setup channels
        self.diagnostics_channel = 1
        self.controls_channel = self.diagnostics_channel

        self.diagnostics_channel_total = 8
        self.controls_channel_total = self.diagnostics_channel_total
        
        self.diagnostics_channel_reset = 1
        self.controls_channel_reset = self.diagnostics_channel_reset

        # controls
        self.controls = np.zeros((16, 10), int)

        # diagnostics
        self.diagnostics = np.zeros((16, 10))
        self.diagnostic_select = np.zeros(16)

    def connect_to_arduino(self):
        # Initializing Arduino Serial Connection
        self.arduino = serial.Serial(port='COM5', baudrate=2000000)
        time.sleep(2) # wait for connection to complete

    def write_read(self, x):
        self.arduino.write(bytes(x + "\n", 'utf-8'))
        
        # Read from the serial port until data is received
        data = self.arduino.readline().decode('utf-8').strip()
        return data

    def set_act_OR_motor(self, config=np.zeros(15)):
        self.act_OR_motor = config

    def start_arduino_command(self, HIGH_LOW):
        start_command = "startup " + str(HIGH_LOW)
        if(self.verbose):
            print(start_command)
            print(self.write_read(start_command))
        else:
            self.write_read(start_command)

        if(HIGH_LOW == 1):
            self.diagnostics_channel = 9
            self.controls_channel = self.diagnostics_channel

            self.diagnostics_channel_total = 16
            self.controls_channel_total = self.diagnostics_channel_total
            
            self.diagnostics_channel_reset = 9
            self.controls_channel_reset = self.diagnostics_channel_reset

        else:
            self.diagnostics_channel = 1
            self.controls_channel = self.diagnostics_channel

            self.diagnostics_channel_total = 8
            self.controls_channel_total = self.diagnostics_channel_total
            
            self.diagnostics_channel_reset = 1
            self.controls_channel_reset = self.diagnostics_channel_reset

    def control_motor_arduino_command(self, Channel_Numb, EN, EN_EFUSE, PWM, FR, BRAKE):
        motor_control_command = "cMotor " + str(Channel_Numb) + " " + str(EN) + " " + str(EN_EFUSE) + " " + str(PWM) + " " + str(FR) + " " + str(BRAKE)

        if(self.verbose):
            print(motor_control_command)
            print(self.write_read(motor_control_command))
        else:
            self.write_read(motor_control_command)
        
    def control_actuator_arduino_command(self, Channel_Numb, EN_EFUSE, PWM, FR):
        actuator_control_command = "cActuator " + str(Channel_Numb) + " " + str(EN_EFUSE) + " " + str(FR) + " " + str(PWM)

        if(self.verbose):
            print(actuator_control_command)
            print(self.write_read(actuator_control_command))
        else:
            self.write_read(actuator_control_command)

    def start_motor_current_arduino_command(self, Channel_Numb):
        motor_start_current_command = "sMotorCurrent " + str(Channel_Numb)

        if(self.verbose):
            print(motor_start_current_command)
            print(self.write_read(motor_start_current_command))
        else:
            self.write_read(motor_start_current_command)

    def diagnostic_motor_arduino_command(self, Channel_Numb):
        motor_diagnostic_command = "dMotor " + str(Channel_Numb)

        if(self.verbose):
            print(motor_diagnostic_command)
            print(self.write_read(motor_diagnostic_command))
        else:
            self.write_read(motor_diagnostic_command)

    def start_motor_speed_arduino_command(self, Channel_Numb):
        start_motor_diagnostic_speed_command = "sMotrSpeed " + str(Channel_Numb)

        if(self.verbose):
            print(start_motor_diagnostic_speed_command)
            print(self.write_read(start_motor_diagnostic_speed_command))
        else:
            self.write_read(start_motor_diagnostic_speed_command)

    def diagnostic_motor_speed_arduino_command(self, Channel_Numb):
        motor_diagnostic_speed_command = "dMotrSpeed " + str(Channel_Numb)

        if(self.verbose):
            print(motor_diagnostic_speed_command)
            print(self.write_read(motor_diagnostic_speed_command))
        else:
            self.write_read(motor_diagnostic_speed_command)

    def start_actuator_current_arduino_command(self, Channel_Numb):
        start_actuator_diagnostic_current_command = "sActuatorCurrent " + str(Channel_Numb)

        if(self.verbose):
            print(start_actuator_diagnostic_current_command)
            print(self.write_read(start_actuator_diagnostic_current_command))
        else:
            self.write_read(start_actuator_diagnostic_current_command)

    def diagnostic_actuator_arduino_command(self, Channel_Numb):
        actuator_diagnostic_command = "dActuator " + str(Channel_Numb)

        if(self.verbose):
            print(actuator_diagnostic_command)
            print(self.write_read(actuator_diagnostic_command))
        else:
            self.write_read(actuator_diagnostic_command)

    def start_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb):
        start_actuator_feedback_command = "sActuatrFeeback " + str(Channel_Numb)

        if(self.verbose):
            print(start_actuator_feedback_command)
            print(self.write_read(start_actuator_feedback_command))
        else:
            self.write_read(start_actuator_feedback_command)

    def diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self, Channel_Numb):
        actuator_feedback_command = "dActuatrFeeback " + str(Channel_Numb)

        if(self.verbose):
            print(actuator_feedback_command)
            print(self.write_read(actuator_feedback_command))
        else:
            self.write_read(actuator_feedback_command)

    def select_controls(self):
        # print(self.controls_channel, )
        if(self.act_OR_motor[self.controls_channel-1] == 0 or self.act_OR_motor[self.controls_channel-1] == 2): # motor or slewgear
            self.control_motor_arduino_command(self.controls_channel, self.controls[self.controls_channel-1][0], self.controls[self.controls_channel-1][1], self.controls[self.controls_channel-1][2], self.controls[self.controls_channel-1][3], self.controls[self.controls_channel-1][4])
        elif(self.act_OR_motor[self.controls_channel-1] == 1): # actuator
            self.control_actuator_arduino_command(self.controls_channel, self.controls[self.controls_channel-1][0], self.controls[self.controls_channel-1][2], self.controls[self.controls_channel-1][3])
        # elif(self.act_OR_motor[self.controls_channel-1] == 3): # motherboard
            
    def select_diagnostic(self):
        if(self.diagnostics_channel == 1 and (self.controls_channel == 1 or self.controls_channel == 5)):
            self.start = time.time()
            print("------------ start ------------")
        if(self.diagnostics_channel == 8 and (self.controls_channel == 1 or self.controls_channel == 5)):
            print("------------ end ------------")
            print("Time: ", time.time()-self.start)

        if(self.act_OR_motor[self.diagnostics_channel-1] == 0): # motor
            if(self.diagnostic_select[self.diagnostics_channel-1] == 0):
                self.start_motor_current_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 1):
                self.diagnostic_motor_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 2):
                self.start_motor_speed_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 3):
                self.diagnostic_motor_speed_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel-1] == 1): # actuator
            if(self.diagnostic_select[self.diagnostics_channel-1] == 0):
                self.start_actuator_current_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 1):
                self.diagnostic_actuator_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 2):
                self.start_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 3):
                self.diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 0

        elif(self.act_OR_motor[self.diagnostics_channel-1] == 2): # slewgear
            if(self.diagnostic_select[self.diagnostics_channel-1] == 0):
                self.start_motor_current_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 1
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 1):
                self.diagnostic_motor_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 2
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 2):
                self.start_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 3
            elif(self.diagnostic_select[self.diagnostics_channel-1] == 3):
                self.diagnostic_actuator_SLEWGEAR_feedback_arduino_command(self.diagnostics_channel)
                self.diagnostic_select[self.diagnostics_channel-1] = 0

        # elif(self.act_OR_motor[self.diagnostics_channel-1] == 3): # motherboard

    def start_diagnostic_AND_controls(self):
        # only worry about 8 channels
        while True:
            self.select_diagnostic()
            self.diagnostics_channel = self.diagnostics_channel + 1
            if(self.diagnostics_channel >= self.diagnostics_channel_total + 1):
                self.diagnostics_channel = self.diagnostics_channel_reset
            self.select_controls()
            self.controls_channel = self.controls_channel + 1
            self.select_controls()
            self.controls_channel = self.controls_channel + 1
            self.select_controls()
            self.controls_channel = self.controls_channel + 1
            self.select_controls()
            self.controls_channel = self.controls_channel + 1
            if(self.controls_channel >= self.controls_channel_total):
                self.controls_channel = self.controls_channel_reset

    def start_diagnostics_AND_controls_thread(self):
        self.d_and_c = threading.Thread(target=self.start_diagnostic_AND_controls)
        self.d_and_c.daemon = True
        self.d_and_c.start()

            
        
cd = Controls_Diagnostics(verbose=True)
cd.connect_to_arduino()
cd.start_arduino_command(0)
# cd.start_diagnostic_AND_controls()

cd.start_diagnostics_AND_controls_thread()

while True:
    print("hello")
    time.sleep(0.01)

    # # Main thread continues to run the Arduino communication
    # def majik_merigoround(i):
    #     motor_control_command = "cMotor " + str(i) + " 1 1 234 1 0"
    #     print(motor_control_command)
    #     print(write_read(motor_control_command))

    #     # act_control_command = "cActuator 2 1 1 234"
    #     # print(act_control_command)
    #     # print(write_read(act_control_command))

    #     motor_current_start = "sMotorCurrent " + str(i)
    #     print(motor_current_start)
    #     print(write_read(motor_current_start))

    # # Your main loop for other tasks related to Arduino communication
    # start = time.time()

    # start_command = "startup"
    # print(start_command)
    # print(write_read(start_command))

    # majik_merigoround(8)
    # majik_merigoround(1)
    # majik_merigoround(2)
    # majik_merigoround(3)
    # majik_merigoround(4)
    # majik_merigoround(5)
    # majik_merigoround(6)
    # majik_merigoround(7)

    # print("total time: ", time.time() - start)

    # time.sleep(0.05)

    # motor_current_get = "dMotor 8"
    # print(motor_current_get)
    # print(write_read(motor_current_get))

    # start = time.time()
    # motor_control_command = "cMotor 2 1 1 234 1 0"
    # print(motor_control_command)
    # print(write_read(motor_control_command))

    # motor_control_command = "cMotor 3 1 1 234 1 0"
    # print(motor_control_command)
    # print(write_read(motor_control_command))

    # motor_control_command = "cMotor 4 1 1 234 1 0"
    # print(motor_control_command)
    # print(write_read(motor_control_command))

    # motor_control_command = "cMotor 5 1 1 234 1 0"
    # print(motor_control_command)
    # print(write_read(motor_control_command))

    # motor_current_start = "sMotorCurrent 1"
    # print(motor_current_start)
    # print(write_read(motor_current_start))

    # print(time.time()-start)

# motor_speed_start = "sMotrSpeed 3"
# print(motor_speed_start)
# print(write_read(motor_speed_start))

# motor_speed_get = "dMotrSpeed 3"
# print(motor_speed_get)
# print(write_read(motor_speed_get))

# act_current_start = "sActuatorCurrent 2"
# print(act_current_start)
# print(write_read(act_current_start))

# act_current_get = "dActuator 2"
# print(act_current_get)
# print(write_read(act_current_get))

# act_feedback_start = "sActuatrFeeback 2"
# print(act_feedback_start)
# print(write_read(act_feedback_start))

# act_feedback_get = "dActuatrFeeback 2"
# print(act_feedback_get)
# print(write_read(act_feedback_get))
