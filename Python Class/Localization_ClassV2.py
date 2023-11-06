import pygame
import numpy as np
import cv2
import math

class localization:
    def __init__(self, scaling_factor = 1, camera_x = 0, camera_y = 0, camera_z = 0, zoom_factor = 1.0, zoom_step = 0.1, Output_Res=(1280, 720)):
        self.scaling_factor = scaling_factor # scaling factor
        self.camera_x = camera_x             # camera x 
        self.camera_y = camera_y             # camera y
        self.camera_z = camera_z             # camera z
        self.zoom_factor = zoom_factor       # zoom factor
        self.zoom_step = zoom_step           # zoom step
        self.Output_Res = Output_Res         # output res

        self.actual_tag = np.array([])
        self.actual_tag_loc = np.array([]).reshape(-1, 6)
        self.cal_seen_move = np.array([])

        # get a sampler array
        self.sample_actual_tag = np.array([]).reshape(-1, 2)
        self.sample_tag_loc = np.array([]).reshape(-1, 6, 30)

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

    def init_pygame(self):
        # Initialize Pygame
        pygame.init()
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
        while sample_count < 30:
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
            self.sample_tag_loc = np.array([]).reshape(-1, 6, 30)

            if len(tags_ids) > 0:
                # Find the closest marker
                index = np.argmin(dist)   # get closest one
                closest_marker_id = tags_ids[index]  # take the tag id and filter it

                # Call calibration function for the closest marker
                dx, dy, dz, drx, dry, drz = self.calibrate_first_marker(aruco_class, x, y, z, tags_ids, closest_marker_id)
                
                # Assuming you have the rotation vector as [drx, dry, drz]
                R_ct, _ = cv2.Rodrigues(np.array([drx, dry, drz]))
                R_tc = R_ct.T
                
                roll_marker, yaw_marker, pitch_marker = self.rotationMatrixToEulerAngles(np.dot(self.R_flip, R_tc))

                # set that in the coordinates
                self.actual_tag = np.append(self.actual_tag, closest_marker_id)
                self.actual_tag_loc = np.append(self.actual_tag_loc, [0, 0, 0, roll_marker, pitch_marker, yaw_marker]).reshape(-1, 6)
                self.cal_seen_move = np.append(self.cal_seen_move, 3) # seen and closest one

                # Initial position estimate based on ArUco tag
                initial_position = np.array([dx, dy, dz])

                # Transform the initial position into camera coordinate system
                self.camera_x, self.camera_y, self.camera_z = np.dot(R_tc, -initial_position)

                # convert that to the cameras position and that tags position is 0,0,0
                print("for maker id: ", self.actual_tag, " its location is now: ", self.actual_tag_loc)
                print("camera location: ", self.camera_x, self.camera_y, self.camera_z)

                self.calibration_bool = False # we are done with calibration
    
    def compute_tag_camera_location(self, tags_ids, dist, x, y, z, rx, ry, rz):
        if len(self.actual_tag) and len(tags_ids):
            # check if we need to add a new location
            # find the closest tag to relate to
            calc_location_index = np.argsort(dist) # find the tag thats the closest from opencv
            actual_location_index = np.where(self.actual_tag == tags_ids[calc_location_index[0]]) # find the spot in the saved array
            self.cal_seen_move[actual_location_index] = 3 # move and see

            # print(actual_tag_loc[actual_location_index, 0], x[calc_location_index[0]])

            if(actual_location_index[0] >= 0 and actual_location_index[0] >= 0): # if we found something
                # use that location to get the location of the camera
                # Assuming you have the rotation vector as [drx, dry, drz]
                roll_marker, yaw_marker, pitch_marker = self.convert_rot_to_ypr(rx[calc_location_index[0]], ry[calc_location_index[0]], rz[calc_location_index[0]])

                # Calculate the localized position by transforming the initial position
                localized_position = self.two_ypr_diff_localization(roll_marker-self.actual_tag_loc[actual_location_index, 3][0, 0],
                                                                    yaw_marker-self.actual_tag_loc[actual_location_index, 5][0, 0], 
                                                                    pitch_marker-self.actual_tag_loc[actual_location_index, 4][0, 0], 
                                                                    x[calc_location_index[0]], y[calc_location_index[0]], z[calc_location_index[0]])

                self.camera_x = float(self.actual_tag_loc[actual_location_index, 0] - localized_position[0])
                self.camera_y = float(self.actual_tag_loc[actual_location_index, 1] - localized_position[1])
                self.camera_z = float(self.actual_tag_loc[actual_location_index, 2] - localized_position[2])

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
                        if self.sample_actual_tag[sample_actual_location_index, 1] < 30:
                            # <------------- sanples of translational and rotational
                            self.sample_tag_loc[sample_actual_location_index, :, int(self.sample_actual_tag[sample_actual_location_index, 1])] = [self.camera_x + x[calc_location_index[i]], self.camera_y + y[calc_location_index[i]], 
                                                                                                                                               self.camera_z + z[calc_location_index[i]]]# add another sample
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
                        new_data = np.array([[self.camera_x + x[calc_location_index[i]], self.camera_y + y[calc_location_index[i]], 
                                                        self.camera_z + z[calc_location_index[i]]]] + [[0,0,0] for _ in range(29)]).reshape(1,6,30)
                        self.sample_tag_loc = np.append(self.sample_tag_loc, new_data).reshape(-1, 6, 30) # save new tag location with respect to camera

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

    def isRotationMatrix(self, R):
        Rt = np.transpose(R)
        shouldBeIdentity = np.dot(Rt, R)
        I = np.identity(3, dtype=R.dtype)
        n = np.linalg.norm(I - shouldBeIdentity)
        return n < 1e-6


    # Calculates rotation matrix to euler angles
    # The result is the same as MATLAB except the order
    # of the euler angles ( x and z are swapped ).
    def rotationMatrixToEulerAngles(self, R):
        assert (self.isRotationMatrix(R))

        sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

        singular = sy < 1e-6

        if not singular:
            x = math.atan2(R[2, 1], R[2, 2])
            y = math.atan2(-R[2, 0], sy)
            z = math.atan2(R[1, 0], R[0, 0])
        else:
            x = math.atan2(-R[1, 2], R[1, 1])
            y = math.atan2(-R[2, 0], sy)
            z = 0

        return np.array([x, y, z])
    
    def convert_rot_to_ypr(self, rx, ry, rz):
        # use that location to get the location of the camera
        # Assuming you have the rotation vector as [drx, dry, drz]
        R_ct, _ = cv2.Rodrigues(np.array([rx, ry, rz]))
        R_tc = R_ct.T
        
        roll_marker, yaw_marker, pitch_marker = self.rotationMatrixToEulerAngles(np.dot(self.R_flip, R_tc))

        return roll_marker, yaw_marker, pitch_marker
    
    def two_ypr_diff_localization(self, roll, pitch, yaw, x, y, z):
        # Create transformation matrices for yaw, pitch, and roll rotations
        R_yaw = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                        [np.sin(yaw), np.cos(yaw), 0],
                        [0, 0, 1]])

        R_pitch = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                            [0, 1, 0],
                            [-np.sin(pitch), 0, np.cos(pitch)]])

        R_roll = np.array([[1, 0, 0],
                        [0, np.cos(roll), -np.sin(roll)],
                        [0, np.sin(roll), np.cos(roll)]])

        # Combine the rotation matrices to get the final transformation matrix
        R_combined = np.dot(R_yaw, np.dot(R_pitch, R_roll))

        # Calculate the localized position by transforming the initial position
        return np.dot(R_combined, [x, y, z]) # location x,y,z