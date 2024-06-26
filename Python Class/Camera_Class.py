import cv2
import urllib.request
from urllib.parse import urlparse
import numpy as np

class Amcrest_Camera:
    def VideoCapture(self, ip = "http://nasabtic:nasabs123@192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1", timeout = 0.5):

        def convert_ip_to_base_user_pass(ip):

            parsed_url = urlparse(ip)

            username = parsed_url.username
            password = parsed_url.password

            # Remove the username and password from the netloc
            netloc_without_auth = parsed_url.netloc.replace(f"{username}:{password}@", "", 1)

            # print("This is Camera: ")
            # print("Username:", username)
            # print("Password:", password)
            # print("Remaining URL:", parsed_url._replace(netloc=netloc_without_auth).geturl())

            return username, password, parsed_url._replace(netloc=netloc_without_auth).geturl()

        self.first_four_letters = ip[:4]

        # Check if it matches "rtsp" or "http"
        if self.first_four_letters == "rtsp":
            self.stream = cv2.VideoCapture(ip)
            return True
        elif self.first_four_letters == "http":
            try:
                # convert to auth password and stuff
                auth_user, auth_passwd, url = convert_ip_to_base_user_pass(ip)

                # send in username and pasword (digest)
                self.passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                self.passman.add_password(None, url, auth_user, auth_passwd)
                self.authhandler = urllib.request.HTTPDigestAuthHandler(self.passman)

                self.opener = urllib.request.build_opener(self.authhandler)
                urllib.request.install_opener(self.opener)

                # start video
                self.stream = urllib.request.urlopen(url, timeout=timeout)
                self.bytes = b''
                return True  # Connection successful
            except Exception as e:
                print(f"Failed to connect: {e}")
                self.stream = None
                return False  # Connection failed
        
    def read(self):
        if self.first_four_letters == "rtsp":
            ret, img = self.stream.read()
            return ret, img
        elif self.first_four_letters == "http":
            self.bytes += self.stream.read(1024)
            a = self.bytes.find(b'\xff\xd8') #frame starting 
            b = self.bytes.find(b'\xff\xd9') #frame ending
            if a != -1 and b != -1:
                jpg = self.bytes[a:b+2]
                self.bytes = self.bytes[b+2:]
                img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                return True, img
            return False, None
    
    def destroy(self):
        if self.first_four_letters == "rtsp":
            if self.stream:
                self.stream.release()
                self.stream = None
        elif self.first_four_letters == "http":
            if self.stream:
                self.stream.close()
                self.stream = None
            