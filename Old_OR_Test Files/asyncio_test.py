import threading
import time

print_lock = threading.Lock()

# Function to be executed after a certain delay
def delayed_function(delay):
    time.sleep(delay)
    with print_lock:
        print("Delayed function executed.")

# Function that runs immediately
def immediate_function():
    with print_lock:
        print("Immediate function executed.")

# Run immediate_function immediately
immediate_function()

# Run delayed_function after 5 seconds
thread = threading.Thread(target=delayed_function, args=(5,))
thread.start()

while True:
    # Continue with other operations
    immediate_function()
    time.sleep(0.1)