    # import cv2

    # # Set up VideoCapture with boundary marker
    # cap = cv2.VideoCapture("rtsp://admin:admin@192.168.1.49/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46YWRtaW4=")

    # while cap.isOpened():
    #     # Read a frame from the stream
    #     ret, img = cap.read()

    #     if ret:
    #         img = cv2.resize(img, (640, 480))
    #         cv2.imshow('Video Stream Monitor', img)

    #         if cv2.waitKey(1) & 0xFF == ord('q'):
    #             break

    # cap.release()
    # cv2.destroyAllWindows()


# import cv2
# import urllib.request
# import numpy as np

# url = 'http://192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1'

# auth_user="nasabtic"
# auth_passwd="nasabs123"

# passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
# passman.add_password(None, url, auth_user, auth_passwd)
# authhandler = urllib.request.HTTPDigestAuthHandler(passman)

# opener = urllib.request.build_opener(authhandler)
# urllib.request.install_opener(opener)

# stream = urllib.request.urlopen(url)
# bytes = b''
# while True:
#     bytes += stream.read(1024)
#     a = bytes.find(b'\xff\xd8') #frame starting 
#     b = bytes.find(b'\xff\xd9') #frame ending
#     if a != -1 and b != -1:
#         jpg = bytes[a:b+2]
#         bytes = bytes[b+2:]
#         img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
#         img = cv2.resize(img, (1280, 720))
#         cv2.imshow('image', img)
#         if cv2.waitKey(1) == 27:
#             cv2.destroyAllWindows()
#             break

