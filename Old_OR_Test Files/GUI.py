import PySimpleGUI as sg

layout = [[sg.Text("Please Select Your Rover!")], [sg.Button("Excavator Rover")], [sg.Button("Dump Truck Rover")],
          [sg.Button("Battery Swapper Rover")], [sg.Button("Main Base Station")]]

# Create the window
window = sg.Window("1", layout)

# Create an event loop
while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "Excavator Rover" or event == sg.WIN_CLOSED:
        print("Excavator Rover")
        break
    elif event == "Dump Truck Rover" or event == sg.WIN_CLOSED:
        print("Dump Truck Rover")
        break
    elif event == "Battery Swapper Rover" or event == sg.WIN_CLOSED:
        print("Battery Swapper Rover")
        break
    elif event == "Main Base Station" or event == sg.WIN_CLOSED:
        print("Main Base Station")
        break

window.close()
