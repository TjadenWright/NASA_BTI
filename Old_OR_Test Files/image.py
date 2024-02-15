import matplotlib.pyplot as plt
import numpy as np

def make_circles(anchor_x, anchor_y, anchor_add, distances, closest_point, circles = True):
        """
        Plot circles with given radii and center points for multiple anchors.

        :param anchor_add: List of anchor labels or names.
        :param anchor_x: List of anchor x-coordinates.
        :param anchor_y: List of anchor y-coordinates.
        :param distances: List of radii for each anchor.
        :param closest_point: (x, y) coordinates of the closest point (optional).
        """

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
            if(circles == True):
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

        ax.set_xlabel("X Distance (m)")
        ax.set_ylabel("Y Distance (m)")
        ax.set_title("Positioning of Anchors to Tag with Trilateration")
        ax.grid()

        # Set equal scaling for x and y axes
        ax.set_aspect('equal', adjustable='box')

        # Calculate the limits for x and y axes
        x_min = -100 #min(anchor_x - distances)
        x_max = 160 #max(anchor_x + distances)
        y_min = -100 #min(anchor_y - distances)
        y_max = 160 #max(anchor_y + distances)

        # Set axis limits
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        plt.show()
        #plt.pause(1e-3)  # Adjust the pause duration as needed

make_circles(anchor_x = np.array([0, 73, 0]), anchor_y = np.array([70, 0, 0]), anchor_add=np.array(['A1', 'A2', 'A4']), 
             distances=np.array([67,66,100.4]), closest_point = np.array([68, 67]))