import cv2
import urllib.request
import numpy as np

class Amcrest_Camera:
    def VideoCapture(self, ip = ""):

        # def convert_ip_to_base_user_pass(ip):
                
        url = 'http://192.168.1.49/cgi-bin/mjpg/video.cgi?channel=0&subtype=1'

        auth_user="nasabtic"
        auth_passwd="nasabs123"

        self.passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        self.passman.add_password(None, url, auth_user, auth_passwd)
        self.authhandler = urllib.request.HTTPDigestAuthHandler(self.passman)

        self.opener = urllib.request.build_opener(self.authhandler)
        urllib.request.install_opener(self.opener)

        self.stream = urllib.request.urlopen(url)
        self.bytes = b''
        
    def read(self):
        self.bytes += self.stream.read(1024)
        a = self.bytes.find(b'\xff\xd8') #frame starting 
        b = self.bytes.find(b'\xff\xd9') #frame ending
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            return True, img
        return False, None
            