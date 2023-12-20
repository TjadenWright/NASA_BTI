import cv2
import numpy as np
import time

# Initialize the video capture (replace '0' with your camera index)
cap = cv2.VideoCapture("rtsp://172.168.100.39:8080/h264.sdp")
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

while True:
    start = time.time()

    # Capture a frame from the camera
    ret, frame = cap.read()

    end = time.time()
    elapsed_time = end - start

    # Check if the elapsed time is not zero to avoid divide-by-zero error
    if elapsed_time > 0:
        fps = 1 / elapsed_time
    else:
        fps = 0

    print(f"FPS: {fps:.2f}")

    # Display the frame
    display_frame = cv2.resize(frame, (640, 480))
    cv2.imshow("ArUco Detection", display_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
