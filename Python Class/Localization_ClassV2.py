import pygame
import numpy as np
import cv2
import math
from scipy.spatial.transform import Rotation
from pygame.locals import *

class localization:
    def __init__(self, scaling_factor = 1, camera_x = 0, camera_y = 0, camera_z = 0, zoom_factor = 1.0, zoom_step = 0.1, Output_Res=(1280, 720), samplesCal = 100, samplesLoc = 10):
        self.scaling_factor = scaling_factor # scaling factor
        self.camera_x = camera_x             # camera x 
        self.camera_y = camera_y             # camera y
        self.camera_z = camera_z             # camera z
        self.zoom_factor = zoom_factor       # zoom factor
        self.zoom_step = zoom_step           # zoom step
        self.Output_Res = Output_Res         # output res

        self.samples = samplesCal
        self.samplesLoc = samplesLoc

        self.actual_tag = np.array([])
        self.actual_tag_loc = np.array([]).reshape(-1, 6)
        self.cal_seen_move = np.array([])

        # get a sampler array
        self.sample_actual_tag = np.array([]).reshape(-1, 2)
        self.sample_tag_loc = np.array([]).reshape(-1, 6, self.samples)
        # sample camera and current tag
        # self.sample_tag_camera = np.array([]).reshape(2, 6, self.samplesLoc)

        self.zoom_factor = max(0.1, min(5.0, zoom_factor))

        self.calibration_bool = False
        self.end_program = False

        # Define colors
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.GRAY = (192, 192, 192)

        # Define positions and states of tags (for illustration)
        self.tag_positions = [(100, 100), (200, 200), (300, 300)]
        self.tag_states = ["going_towards", "online_not_going", "offline"]

        self.R_flip  = np.zeros((3,3), dtype=np.float32)
        self.R_flip[0,0] = 1.0
        self.R_flip[1,1] =-1.0
        self.R_flip[2,2] =-1.0

        self.camera_roll = 0

        # Initialize Pygame
        pygame.init()

    def init_pygame(self):
        self.screen = pygame.display.set_mode(self.Output_Res)
        self.font = pygame.font.Font(None, 24)

        self.coord_font = pygame.font.Font(None, 16)  # Choose your desired font and size

        # Initialize Pygame screen
        self.screen.fill((0, 0, 0))

    def calibrate_first_marker(self, aruco_class, x, y, z, tags_ids, marker_id):
        print(f"Calibrating marker with ID: {marker_id}")
        
        # Create lists to store 30 samples for x, y, and z
        x_samples, y_samples, z_samples = [], [], []
        rx_samples, ry_samples, rz_samples = [], [], []

        # Collect 30 samples of x, y, and z for the specified marker
        sample_count = 0
        while sample_count < self.samples:
            x, y, z, _, tags_ids, rVx, rVy, rVz = aruco_class.aruco_tags_threaded(pic_out=False, FPS_read=False)
            closest_marker_index = tags_ids.index(marker_id) if marker_id in tags_ids else -1

            if closest_marker_index != -1:
                x_samples.append(x[closest_marker_index])
                y_samples.append(y[closest_marker_index])
                z_samples.append(z[closest_marker_index])
                rx_samples.append(rVx[closest_marker_index])
                ry_samples.append(rVy[closest_marker_index])
                rz_samples.append(rVz[closest_marker_index])
                sample_count += 1

        # Calculate the average values for x, y, and z
        avg_x = np.median(x_samples)
        avg_y = np.median(y_samples)
        avg_z = np.median(z_samples)

        avg_rx = np.median(rx_samples)
        avg_ry = np.median(ry_samples)
        avg_rz = np.median(rz_samples)

        print(f"Calibration completed for marker {marker_id}")
        print(f"Average x: {avg_x}, Average y: {avg_y}, Average z: {avg_z}")

        return avg_x, avg_y, avg_z, avg_rx, avg_ry, avg_rz
    
    def get_origin_tag(self, aruco_class, tags_ids, dist, x, y, z):
        # Check if the 'c' key is pressed
        if self.calibration_bool:
            # reset all saved stuff
            self.actual_tag = np.array([])
            self.actual_tag_loc = np.array([]).reshape(-1, 6)
            self.cal_seen_move = np.array([])

            # get a sampler array
            self.sample_actual_tag = np.array([]).reshape(-1, 2)
            self.sample_tag_loc = np.array([]).reshape(-1, 6, self.samples)

            if len(tags_ids) > 0:
                # Find the closest marker
                index = np.argmin(dist)   # get closest one
                closest_marker_id = tags_ids[index]  # take the tag id and filter it

                # Call calibration function for the closest marker
                _, _, _, drx, dry, drz = self.calibrate_first_marker(aruco_class, x, y, z, tags_ids, closest_marker_id)

                # set that in the coordinates
                self.actual_tag = np.append(self.actual_tag, closest_marker_id)
                self.actual_tag_loc = np.append(self.actual_tag_loc, [0, 0, 0, drx, dry, drz]).reshape(-1, 6)
                self.cal_seen_move = np.append(self.cal_seen_move, 3) # seen and closest one

                # convert that to the that tags position is 0,0,0
                print("for maker id: ", self.actual_tag[0], " its location is now: ", self.actual_tag_loc[:][0])

                self.calibration_bool = False # we are done with calibration
        
            return True
        return False
    
    def compute_tag_camera_location(self, tags_ids, dist, x, y, z, rx, ry, rz):
        if len(self.actual_tag) and len(tags_ids):
            # check if we need to add a new location
            # find the closest tag to relate to
            calc_location_index = np.argsort(dist) # find the tag thats the closest from opencv
            actual_location_index = np.where(self.actual_tag == tags_ids[calc_location_index[0]]) # find the spot in the saved array
            self.cal_seen_move[actual_location_index] = 3 # move and see

            if(actual_location_index[0] >= 0 and calc_location_index[0] >= 0): # if we found something
                # use that location to get the location of the camera
                [self.camera_x, self.camera_y, self.camera_z], camera_pose = self.calculatePos(
                    np.array([x[calc_location_index[0]], y[calc_location_index[0]], z[calc_location_index[0]]]),
                    np.array([rx[calc_location_index[0]], ry[calc_location_index[0]], rz[calc_location_index[0]]]),
                    np.array([self.actual_tag_loc[actual_location_index[0], 0][0], self.actual_tag_loc[actual_location_index[0], 1][0], self.actual_tag_loc[actual_location_index[0], 2][0]]),
                    np.array([self.actual_tag_loc[actual_location_index[0], 3][0], self.actual_tag_loc[actual_location_index[0], 4][0], self.actual_tag_loc[actual_location_index[0], 5][0]])
                )

                camera_pose = camera_pose[:, 0]
                # print(pose[:, 0])
                angles = self.rotationVectorToEulerAngles(camera_pose)
                # print(angles)
                self.camera_roll = -angles[2]
            # take samples of the tags that haven't got a actual location:
            # for i in range(1, len(calc_location_index)): # leave out the first one since that's assumed to be calibrated
            # we have the new camera x,z so we can relate that to the distance the tag is away.
            for i in range(1, len(calc_location_index)):
                actual_location_index = np.where(self.actual_tag == tags_ids[calc_location_index[i]]) # check if the tag was saved
                if actual_location_index[0] >= 0: # saved
                    self.cal_seen_move[actual_location_index] = 2 # seen, but not closest
                else:
                    # if we haven't seen it see if we how many samples we need or if we need to start sampling
                    sample_actual_location_index = np.where(self.sample_actual_tag[:, 0] == tags_ids[calc_location_index[i]]) # check if we are sampling yet
                    # print(self.sample_tag_loc)
                    if sample_actual_location_index[0] >= 0: # we are
                        self.sample_actual_tag[sample_actual_location_index, 1] +=1 # increment the samples
                        if self.sample_actual_tag[sample_actual_location_index, 1] < self.samples:
                        # <------------- sanples of translational and rotational
                            # Assuming you have the rotation vector as [drx, dry, drz]
                            tag_position_world, rvec_tag_world = self.tag_camera_to_world(np.array([self.camera_x, self.camera_y, self.camera_z]),
                                                                                        camera_pose, 
                                                                                        np.array([x[calc_location_index[i]], y[calc_location_index[i]], z[calc_location_index[i]]]),
                                                                                        np.array([rx[calc_location_index[i]], ry[calc_location_index[i]], rz[calc_location_index[i]]])
                            )
                            rvec_tag_world = rvec_tag_world.T[:][0]

                            print(tag_position_world, rvec_tag_world)
                            # save the sample
                            self.sample_tag_loc[sample_actual_location_index, :, int(self.sample_actual_tag[sample_actual_location_index, 1])] = [tag_position_world[0], tag_position_world[1], tag_position_world[2], 
                                                                                                                                                  rvec_tag_world[0], rvec_tag_world[1], rvec_tag_world[2]]# add another sample
                        else: # done sampling
                            # after 30 samples
                            # get the median of the samples and convert rx, ry, rz to roll, pitch, yaw
                            mean_per_tag = np.median(self.sample_tag_loc, axis=2)[sample_actual_location_index, :] # get the tags mean
                            self.actual_tag = np.append(self.actual_tag, tags_ids[calc_location_index[i]]) # save new tag
                            self.actual_tag_loc = np.append(self.actual_tag_loc, mean_per_tag).reshape(-1, 6) # save new tag location with respect to camera
                            self.cal_seen_move = np.append(self.cal_seen_move, 2) # seen and closest one

                    else: # havent sampled start doing so.
                        self.sample_actual_tag = np.append(self.sample_actual_tag, [tags_ids[calc_location_index[i]], 1]).reshape(-1, 2) # save new tag sample at 1 sample
                    # <------------- sanples of translational and rotational
                        # Assuming you have the rotation vector as [drx, dry, drz]
                        tag_position_world, rvec_tag_world = self.tag_camera_to_world(np.array([self.camera_x, self.camera_y, self.camera_z]),
                                                                                      camera_pose, 
                                                                                      np.array([x[calc_location_index[i]], y[calc_location_index[i]], z[calc_location_index[i]]]),
                                                                                      np.array([rx[calc_location_index[i]], ry[calc_location_index[i]], rz[calc_location_index[i]]])
                        )
                        rvec_tag_world = rvec_tag_world.T[:][0]

                        print(tag_position_world, rvec_tag_world)

                        # start a new data set
                        new_data = np.array([[tag_position_world[0], tag_position_world[1], tag_position_world[2], 
                                              rvec_tag_world[0], rvec_tag_world[1], rvec_tag_world[2]]] + [[0,0,0,0,0,0] for _ in range(self.samples-1)]).reshape(1,6,self.samples)
                        # make a new column in the sample array
                        self.sample_tag_loc = np.append(self.sample_tag_loc, new_data).reshape(-1, 6, self.samples) # save new tag location with respect to camera

            # Find the indices where actual tags are not in tags_ids
            indices_not_in_tags_ids = np.where(~np.isin(self.actual_tag, tags_ids))
            for i in range(0, len(indices_not_in_tags_ids)):
                self.cal_seen_move[indices_not_in_tags_ids[i]] = 0 # not seen offline
        
        # if there was no tag found make them all offline
        elif len(self.actual_tag):
            for i in range(0, len(self.actual_tag)):
                self.cal_seen_move[i] = 0

    def show_tags(self):
        for i in range(len(self.actual_tag)):
            # Convert x and z to Pygame coordinates
            pygame_x = int((self.actual_tag_loc[i, 0]) / self.scaling_factor / self.zoom_factor) + self.Output_Res[0] // 2
            pygame_y = self.Output_Res[1] // 2 - int((self.actual_tag_loc[i, 1]) / self.scaling_factor / self.zoom_factor)

            # Determine dot color
            if(self.cal_seen_move[i] == 3):
                dot_color = self.GREEN
            elif(self.cal_seen_move[i] == 2):
                dot_color = self.RED
            elif(self.cal_seen_move[i] == 1):
                dot_color = (255, 255, 0)     # <---- not implemented
            else:
                dot_color = self.GRAY

            # Draw the dot
            pygame.draw.circle(self.screen, dot_color, (pygame_x, pygame_y), 5)

            # Display the tag ID above the dot
            text = self.font.render(f"ID: {int(self.actual_tag[i])}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(pygame_x, pygame_y - 20))
            self.screen.blit(text, text_rect)

            # Display the coordinates next to the dot
            coord_text = self.coord_font.render(f"({self.actual_tag_loc[i, 0]:.2f}, {self.actual_tag_loc[i, 1]:.2f})", True, (255, 255, 255))
            coord_text_rect = coord_text.get_rect(center=(pygame_x, pygame_y + 20))
            self.screen.blit(coord_text, coord_text_rect)

    def show_camera(self):
        # Convert camera coordinates to Pygame coordinates
        pygame_camera_x = self.Output_Res[0] // 2 + int(self.camera_x / self.scaling_factor / self.zoom_factor)
        pygame_camera_y = self.Output_Res[1] // 2 - int(self.camera_y / self.scaling_factor / self.zoom_factor)

        # Draw the camera as a purple dot
        pygame.draw.circle(self.screen, (128, 0, 128), (pygame_camera_x, pygame_camera_y), 10)

        # Display the "Camera" label above the camera dot
        camera_text = self.font.render("Camera", True, (255, 255, 255))
        camera_text_rect = camera_text.get_rect(center=(pygame_camera_x, pygame_camera_y - 20))
        self.screen.blit(camera_text, camera_text_rect)

        # Display the coordinates next to the "Camera" dot
        coord_text = self.coord_font.render(f"({self.camera_x:.2f}, {self.camera_y:.2f})", True, (255, 255, 255))
        coord_text_rect = coord_text.get_rect(center=(pygame_camera_x, pygame_camera_y + 20))
        self.screen.blit(coord_text, coord_text_rect)

        # Calculate the arrow coordinates
        arrow_length = 20  # Length of the arrow
        arrow_x = pygame_camera_x + arrow_length * np.cos(self.camera_roll-math.pi/2)
        arrow_y = pygame_camera_y + arrow_length * np.sin(self.camera_roll-math.pi/2)

        # Draw the arrow
        pygame.draw.line(self.screen, (255, 0, 0), (pygame_camera_x, pygame_camera_y), (arrow_x, arrow_y), 3)

    def update_pygames_screen(self):
        # Update Pygame screen
        pygame.display.flip()

        # end program 
        return self.end_program

    def handler(self):
        # check for key press
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.zoom_factor += self.zoom_step
                elif event.key == pygame.K_DOWN:
                    self.zoom_factor -= self.zoom_step
                if event.key == pygame.K_c:
                    self.calibration_bool = not self.calibration_bool
                if event.key == pygame.K_q:
                    self.end_program = True
        
        # clear pygame screen
        self.screen.fill((0, 0, 0))

    def legend(self):
        # Draw the key in the top left corner
        key_x, key_y = 10, 10
        key_spacing = 30

        for i, (text, color) in enumerate(zip(["Going Towards", "Online, Not Going Towards", "Offline"], [self.GREEN, self.RED, self.GRAY])):
            pygame.draw.circle(self.screen, color, (key_x + 10, key_y + 10 + i * key_spacing), 5)  # Draw dots
            key_text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(key_text_surface, (key_x + 30, key_y + i * key_spacing))

    # Calculate position data from stored values and current values
    def calculatePos(self, tvec, rvec, tvec_orig, rvec_orig, rotation_threshold=0.1):
        tvec = np.transpose(tvec)
        tvec_orig = np.transpose(tvec_orig)
        R = cv2.Rodrigues(rvec)[0]
        dRot = cv2.Rodrigues(rvec_orig)[0]
        tvec = -R.T.dot(tvec)
        tvec = tvec_orig + dRot.dot(tvec)
        tvec = np.transpose(tvec)

        # Calculate the rotation vector (rvec) representing the rotation of the camera
        R_combined = np.dot(R, dRot.T)
        rvec_camera, __ = cv2.Rodrigues(R_combined)

        return tvec, -rvec_camera

    def tag_camera_to_world(self, tvec_camera, rvec_camera, tvec_tag_camera, rvec_tag_camera):
        # Convert rotation vectors to rotation matrices
        R_camera, _ = cv2.Rodrigues(rvec_camera)
        R_tag_camera, _ = cv2.Rodrigues(rvec_tag_camera)

        # Transform tag coordinates from camera to world
        tag_position_world = R_camera.dot(tvec_tag_camera) + tvec_camera

        # Transform tag pose from camera to world
        R_tag_world = R_camera.T.dot(R_tag_camera)

        # Convert rotation matrix to rotation vector
        rvec_tag_world, _ = cv2.Rodrigues(R_tag_world)

        return tag_position_world, rvec_tag_world



    # Get position in marker's coordinate system
    def TranslationInMarker(rvec, tvec):
        tvec = np.transpose(tvec)
        R = cv2.Rodrigues(rvec)[0]
        tvec = -R.T.dot(tvec)
        tvec = np.transpose(tvec)
        return tvec

    def isRotationMatrix(self, R):
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        I = np.identity(3, dtype=R.dtype)
        n = np.linalg.norm(I - shouldBeIdentity)
        return n < 1e-6

    # Calculates rotation vector to euler angles
    def rotationVectorToEulerAngles(self, rvec):
        r = Rotation.from_rotvec(rvec)
        return r.as_euler('xyz')

    # Calculates rotation matrix to rotation vector
    def rotationMatrixToRotationVector(self, dR):
        r = Rotation.from_dcm(dR)
        return r.as_rotvec()
    
    def controller_handler(self, cal, up, down):
        if(cal):
            self.calibration_bool = True
        if(up):
            self.zoom_factor += self.zoom_step
        elif(down):
            self.zoom_factor -= self.zoom_step