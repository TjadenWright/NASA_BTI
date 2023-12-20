import cv2
from cv2 import aruco
import numpy as np
import time
import os
import threading
import queue
import math

class aruco_detect:
    def __init__(self, calib_data_path = None, MARKER_SIZE = 8, verbose = True, Input_Res=(1280, 720), Output_Res = (640, 480), fps_vid = 10, calib_file = "MultiMatrix.npz", num_threads=4):
        self.calib_data_path = calib_data_path  # camera calibration data path
        self.verbose = verbose                  # debugging purpose
        self.MARKER_SIZE = MARKER_SIZE          # how big is the marker?
        self.start_time = time.time()           # start time (for fps)
        self.frame_count = 0                    # frame count for fps start at zero
        self.smoothed_frame_rate = 0            # fps
        self.Input_Res=Input_Res                # input resolution
        self.Output_Res = Output_Res            # output resolution
        self.fps_vid = fps_vid                  # fps of the realtime video
        self.calib_file = calib_file            # calibration file name
        self.frame = None                       # start with a frame

        # distances
        self.x_values = []
        self.y_values = []
        self.z_values = []
        self.distance_list = []
        self.ids_list = []
        self.rVecx = []
        self.rVecy = []
        self.rVecz = []

        # Number of threads for marker detection
        self.num_threads = num_threads
        self.thread_pool = []          # Create a thread pool
        self.frame_queue = queue.Queue()
        self.data_queue = queue.Queue()

        self.max_retries = 3  # Maximum number of retries

        self.lock = threading.Lock()

    # setup camera with its calibrated data
    def calibrated_cam_data(self):
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

    def camera_init(self, url_OR_cam_numb = 0):
        # get the camera feed
        retries = 0
        while True:
            print("Setting up camera.")
            self.cap = cv2.VideoCapture(url_OR_cam_numb) # give the server id shown in IP webcam App
            if self.cap.isOpened():          # check if webcam was sucessfully open
                print("Camera connected.")   # if webcam was open print
                break
            # still waiting
            print("Waiting for camera...")   # elif not print wait and wait a second.
            # didn't connect
            if retries == self.max_retries - 1:
                print("Camera has failed to connect.")
                return False
            retries+=1

        # once connection is made set the format
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.Input_Res[0])
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.Input_Res[1])
        # self.cap.set(cv2.CAP_PROP_FPS, self.fps_vid)
        self.actual_frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)

        # Start the thread for capturing frames
        self.start_capture_thread()

        return True

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

    def detect_markers(self, frame):
        # Convert the image to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get the corners of the Aruco tags
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, self.marker_dict, parameters=self.param_markers)

        self.x_values, self.y_values, self.z_values = [], [], []
        self.distance_list, self.ids_list, self.rVecx, self.rVecy, self.rVecz = [], [], [], [], []

        # Exit if no tags found
        if not marker_corners:
            return

        # If there are markers
        if marker_corners:
            # Get the pose of the markers (rotational and translational)
            rVec, tVec, object_points = aruco.estimatePoseSingleMarkers(marker_corners, self.MARKER_SIZE, self.cam_mat, self.dist_coef)

            # Iterate through the markers
            for i, (ids, corners) in enumerate(zip(marker_IDs, marker_corners)):
                rx, ry, rz = rVec[i][0][0], rVec[i][0][2], rVec[i][0][1]

                # Reverse any bad rvecs
                rx, ry, rz, flips, bad_rot = self.filter_flip(rx, ry, rz)

                # If the rotation vector is not bad
                if not bad_rot:
                    # Calculate the distance from the camera to the Aruco tag
                    distance = np.sqrt(tVec[i][0][2] ** 2 + tVec[i][0][0] ** 2 + tVec[i][0][1] ** 2)

                    # Append the marker information to respective lists
                    self.x_values.append(tVec[i][0][0])
                    self.y_values.append(tVec[i][0][2])
                    self.z_values.append(tVec[i][0][1])
                    self.ids_list.append(ids[0])
                    self.distance_list.append(distance)
                    self.rVecx.append(rx)
                    self.rVecy.append(ry)
                    self.rVecz.append(rz)
                        
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
                    cv2.drawFrameAxes(frame, self.cam_mat, self.dist_coef, rVec[i], tVec[i], 9)

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
                        2.0,
                        (0, 0, 255),
                        2,
                        cv2.LINE_AA,
                    )
        
        return frame

    def start_capture_thread(self):
        # Start the thread for capturing frames
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.daemon = True
        self.capture_thread.start()

    def capture_frames(self):
        while True:
            ret, frame = self.cap.read()
            with self.lock:
                self.frame = frame

    # get the tag data
    def aruco_tags(self, pic_out=True, FPS_read=False):
        # Frame rate calculation
        current_time = time.time()
        self.frame_count += 1
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 1.0:
            self.smoothed_frame_rate = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = current_time

        with self.lock:
            # Check if self.frame is not None before copying
            if self.frame is not None:
                frame = self.frame.copy()
            else:
                frame = None  # or any other suitable default value

        # Process the frame (call detect_markers or any other processing function)
        if frame is not None:
            self.detect_markers(frame)

            # Display the processed frame
            if pic_out:
                display_frame = cv2.resize(frame, self.Output_Res)
                cv2.putText(display_frame, f"Frame Rate: {self.smoothed_frame_rate:.2f} FPS (Actual: {self.actual_frame_rate:.2f} FPS)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Video', display_frame)
            elif FPS_read:
                print(f"Frame Rate: {self.smoothed_frame_rate:.2f} FPS (Actual: {self.actual_frame_rate:.2f} FPS)")

        # x_values, y_values, z_values, dist_list, ids_list, rVecx, rVecy, rVecz
        return self.x_values, self.y_values, self.z_values, self.distance_list, self.ids_list, self.rVecx, self.rVecy, self.rVecz


    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def wait_key(self, key_value = "q"):
        key = cv2.waitKey(1)
        if key == ord(key_value):
            return True
        else:
            return False
    
    ### These functions are for calibration ####
    def take_picks(self, images_folder = "images"):
        # initialization
        n = 0 # set value of saved to 0
        img_path = self.calib_data_path + "/" + images_folder  # go to image path
        Dir_Check = os.path.isdir(img_path) # get directory to check
        
        # shows stuff about the directory
        if not Dir_Check:  # if directory does not exist, a new one is created
            os.makedirs(img_path)
            print(f'"{img_path}" Directory is created')
        else:
            print(f'"{img_path}" Directory already exists.')


        # image out loop (might consider threading just to increase performance)
        while True:
            with self.lock:
                # Check if self.frame is not None before copying
                if self.frame is not None:
                    frame = self.frame.copy()
                else:
                    frame = None  # or any other suitable default value

            if frame is not None:
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
                resized_frame = cv2.resize(frame, self.Output_Res)
                cv2.imshow("frame", resized_frame)

            key = cv2.waitKey(1)
            if key == ord("q"):
                break # breaks the loop
            if key == ord("s"):
                # the checker board image gets stored
                cv2.imwrite(f"{img_path}/image{n}.png", frame_cp)

                print(f"saved image number {n}")
                n += 1  # the image counter: incrementing

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

    ### These function will be for threading purposes ###
    def detect_markers_thread(self):
        # Convert the image to grayscale
        gray_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # Get the corners of the Aruco tags
        marker_corners, marker_IDs, reject = aruco.detectMarkers(gray_frame, self.marker_dict, parameters=self.param_markers)

        # initialize the frame with markers
        frame_with_markers = self.frame.copy()  # Create a copy of the frame

        # intitlaize the closest distance to infinity
        closest_distance = float('inf')
        
        # initialize data sent back
        x_values = []
        y_values = []
        z_values = []
        dist_list = []
        ids_list = []
        rVecx = []
        rVecy = []
        rVecz = []

        # Initialize self.move_flags with False values
        self.move_flags = [False] * len(marker_corners)

        # If there are markers
        if marker_corners:
            object_points = np.array([[-self.MARKER_SIZE   / 2, self.MARKER_SIZE   / 2, 0],
                          [self.MARKER_SIZE   / 2, self.MARKER_SIZE   / 2, 0],
                          [self.MARKER_SIZE   / 2, -self.MARKER_SIZE   / 2, 0],
                          [-self.MARKER_SIZE   / 2, -self.MARKER_SIZE   / 2, 0]])
            # Get the pose of the markers (rotational and translational)
            # rVec, tVec, _ = aruco.estimatePoseSingleMarkers(marker_corners, self.MARKER_SIZE, self.cam_mat, self.dist_coef)
            # Iterate through the markers
            for i, (ids, corners) in enumerate(zip(marker_IDs, marker_corners)):
                success, rVec, tVec = cv2.solvePnP(object_points, marker_corners[i], self.cam_mat, self.dist_coef, False, cv2.SOLVEPNP_IPPE_SQUARE)
                # tVec_i = tVec# [i] #[0]  # Extract tVec[i][0] for readability
                if success:
                    x, y, z = tVec[0][0], tVec[2][0], tVec[1][0] # y and z flipped for mapping

                    # save the rVec into ints
                    rx = rVec[0][0]
                    ry = rVec[2][0]
                    rz = rVec[1][0]

                    # reverse any bad rvecs
                    rx, ry, rz, flip, bad_rot = self.filter_flip(rx, ry, rz)
                    # print("rx: ", round(rx, 3), "ry: ", round(ry, 3), "rz: ", round(rz, 3))
                    if(not bad_rot): # if rotation is good

                        # Calculate the distance from the camera to the Aruco tag
                        distance = np.sqrt(x**2 + y**2 + z**2)

                        # Append the marker information to respective lists
                        x_values.append(tVec[0][0])
                        y_values.append(tVec[2][0])  # flipped y and z for readability
                        z_values.append(tVec[1][0])
                        ids_list.append(ids[0])
                        dist_list.append(distance)
                        rVecx.append(rx)
                        rVecy.append(ry)
                        rVecz.append(rz)

                        # data to send back
                        data = {
                            'x': x_values,
                            'y': y_values,
                            'z': z_values,
                            'dist': dist_list,
                            'ids': ids_list,
                            'rVecx': rVecx,
                            'rVecy': rVecy,
                            'rVecz': rVecz
                        }

                        # Make lines around the Aruco tag
                        cv2.polylines(frame_with_markers, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv2.LINE_AA)

                        # Get the corners individually
                        corners = corners.reshape(4, 2)
                        corners = corners.astype(int)
                        top_right = corners[0].ravel()
                        top_left = corners[1].ravel()
                        bottom_right = corners[2].ravel()
                        bottom_left = corners[3].ravel()

                        # Draw the pose of the marker with the x, y, z lines
                        cv2.drawFrameAxes(frame_with_markers, self.cam_mat, self.dist_coef, rVec, tVec, 9)

                        # Draw the distance vector at the top right
                        cv2.putText(
                            frame_with_markers,
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
                            frame_with_markers,
                            f"x: {round(tVec[0][0], 1)} y: {round(tVec[2][0], 1)} z: {round(tVec[1][0], 1)} rvec: {round(rx,1), round(ry,1), round(rz,1)}", # y and z flipped
                            (bottom_right[0], bottom_right[1]),
                            cv2.FONT_HERSHEY_PLAIN,
                            1.0,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )

                        self.frame_queue.put(frame_with_markers)
                        self.data_queue.put(data)

    def aruco_tags_threaded(self, pic_out=True, FPS_read=True):
        # Read a frame
        __, self.frame = self.cap.read()

        # Ensure there are no more threads than needed
        while len(self.thread_pool) >= self.num_threads:
            for thread in self.thread_pool:
                if not thread.is_alive():
                    self.thread_pool.remove(thread)
                    break

        # Create a thread to detect markers in the frame
        marker_thread = threading.Thread(target=self.detect_markers_thread, args=())
        self.thread_pool.append(marker_thread)
        marker_thread.start()

        # Frame rate calculation
        current_time = time.time()
        self.frame_count += 1
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 1.0:
            self.smoothed_frame_rate = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = current_time

        # Check if there is a frame with markers in the queue
        if not self.frame_queue.empty():
            # Get the frame from the queue
            frame_with_markers = self.frame_queue.get()
        else:
            frame_with_markers = self.frame  # Use the original captured frame

        # data queue
        if not self.data_queue.empty():
            data = self.data_queue.get()
            x_values = data['x']
            y_values = data['y']
            z_values = data['z']
            dist_list = data['dist']
            ids_list = data['ids']
            rVecx = data['rVecx']
            rVecy = data['rVecy']
            rVecz = data['rVecz']

            # print("rx: ", round(rVecx[0], 3), "ry: ", round(rVecy[0], 3), "rz: ", round(rVecz[0], 3))
        else:
            x_values = []
            y_values = []
            z_values = []
            dist_list = []
            ids_list = []
            rVecx = []
            rVecy = []
            rVecz = []
        # Display the frame
        if pic_out:
            display_frame = cv2.resize(frame_with_markers, self.Output_Res)
            cv2.putText(display_frame, f"Frame Rate: {self.smoothed_frame_rate:.2f} FPS (Actual: {self.actual_frame_rate:.2f} FPS)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Video', display_frame)
        elif FPS_read:
            print(f"Frame Rate: {self.smoothed_frame_rate:.2f} FPS (Actual: {self.actual_frame_rate:.2f} FPS)")

        return x_values, y_values, z_values, dist_list, ids_list, rVecx, rVecy, rVecz
    
    def filter_flip(self, rx, ry, rz):
        flip = False
        bad = False
        if(rx < 0): # if roll is negative (meaning there was a glitch)
            # flip
            rx = -rx
            ry = -ry
            rz = -rz
            flip = True

        if(rx > math.pi):
            bad = True
        
        return rx, ry, rz, flip, bad