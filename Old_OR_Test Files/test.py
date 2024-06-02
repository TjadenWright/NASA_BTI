from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
index = 0
data = "cMotor " + str(3) + " " + str(1) + " " + str(0) + " " + str(232) + " " + str(1) + " " + str(0)
data_get = "3 1 0 232 1 0"

with open("leonardo_log.txt", "a") as error_file:
    error_file.write(current_time + str(index) + ": " + data + ": -> " + data_get + "\n")