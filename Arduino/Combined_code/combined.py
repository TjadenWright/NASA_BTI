import serial
import time
import threading

def write_read(x):
    arduino.write(bytes(x + "\n", 'utf-8'))
    
    # Read from the serial port until data is received
    data = arduino.readline().decode('utf-8').strip()
    return data

# Initializing Arduino Serial Connection
arduino = serial.Serial(port='COM5', baudrate=2000000)
time.sleep(2)

# Main thread continues to run the Arduino communication
def majik_merigoround():
    motor_control_command = "cMotor 3 1 1 234 1 0"
    print(motor_control_command)
    print(write_read(motor_control_command))

    # act_control_command = "cActuator 2 1 1 234"
    # print(act_control_command)
    # print(write_read(act_control_command))

    motor_current_start = "sMotorCurrent 3"
    print(motor_current_start)
    print(write_read(motor_current_start))

# Your main loop for other tasks related to Arduino communication
start = time.time()

start_command = "startup"
print(start_command)
print(write_read(start_command))

majik_merigoround()
majik_merigoround()
majik_merigoround()
majik_merigoround()
majik_merigoround()
majik_merigoround()
majik_merigoround()
majik_merigoround()

print("total time: ", time.time() - start)

time.sleep(0.05)

motor_current_get = "dMotor 3"
print(motor_current_get)
print(write_read(motor_current_get))

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
