import pygame
import numpy as np

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
        self.actual_tag_loc = np.array([]).reshape(-1, 3)
        self.cal_seen_move = np.array([])

        # get a sampler array
        self.sample_actual_tag = np.array([]).reshape(-1, 2)
        self.sample_tag_loc = np.array([]).reshape(-1, 3, 30)

        self.zoom_factor = max(0.1, min(5.0, zoom_factor))

        self.calibration_bool = False
        self.end_program = False

    def init_pygame(self):
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.Output_Res)
        self.font = pygame.font.Font(None, 36)

        self.coord_font = pygame.font.Font(None, 24)  # Choose your desired font and size

        # Initialize Pygame screen
        self.screen.fill((0, 0, 0))

    def calibrate_first_marker(self, aruco_class, x, y, z, tags_ids, marker_id):
        print(f"Calibrating marker with ID: {marker_id}")
        
        # Create lists to store 30 samples for x, y, and z
        x_samples, y_samples, z_samples = [], [], []

        # Collect 30 samples of x, y, and z for the specified marker
        sample_count = 0
        while sample_count < 30:
            x, y, z, _, tags_ids = aruco_class.aruco_tags_threaded(pic_out=False, FPS_read=False)
            closest_marker_index = tags_ids.index(marker_id) if marker_id in tags_ids else -1

            if closest_marker_index != -1:
                x_samples.append(x[closest_marker_index])
                y_samples.append(y[closest_marker_index])
                z_samples.append(z[closest_marker_index])
                sample_count += 1

        # Calculate the average values for x, y, and z
        avg_x = np.median(x_samples)
        avg_y = np.median(y_samples)
        avg_z = np.median(z_samples)

        print(f"Calibration completed for marker {marker_id}")
        print(f"Average x: {avg_x}, Average y: {avg_y}, Average z: {avg_z}")

        return avg_x, avg_y, avg_z
    
    def get_origin_tag(self, aruco_class, tags_ids, dist, x, y, z):
        # Check if the 'c' key is pressed
        if self.calibration_bool:
            # reset all saved stuff
            self.actual_tag = np.array([])
            self.actual_tag_loc = np.array([]).reshape(-1, 3)
            self.cal_seen_move = np.array([])

            # get a sampler array
            self.sample_actual_tag = np.array([]).reshape(-1, 2)
            self.sample_tag_loc = np.array([]).reshape(-1, 3, 30)

            if len(tags_ids) > 0:
                # Find the closest marker
                index = np.argmin(dist)   # get closest one
                closest_marker_id = tags_ids[index]  # take the tag id and filter it

                # Call calibration function for the closest marker
                dx, dy, dz = self.calibrate_first_marker(aruco_class, x, y, z, tags_ids, closest_marker_id)
                
                # set that in the coordinates
                self.actual_tag = np.append(self.actual_tag, closest_marker_id)
                self.actual_tag_loc = np.append(self.actual_tag_loc, [0, 0, 0]).reshape(-1, 3)
                self.cal_seen_move = np.append(self.cal_seen_move, 3) # seen and closest one

                # convert that to the cameras position and that tags position is 0,0,0
                print("for maker id: ", self.actual_tag, " its location is now: ", self.actual_tag_loc)
                self.camera_x = -dx
                self.camera_y = -dy
                self.camera_z = -dz
                print("camera location: ", self.camera_x, self.camera_y, self.camera_z)

                self.calibration_bool = False # we are done with calibration
    
    def compute_tag_camera_location(self, tags_ids, dist, x, y, z):
        if len(self.actual_tag) and len(tags_ids):
            # check if we need to add a new location
            # find the closest tag to relate to
            calc_location_index = np.argsort(dist) # find the tag thats the closest from opencv
            actual_location_index = np.where(self.actual_tag == tags_ids[calc_location_index[0]]) # find the spot in the saved array
            self.cal_seen_move[actual_location_index] = 3 # move and see

            # print(actual_tag_loc[actual_location_index, 0], x[calc_location_index[0]])

            if(actual_location_index[0] >= 0 and actual_location_index[0] >= 0): # if we found something
                # use that location to get the location of the camera
                self.camera_x = float(self.actual_tag_loc[actual_location_index, 0] - x[calc_location_index[0]])
                self.camera_y = float(self.actual_tag_loc[actual_location_index, 1] - y[calc_location_index[0]])
                self.camera_z = float(self.actual_tag_loc[actual_location_index, 2] - z[calc_location_index[0]])

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
                            self.sample_tag_loc[sample_actual_location_index, :, int(self.sample_actual_tag[sample_actual_location_index, 1])] = [self.camera_x + x[calc_location_index[i]], self.camera_y + y[calc_location_index[i]], 
                                                                                                                                               self.camera_z + z[calc_location_index[i]]]# add another sample
                        else: # done sampling
                            # after 30 samples
                            mean_per_tag = np.median(self.sample_tag_loc, axis=2)[sample_actual_location_index, :] # get the tags mean
                            self.actual_tag = np.append(self.actual_tag, tags_ids[calc_location_index[i]]) # save new tag
                            self.actual_tag_loc = np.append(self.actual_tag_loc, mean_per_tag).reshape(-1, 3) # save new tag location with respect to camera
                            self.cal_seen_move = np.append(self.cal_seen_move, 2) # seen and closest one

                    else: # havent sampled start doing so.
                        self.sample_actual_tag = np.append(self.sample_actual_tag, [tags_ids[calc_location_index[i]], 1]).reshape(-1, 2) # save new tag sample at 1 sample
                        new_data = np.array([[self.camera_x + x[calc_location_index[i]], self.camera_y + y[calc_location_index[i]], 
                                                        self.camera_z + z[calc_location_index[i]]]] + [[0,0,0] for _ in range(29)]).reshape(1,3,30)
                        self.sample_tag_loc = np.append(self.sample_tag_loc, new_data).reshape(-1, 3, 30) # save new tag location with respect to camera

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
                dot_color = (0, 255, 0)
            elif(self.cal_seen_move[i] == 2):
                dot_color = (165, 42, 42)
            elif(self.cal_seen_move[i] == 1):
                dot_color = (255, 255, 0)
            else:
                dot_color = (128, 128, 128)

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