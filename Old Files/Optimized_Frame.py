import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

# Initialize the video capture (replace '0' with your camera index)
cap = cv2.VideoCapture("rtsp://172.168.100.39:8080/h264.sdp")
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

def read_frame():
    ret, frame = cap.read()
    return frame

with ThreadPoolExecutor() as executor:
    while True:
        start = time.time()

        # Submit the read_frame function to the ThreadPoolExecutor
        future = executor.submit(read_frame)

        # Display the previous frame while waiting for the new frame
        if 'frame' in locals():
            display_frame = cv2.resize(frame, (640, 480))
            cv2.imshow("ArUco Detection", display_frame)

        # Wait for the reading to complete and get the frame
        frame = future.result()

        end = time.time()
        print(end - start)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
