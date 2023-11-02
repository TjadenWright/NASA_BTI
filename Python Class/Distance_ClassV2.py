import cv2
from cv2 import aruco
import numpy as np
import time
import os

class aruco_detect:
    def __init__(self, calib_data_path = r"C:\Users\tj10c\Downloads\practice", MARKER_SIZE = 8, verbose = True, w = 1280, h = 720, fps_vid = 10, calib_file = "MultiMatrix.npz"):
        self.calib_data_path = calib_data_path  # camera calibration data path
        self.verbose = verbose                  # debugging purpose
        self.MARKER_SIZE = MARKER_SIZE          # how big is the marker?
        self.start_time = time.time()           # start time (for fps)
        self.frame_count = 0                    # frame count for fps start at zero
        self.fps = 0                            # fps
        self.w = w
        self.h = h
        self.fps_vid = fps_vid
        self.calib_file = calib_file

    # setup camera with its calibrated data
    def calibrated_cam_data(self, url_OR_cam_numb = "http://192.168.4.20:8080/video"):
        calib_data = np.load(self.calib_data_path + "/" + self.calib_file) # zip file of the caibration data
        # distance and matrix vectors
        self.cam_mat = calib_data["camMatrix"]
        self.dist_coef = calib_data["distCoef"]
        self.r_vectors = calib_data["rVector"]
        self.t_vectors = calib_data["tVector"]

        if(self.verbose == True):
            print("cam_mat: ", self.cam_mat)
            print("dist_coef: ", self.dist_coef)
            print("r_vectors: ", self.r_vectors)
            print("t_vectors: ", self.t_vectors)

        # get the camera feed
        self.cap = cv2.VideoCapture(url_OR_cam_numb) #give the server id shown in IP webcam App
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps_vid)
        self.actual_frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

    # setup the aruco marker dictionary
    def aruco_marker_dict(self, DICT_MXM_L = "DICT_4X4_100"):
        # dictionary of aruco tags
        ARUCO_DICT = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
            "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
            "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
            "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
        }

        self.marker_dict = aruco.Dictionary_get(ARUCO_DICT[DICT_MXM_L])
        self.param_markers = aruco.DetectorParameters_create()

    # get the tag data
    def aruco_tag(self, calc_aruco=True, pic_out=True, scale = 1):
        # Read from the camera
        _, frame = self.cap.read()
        
        # Initialize variables to keep track of the closest Aruco tag
        closest_distance = float('inf')
        closest_x = 0
        closest_y = 0
        closest_z = 0
        closest_move = False
        closest_ids = None
        
        # If you want to look for Aruco tags
        if calc_aruco:
            # Convert the image to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Get the corners of the Aruco tags
            marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, self.marker_dict, parameters=self.param_markers)
            
            # If there are markers
            if marker_corners:
                # Get the pose of the markers (rotational and translational)
                rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, self.MARKER_SIZE, self.cam_mat, self.dist_coef)
                
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
                    cv2.drawFrameAxes(frame, self.cam_mat, self.dist_coef, rVec[i], tVec[i], self.MARKER_SIZE)

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

        # Calculate FPS
        self.frame_count += 1
        if self.frame_count >= 10:
            elapsed_time = time.time() - self.start_time
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
        
        # Print the FPS on the screen
        cv2.putText(frame, f"Frame Rate: {self.fps:.2f} FPS (Actual: {self.actual_frame_rate:.2f} FPS)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show an image if pic_out is True
        if pic_out:
            resized_frame = cv2.resize(frame, None, fx=scale, fy=scale)
            cv2.imshow("frame", resized_frame)
        else:
            print("fps: ", int(self.fps))
        
        # Return the closest Aruco tag's information
        return closest_x, closest_y, closest_z, closest_move, closest_ids

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def wait_key(self):
        key = cv2.waitKey(1)
        if key == ord("q"):
            return True
        else:
            return False

    def detect_checker_board(self, image, grayImage, criteria, boardDimension):
        ret, corners = cv2.findChessboardCorners(grayImage, boardDimension)
        if ret == True:
            corners1 = cv2.cornerSubPix(grayImage, corners, (3, 3), (-1, -1), criteria)
            image = cv2.drawChessboardCorners(image, boardDimension, corners1, ret)

        return image, ret

    def take_picks(self, Chess_Board_Dimensions = (9, 6), images_folder = "images", url_OR_cam_numb = "http://192.168.4.20:8080/video"):
        n = 0
        img_path = self.calib_data_path + "/" + images_folder
        Dir_Check = os.path.isdir(img_path)

        if not Dir_Check:  # if directory does not exist, a new one is created
            os.makedirs(img_path)
            print(f'"{img_path}" Directory is created')
        else:
            print(f'"{img_path}" Directory already exists.')
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        cap = cv2.VideoCapture(url_OR_cam_numb)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        cap.set(cv2.CAP_PROP_FPS, self.fps_vid)

        while True:
            _, frame = cap.read()
            frame_cp = frame.copy()
          
            cv2.putText(
                frame,
                f"saved_img : {n}",
                (30, 40),
                cv2.FONT_HERSHEY_PLAIN,
                1.4,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("frame", frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                break
            if key == ord("s"):
                # the checker board image gets stored
                cv2.imwrite(f"{img_path}/image{n}.png", frame_cp)

                print(f"saved image number {n}")
                n += 1  # the image counter: incrementing
        cap.release()
        cv2.destroyAllWindows()

        print("Total saved Images:", n)

    def make_calibration_table(self, Chess_Board_Dimensions = (9, 6), images_folder = "images", SQUARE_SIZE = 20):
        img_path = self.calib_data_path + "/" + images_folder
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        path = self.calib_data_path + "/" + self.calib_file
        CHECK_DIR = os.path.isdir(img_path)

        if not CHECK_DIR:
            os.makedirs(img_path)
            print(f'"{img_path}" Directory is created')

        else:
            print(f'"{img_path}" Directory already Exists.')

        # prepare object points, i.e. (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        obj_3D = np.zeros((Chess_Board_Dimensions[0] * Chess_Board_Dimensions[1], 3), np.float32)

        obj_3D[:, :2] = np.mgrid[0 : Chess_Board_Dimensions[0], 0 : Chess_Board_Dimensions[1]].T.reshape(
            -1, 2
        )
        obj_3D *= SQUARE_SIZE
        print(obj_3D)

        # Arrays to store object points and image points from all the given images.
        obj_points_3D = []  # 3d point in real world space
        img_points_2D = []  # 2d points in image plane

        files = os.listdir(img_path)  # list of names of all the files present
        for file in files:
            print(file)
            imagePath = os.path.join(img_path, file)
            # print(imagePath)

            image = cv2.imread(imagePath)
            grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(image, Chess_Board_Dimensions, None)
            if ret == True:
                obj_points_3D.append(obj_3D)
                corners2 = cv2.cornerSubPix(grayScale, corners, (3, 3), (-1, -1), criteria)
                img_points_2D.append(corners2)

                img = cv2.drawChessboardCorners(image, Chess_Board_Dimensions, corners2, ret)

        cv2.destroyAllWindows()
        # h, w = image.shape[:2]
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points_3D, img_points_2D, grayScale.shape[::-1], None, None
        )
        print("calibrated")

        print("dumping the data into one files using numpy ")
        np.savez(
            f"{path}",
            camMatrix=mtx,
            distCoef=dist,
            rVector=rvecs,
            tVector=tvecs,
        )

        print("-------------------------------------------")

        print("loading data stored using numpy savez function\n \n \n")

        data = np.load(f"{path}")

        camMatrix = data["camMatrix"]
        distCof = data["distCoef"]
        rVector = data["rVector"]
        tVector = data["tVector"]

        print("loaded calibration data successfully")
