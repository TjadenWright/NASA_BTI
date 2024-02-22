from tkinter import *
import threading

class ChannelSelector:
    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.title("Channel Selector")
        self.master.configure(bg="#0033A0")

        self.channel_options = ["Motor", "BIG Motor", "Actuator", "IMU"]

        self.done = False

    def on_closing(self):
        self.master.destroy()
        self.done = True
        print("by by")

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
        self.done = False
        self.create_widgets()

    def run_loop(self):
        if(not self.done):
            self.master.update()
        
    def done_help(self):
        return self.done
    
    def delete(self):
        self.master.destroy()

def main():
    root2 = Tk()
    c2 = ChannelSelector(root2)
    c2.run()
    # the idea is that you can run both of them in the same loop

    root = Toplevel()
    c1 = ChannelSelector(root)
    c1.run()

    while (not c1.done_help() or not c2.done_help()):
        c1.run_loop()
        c2.run_loop()
    c1.delete()
    c2.delete()


if __name__ == "__main__":
    main()
