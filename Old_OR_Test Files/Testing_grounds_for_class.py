from Controls_Class import Rover_Controls
import time

rc1 = Rover_Controls(verbose=False)

rc1.Enable_Write_arduino(baud_rate = 115200)

while not rc1.Stop_Manual_Control():        # keep getting data till the manual control button has been pressed (defaults to PS Home Button).
    rc1.Write_message(data=rc1.Motor_PWM()) # send PWM data to the arduino
    print(rc1.Motor_PWM())

rc1.Disable_write_arduino()
