from Controls_Class import Rover_Controls

rc1 = Rover_Controls(verbose=False)

def run_controls():
    rc1.Enable_Write_arduino()

    while not rc1.Stop_Manual_Control():
        PWM_Motors = rc1.Motor_PWM()
        rc1.Write_message(data=PWM_Motors)

    rc1.Disable_write_arduino()

run_controls()
