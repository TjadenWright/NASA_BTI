# import cv2

# # Set up VideoCapture with boundary marker
# cap = cv2.VideoCapture("http://admin:admin@192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1&authbasic=YWRtaW46YWRtaW4=")
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_FPS, 30)

# while cap.isOpened():
#     # Read a frame from the stream
#     ret, img = cap.read()

#     if ret:
#         cv2.imshow('Video Stream Monitor', img)
#     else:
#         print("bad feed")
#         break

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()


import cv2
import urllib.request
import numpy as np

url = 'http://192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1'

auth_user="nasabtic"
auth_passwd="nasabs123"

passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, url, auth_user, auth_passwd)
authhandler = urllib.request.HTTPDigestAuthHandler(passman)

opener = urllib.request.build_opener(authhandler)
urllib.request.install_opener(opener)

stream = urllib.request.urlopen(url)
bytes = b''
while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8') #frame starting 
    b = bytes.find(b'\xff\xd9') #frame ending
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        img = cv2.resize(img, (1280, 720))
        cv2.imshow('image', img)
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            break


# import requests

# url = 'http://192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1'
# response = requests.get(url)

# if response.status_code == 401:
#     authenticate_header = response.headers.get('WWW-Authenticate')
#     if authenticate_header:
#         # Example parsing to extract the realm parameter
#         realm_start = authenticate_header.find('realm="') + len('realm="')
#         realm_end = authenticate_header.find('"', realm_start)
#         realm = authenticate_header[realm_start:realm_end]
#         print("Realm:", realm)
#     else:
#         print("No WWW-Authenticate header found in the response.")
# else:
#     print("Request was successful without authentication.")