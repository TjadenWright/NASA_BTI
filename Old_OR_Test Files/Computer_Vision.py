import numpy as np
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(grey_frame, maxCorners=1000,
                                      qualityLevel=0.1, minDistance=50)

    corners = np.int0(corners)

    for c in corners:
        x, y = c.ravel()
        frame = cv2.circle(frame, center=(x,y), radius=5,
                           color=(0,0,255), thickness=-1)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()