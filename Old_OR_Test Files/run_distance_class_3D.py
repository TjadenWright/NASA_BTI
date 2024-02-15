import os
import sys
import numpy as np
import pygame

# Navigate up one directory level to access the class folder
current_file_path = os.path.dirname(os.path.abspath(__file__))          # get the data path of this file
parent_directory = os.path.dirname(current_file_path)                   # get the data parent directory (go back one folder in the directory)
class_folder_path = os.path.join(current_file_path, '../Python Class')  # get the class data path
calib_data_path = os.path.join(current_file_path, '../Calibrated_data') # get the caibrated data path
sys.path.append(class_folder_path)                                      # set the path as the class folder so that the classes show up

from Distance_ClassV3 import aruco_detect

url_OR_cam_numb = 0                                   # <--- camera # if on usb, camera ip if over ethernet/wireless
recal_cam = False                                     # <--- if you need to recalibrate the camera set this to true (only need to do this if you change resolution/camera)
Input_Res = (1920, 1080)                              # <--- change camera resolution (if change reclaibrate)
Output_Res = (640, 480)                               # <--- output resolution
FPS_video = 30                                        # <--- change fps (no need to recalibrate)
MARKER_SIZE = 7                                       # <--- height of the whole tag in cm (or same units as in calibrate sheet)
Calibrate_sheet_square_SIZE = 1.8                     # <--- size of the calibration sheet squares (height of one of the squares in cm (or same units as marker size))
images_folder = "images1080"                          # <--- folder to store images in calibration
calib_file = "MultiMatrix1080.npz"                    # <--- file that stores the matricies. Must end it .npz
DICT_MXM_L = "DICT_7X7_100"                           # <--- dictionary used
num_threads = 8                                       # <--- number of threads used
scaling_factor = 1                                    # <--- You can change this to adjust the scaling
camera_x = 0                                          # Adjust the camera's x position as needed
camera_z = 0                                          # Adjust the camera's z position as needed
zoom_factor = 1.0
zoom_step = 0.1  # You can adjust the step size as needed.

# initialize the aruco detect class
a1 = aruco_detect(calib_data_path=calib_data_path, MARKER_SIZE=MARKER_SIZE, verbose=False, Input_Res=Input_Res, Output_Res=Output_Res, fps_vid=FPS_video, calib_file=calib_file, num_threads=num_threads) # <--- sets up the class

# initialize the camera to the port used at resolution and fps
get_cam = a1.camera_init(url_OR_cam_numb=url_OR_cam_numb)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(Output_Res)
font = pygame.font.Font(None, 36)

coord_font = pygame.font.Font(None, 24)  # Choose your desired font and size

def calibrate_marker(x, y, z, tags_ids, marker_id):
    print(f"Calibrating marker with ID: {marker_id}")
    
    # Create lists to store 30 samples for x, y, and z
    x_samples, y_samples, z_samples = [], [], []

    # Collect 30 samples of x, y, and z for the specified marker
    sample_count = 0
    while sample_count < 30:
        x, y, z, _, tags_ids = a1.aruco_tags_threaded(pic_out=False)
        closest_marker_index = tags_ids.index(marker_id) if marker_id in tags_ids else -1

        if closest_marker_index != -1:
            x_samples.append(x[closest_marker_index])
            y_samples.append(y[closest_marker_index])
            z_samples.append(z[closest_marker_index])
            sample_count += 1

    # Calculate the average values for x, y, and z
    avg_x = np.mean(x_samples)
    avg_y = np.mean(y_samples)
    avg_z = np.mean(z_samples)

    print(f"Calibration completed for marker {marker_id}")
    print(f"Average x: {avg_x}, Average y: {avg_y}, Average z: {avg_z}")

    return avg_x, avg_y, avg_z

actual_tag = np.array([])
actual_tag_loc = np.array([]).reshape(-1, 2)
cal_seen_move = np.array([])

if get_cam:
    # if you need to calibrate
    if recal_cam:
        a1.take_picks(images_folder=images_folder) # takes the pictures press 's' to save each picture and 'q' to end that processes
        a1.make_calibration_table(SQUARE_SIZE=Calibrate_sheet_square_SIZE, images_folder=images_folder) # this will automatically load the pictures and make the camera matrix and the distance coeff matrix

    # add calibrated data to camera
    a1.calibrated_cam_data()

    # set the marker dictionary
    a1.aruco_marker_dict(DICT_MXM_L=DICT_MXM_L) # makes the aruco dictionary (can go into class and change dictionary if you want, default is 4x4 100)

    # Initialize an empty list to store camera positions for the trail
    camera_trail = []

    # Initialize a flag to indicate when to draw the trail
    drawing_trail = False

    # while loop for sensing data
    while True:
        # check for key press
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    zoom_factor += zoom_step
                elif event.key == pygame.K_DOWN:
                    zoom_factor -= zoom_step
                # Start or stop drawing the trail when 'p' is pressed
                if event.key == pygame.K_p:
                    # Toggle the flag to start/stop drawing the trail
                    drawing_trail = not drawing_trail
                    if not drawing_trail:
                        # Clear the camera trail when you stop drawing
                        camera_trail = []

        # Ensure the zoom factor is within a valid range (e.g., not too small or too large).
        zoom_factor = max(0.1, min(5.0, zoom_factor))

        # display the camera along with aruco tag tracking data.
        x, z, y, dist, tags_ids = a1.aruco_tags_threaded(pic_out=True) # <--- if you want a picture to be dispayed.
        # print("x: ", x, "y: ", y, "z: ", z, "dist: ", dist, "ids: ", tags_ids) # look at the last one
        print(actual_tag, actual_tag_loc, camera_x, camera_z)

        # do some math to get the first tag that has its location stored
        if len(actual_tag) and len(tags_ids):
            # check if we need to add a new location
            # find the closest tag to relate to
            calc_location_index = np.argsort(dist) # find the tag thats the closest from opencv
            actual_location_index = np.where(actual_tag == tags_ids[calc_location_index[0]]) # find the spot in the saved array
            cal_seen_move[actual_location_index] = 3 # move and see

            # print(actual_tag_loc[actual_location_index, 0], x[calc_location_index[0]])

            if(actual_location_index[0] >= 0 and actual_location_index[0] >= 0): # if we found something
                # use that location to get the location of the camera
                camera_x = float(actual_tag_loc[actual_location_index, 0] - x[calc_location_index[0]])
                camera_z = float(actual_tag_loc[actual_location_index, 1] - z[calc_location_index[0]])

            # take samples of the tags that haven't got a actual location:
            # for i in range(1, len(calc_location_index)): # leave out the first one since that's assumed to be calibrated
                # we have the new camera x,z so we can relate that to the distance the tag is away.
            for i in range(1, len(calc_location_index)):
                actual_location_index = np.where(actual_tag == tags_ids[calc_location_index[i]]) # check if the tag was saved
                # print(actual_location_index[0])
                if actual_location_index[0] >= 0: # not saved
                    cal_seen_move[actual_location_index] = 2 # seen and closest one
                else:
                    # save it
                    # take the mean of a sample
                    actual_tag = np.append(actual_tag, tags_ids[calc_location_index[i]]) # save new tag
                    actual_tag_loc = np.append(actual_tag_loc, [camera_x + x[calc_location_index[i]], camera_z + z[calc_location_index[i]]]).reshape(-1, 2) # save new tag location with respect to camera
                    cal_seen_move = np.append(cal_seen_move, 2) # seen and closest one

            # Find the indices where actual tags are not in tags_ids
            indices_not_in_tags_ids = np.where(~np.isin(actual_tag, tags_ids))
            for i in range(0, len(indices_not_in_tags_ids)):
                cal_seen_move[indices_not_in_tags_ids[i]] = 0 # not seen offline


        # print("x: ", camera_x, "y: ", camera_z)

        if a1.wait_key("q") or pygame.key.get_pressed()[pygame.K_q]:
            break

        # calibrate the closest one and set that at 0,0
        # sets camera location and sets actual tag location to 0,0
        if a1.wait_key("c") or pygame.key.get_pressed()[pygame.K_c]:
            # Check if the 'c' key is pressed
            if len(tags_ids) > 0:
                # Find the closest marker
                index = np.argmin(dist)
                closest_marker_id = tags_ids[index]

                # Call calibration function for the closest marker
                dx, dy, dz = calibrate_marker(x, y, z, tags_ids, closest_marker_id)
                
                # set that in the coordinates
                actual_tag = np.append(actual_tag, closest_marker_id)
                actual_tag_loc = np.append(actual_tag_loc, [0, 0]).reshape(-1, 2)
                cal_seen_move = np.append(cal_seen_move, 3) # seen and closest one

                # convert that to the cameras position and that tags position is 0,0,0
                print("for maker id: ", actual_tag, " its location is now: ", actual_tag_loc)
                camera_x = -dx
                flipped_y = -dy
                camera_z = -dz
                print("camera location: ", camera_x, flipped_y, camera_z)

        # Initialize Pygame screen
        screen.fill((0, 0, 0))

        # print(actual_tag_loc)

        for i in range(len(actual_tag)):
            # Convert x and z to Pygame coordinates
            pygame_x = -int((actual_tag_loc[i, 0]) / scaling_factor / zoom_factor) + Output_Res[0] // 2
            pygame_y = Output_Res[1] // 2 - int((actual_tag_loc[i, 1]) / scaling_factor / zoom_factor)

            # Determine dot color
            if(cal_seen_move[i] == 3):
                dot_color = (0, 255, 0)
            elif(cal_seen_move[i] == 2):
                dot_color = (165, 42, 42)
            elif(cal_seen_move[i] == 1):
                dot_color = (255, 255, 0)
            else:
                dot_color = (128, 128, 128)

            # Draw the dot
            pygame.draw.circle(screen, dot_color, (pygame_x, pygame_y), 5)

            # Display the tag ID above the dot
            text = font.render(f"ID: {int(actual_tag[i])}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(pygame_x, pygame_y - 20))
            screen.blit(text, text_rect)

            # Display the coordinates next to the dot
            coord_text = coord_font.render(f"({-actual_tag_loc[i, 0]:.2f}, {actual_tag_loc[i, 1]:.2f})", True, (255, 255, 255))
            coord_text_rect = coord_text.get_rect(center=(pygame_x, pygame_y + 20))
            screen.blit(coord_text, coord_text_rect)

        # Draw the camera trail
        if drawing_trail:
            # Add the current camera position to the trail
            camera_trail.append((pygame_camera_x, pygame_camera_y))
            # Draw the camera trail as line segments
            for i in range(1, len(camera_trail)):
                pygame.draw.line(screen, (128, 0, 128), camera_trail[i - 1], camera_trail[i], 10)


        # Convert camera coordinates to Pygame coordinates
        pygame_camera_x = Output_Res[0] // 2 - int(camera_x / scaling_factor / zoom_factor)
        pygame_camera_y = Output_Res[1] // 2 - int(camera_z / scaling_factor / zoom_factor)

        # Draw the camera as a purple dot
        pygame.draw.circle(screen, (128, 0, 128), (pygame_camera_x, pygame_camera_y), 10)

        # Display the "Camera" label above the camera dot
        camera_text = font.render("Camera", True, (255, 255, 255))
        camera_text_rect = camera_text.get_rect(center=(pygame_camera_x, pygame_camera_y - 20))
        screen.blit(camera_text, camera_text_rect)

        # Display the coordinates next to the "Camera" dot
        coord_text = coord_font.render(f"({-camera_x:.2f}, {camera_z:.2f})", True, (255, 255, 255))
        coord_text_rect = coord_text.get_rect(center=(pygame_camera_x, pygame_camera_y + 20))
        screen.blit(coord_text, coord_text_rect)

        # Update Pygame screen
        pygame.display.flip()

    a1.release()