# import tkinter as tk
# from tkinter import ttk

# def handle_selection(event):
#     selected_item = dropdown.get()
#     print("Selected:", selected_item)

# root = tk.Tk()
# root.title("Dropdown Menu Example")

# # Create a list of options
# options = ["Option 1", "Option 2", "Option 3", "Option 4"]

# # Create a dropdown widget
# dropdown = ttk.Combobox(root, values=options)
# dropdown.pack(pady=20)
# dropdown.bind("<<ComboboxSelected>>", handle_selection)

# root.mainloop()

import tkinter as tk
from tkinter import ttk

def handle_selection(event):
    selected_item = dropdown.get()
    print("Selected:", selected_item)

root = tk.Tk()
root.title("Dropdown Menu Example")

# Create a list of options
options = ["Option 1", "Option 2", "Option 3", "Option 4"]

# Create and pack the first dropdown widget
dropdown1 = ttk.Combobox(root, values=options, state="readonly")
dropdown1.pack(pady=10)
dropdown1.bind("<<ComboboxSelected>>", handle_selection)

# Create and pack the second dropdown widget
dropdown2 = ttk.Combobox(root, values=options, state="readonly")
dropdown2.pack(pady=10)
dropdown2.bind("<<ComboboxSelected>>", handle_selection)

# Create and pack the third dropdown widget
dropdown3 = ttk.Combobox(root, values=options, state="readonly")
dropdown3.pack(pady=10)
dropdown3.bind("<<ComboboxSelected>>", handle_selection)

root.mainloop()