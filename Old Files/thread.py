import cv2
import time
import threading
from cv2 import aruco
import numpy as np
import os
import sys
import queue  # Import the queue module

marker = True

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

# Number of threads for marker detection
num_threads = 4

# Create a thread pool
thread_pool = []

# Create a queue for sharing frames
frame_queue = queue.Queue()

def detect_markers_thread(frame, marker_dict, param_markers, cam_mat, dist_coeff):
    # Convert the image to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if marker:

        # Get the corners of the Aruco tags
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, marker_dict, parameters=param_markers)

        # Initialize variables to keep track of the closest Aruco tag
        closest_distance = float('inf')
        closest_x = 0
        closest_y = 0
        closest_z = 0
        closest_move = False
        closest_ids = None

        # If there are markers
        if marker_corners:
            # Get the pose of the markers (rotational and translational)
            rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, 9, cam_mat, dist_coeff)
            
            # Iterate through the markers
            for i, (ids, corners) in enumerate(zip(marker_IDs, marker_corners)):
                # Calculate the distance from the camera to the Aruco tag
                distance = np.sqrt(tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2)
                
                # If this tag is closer than the previous closest one, update the variables
                if distance < closest_distance:
                    closest_distance = distance
                    closest_x = round(tVec[i][0][0], 1)
                    closest_y = round(tVec[i][0][1], 1)
                    closest_z = round(tVec[i][0][2], 1)
                    closest_move = True  # Tell the rover to move
                    closest_ids = ids[0]
                
                # Make lines around the Aruco tag
                cv2.polylines(frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA)

                # Get the corners individually
                corners = corners.reshape(4, 2)
                corners = corners.astype(int)
                top_right = corners[0].ravel()
                top_left = corners[1].ravel()
                bottom_right = corners[2].ravel()
                bottom_left = corners[3].ravel()

                # Draw the pose of the marker with the x, y, z lines
                cv2.drawFrameAxes(frame, cam_mat, dist_coeff, rVec[i], tVec[i], 9)

                # Draw the distance vector at the top right
                cv2.putText(
                    frame,
                    f"id: {ids[0]} Dist: {round(distance, 2)}",
                    (top_right[0], top_right[1]),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.3,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

                # Draw the x, y, z at the bottom right
                cv2.putText(
                    frame,
                    f"x: {round(tVec[i][0][0], 1)} y: {round(tVec[i][0][1], 1)} z: {round(tVec[i][0][2], 1)}",
                    (bottom_right[0], bottom_right[1]),
                    cv2.FONT_HERSHEY_PLAIN,
                    1.0,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            frame_queue.put(frame)

def load_cal():
    calib_data = np.load(calib_data_path + "/" + "MultiMatrix4k.npz") # zip file of the caibration data
    # distance and matrix vectors
    cam_mat = calib_data["camMatrix"]
    dist_coef = calib_data["distCoef"]
    r_vectors = calib_data["rVector"]
    t_vectors = calib_data["tVector"]

    return cam_mat, dist_coef

def main():
    frame_count = 0
    marker_dict = aruco.Dictionary_get(cv2.aruco.DICT_7X7_100)
    param_markers = aruco.DetectorParameters_create()

    # Open a video capture object using the best backend available
    cap = cv2.VideoCapture("http://192.168.137.118:8080/video")  # Use 0 for the default camera

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    # Set the frame resolution and frame rate
    width = 3480
    height = 2160
    frame_rate = 30
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, frame_rate)
    actual_frame_rate = cap.get(cv2.CAP_PROP_FPS)

    start_time = time.time()
    smoothed_frame_rate = 0

    cam_mat, dist_coeff = load_cal()

    while True:
        # Read a frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read a frame.")
            break

        # Ensure there are no more threads than needed
        while len(thread_pool) >= num_threads:
            for thread in thread_pool:
                if not thread.is_alive():
                    thread_pool.remove(thread)
                    break

        # Create a thread to detect markers in the frame
        marker_thread = threading.Thread(target=detect_markers_thread, args=(frame, marker_dict, param_markers, cam_mat, dist_coeff))
        thread_pool.append(marker_thread)
        marker_thread.start()

        # Frame rate calculation
        current_time = time.time()
        frame_count += 1
        elapsed_time = current_time - start_time

        if elapsed_time >= 1.0:
            smoothed_frame_rate = frame_count / elapsed_time
            frame_count = 0
            start_time = current_time

        # Check if there is a frame with markers in the queue
        if not frame_queue.empty():
            # Get the frame from the queue
            frame_with_markers = frame_queue.get()
        else:
            frame_with_markers = frame  # Use the original captured frame

        # Display the frame
        display_frame = cv2.resize(frame_with_markers, (640, 480))
        cv2.putText(display_frame, f"Frame Rate: {smoothed_frame_rate:.2f} FPS (Actual: {actual_frame_rate:.2f} FPS)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('Video', display_frame)

        # Exit the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
