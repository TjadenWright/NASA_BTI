from tkinter import *

class ChannelSelector:
    def __init__(self, master):
        self.master = master
        self.master.title("Channel Selector")
        self.master.configure(bg="#0033A0")

        self.channel_options = ["Motor", "BIG Motor", "Actuator", "IMU"]

        self.done = False

    def create_widgets(self):
        for i in range(1, 17):
            frame = Frame(self.master, borderwidth=2, relief="groove", width=300, height=300)
            frame.grid(row=(i-1)//4, column=(i-1)%4, padx=10, pady=10)


            label = Label(frame, text="Channel {}".format(i), width=10, height=4)
            label.grid(row=0, column=0)

            option_menu = OptionMenu(frame, StringVar(), *self.channel_options)
            option_menu.grid(row=0, column=1)
            option_menu.config(width=10, height=3, bg="#FFD100")

        self.Save = Button(self.master, text="Save Config")
        self.Save.grid(row=4, columnspan=1, pady=10)
        self.Save.config(width=15, height=2, bg="#FFD100")

        self.LOAD = Button(self.master, text="Load Config", command=self.select_channels)
        self.LOAD.grid(row=4, columnspan=4, pady=10)
        self.LOAD.config(width=15, height=2, bg="#FFD100")

        self.LOAD_Save = Button(self.master, text="Load Config From Save", command=self.select_channels)
        self.LOAD_Save.grid(row=4, column=3, pady=10)
        self.LOAD_Save.config(width=20, height=2, bg="#FFD100")

    def select_channels(self):
        self.done = True
        for i in range(1, 17):
            selected_option = self.master.grid_slaves(row=(i-1)//4, column=(i-1)%4)[0].winfo_children()[1].cget("text")
            print("Channel {}: Selected Option - {}".format(i, selected_option))

    def run(self):
        self.create_widgets()
        while not self.done:
            self.master.update()
        self.master.destroy()

def main():
    root = Tk()
    c1 = ChannelSelector(root)
    c1.run()

if __name__ == "__main__":
    main()
