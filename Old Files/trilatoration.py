import matplotlib.pyplot as plt
import numpy as np
from UWB_Class import UWB_Class
from scipy.optimize import minimize

def make_circles(anchor_add, anchor_x, anchor_y, distances, closest_point=None):
    """
    Plot circles with given radii and center points for multiple anchors.

    :param anchor_add: List of anchor labels or names.
    :param anchor_x: List of anchor x-coordinates.
    :param anchor_y: List of anchor y-coordinates.
    :param distances: List of radii for each anchor.
    :param closest_point: (x, y) coordinates of the closest point (optional).
    """
    # Convert input data to numpy arrays for easier manipulation
    anchor_x = np.array(anchor_x)
    anchor_y = np.array(anchor_y)
    distances = np.array(distances)

    # Create a figure and axis if it doesn't exist
    if not plt.fignum_exists(1):
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()
        ax = plt.gca()

    # Clear the current axis
    ax.clear()

    # Plot circles for each anchor
    for i, (x, y, label, radius) in enumerate(zip(anchor_x, anchor_y, anchor_add, distances)):
        circle = plt.Circle((x, y), radius, fill=False, label=f"Anchor {label} Radius")
        ax.add_artist(circle)

        # Plot the anchor point
        ax.scatter(x, y, label=f"Anchor {label}", marker='o', color='blue')

        # Add text annotations for anchor label and radius
        ax.text(x, y, f"{label}", fontsize=12, ha="left")

    # Plot the closest point if provided
    if closest_point is not None:
        x, y = closest_point
        ax.scatter(x, y, label="Closest Point", marker='x', color='red')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid()

    # Set equal scaling for x and y axes
    ax.set_aspect('equal', adjustable='box')

    # Calculate the limits for x and y axes
    x_min = -5 #min(anchor_x - distances)
    x_max = 5 #max(anchor_x + distances)
    y_min = -5 #min(anchor_y - distances)
    y_max = 5 #max(anchor_y + distances)

    # Set axis limits
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    plt.draw()
    plt.pause(13e-3)  # Adjust the pause duration as needed

def calculate_closest_point(anchor_x, anchor_y, distances):
    # Stack anchor coordinates and distances into arrays
    anchor_x = np.array(anchor_x)
    anchor_y = np.array(anchor_y)
    distances = np.array(distances)

    # Define a function that calculates the sum of squared errors between
    # the distances from a point (x, y) to the circle centers and the circle radii.
    def objective(point):
        x, y = point
        dx = x - anchor_x
        dy = y - anchor_y
        errors = np.sum((np.sqrt(dx**2 + dy**2) - distances)**2)
        return errors

    # Initial guess based on the average of anchor coordinates
    initial_guess = (np.mean(anchor_x), np.mean(anchor_y))

    # Use minimize to find the point that minimizes the objective function
    result = minimize(objective, initial_guess, method='Nelder-Mead', options={'xtol': 1e-5, 'ftol': 1e-5})

    if result.success:
        return result.x
    else:
        return None  # Optimization did not converge to a solution


plt.ion()

uwb1 = UWB_Class(option=1, speed=100)
arduinoData1 = uwb1.serial_communication()

anchor_add = np.array([1, 2, 3, 4])
anchor_x = np.array([0.0, 1.0, 1.0, 0.0])
anchor_y = np.array([0.0, 0.0, 1.0, 1.0])
distances = np.array([0.0, 0.0, 0.0, 0.0])
change_dist = np.array([0, 0, 0, 0])
prev_dist = np.array([0.0, 0.0, 0.0, 0.0])

update_fig_interval = 0
update_fig_interval_max = 10
distance_changes_max = 20

while True:
    add, dist = uwb1.read_arduino_2(arduinoData1)
    prev_dist = distances.copy()
    distances[add-1] = dist

    for i in range(len(anchor_add)):
        if(prev_dist[i] == distances[i]):
            change_dist[i] += 1 # add one each time
        else:
            change_dist[i] = 0 # reset back to zero

    #print("A1: ", distances[0], "A2: ", distances[1],
    #      "A3: ", distances[2], "A4: ", distances[3])
    
    condition = change_dist < distance_changes_max

    #print(condition)

    # Calculate the closest (x, y) point
    closest_point = calculate_closest_point(anchor_x[condition], anchor_y[condition], distances[condition])

    if(update_fig_interval == update_fig_interval_max):
        make_circles(anchor_add, anchor_x, anchor_y, distances, closest_point)
        update_fig_interval = 0
    else:
        update_fig_interval+=1
    
    plt.ioff()
