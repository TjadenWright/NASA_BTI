import pygame
from UWB_Class import UWB_Class

# Initialize Pygame
pygame.init()

# Create a Pygame window with a larger size
window_size = (800, 600)  # Adjust the window size as needed
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('UWB Sensor Position')

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)

# Initialize fixed dot positions
anchor_distance = 3.5
fixed_dot1_x = window_size[0] // 2
fixed_dot1_y = window_size[1] // 2

# Define the zoom level as a variable
zoom_level = 5 # Adjust the zoom level as needed

fixed_dot2_x = fixed_dot1_x + anchor_distance * 20 * zoom_level  # Use the zoom level variable
fixed_dot2_y = fixed_dot1_y

uwb1 = UWB_Class(option=1, speed=100)
uwb2 = UWB_Class(option=2, speed=100)
uwb3 = UWB_Class(option=3, speed=100)  # Add a third UWB sensor

arduinoData1 = uwb1.serial_communication()
arduinoData2 = uwb2.serial_communication()
arduinoData3 = uwb3.serial_communication()  # Serial communication for uwb3

font = pygame.font.Font(None, 24)  # Use a smaller font size for labels

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update UWB sensor coordinates
    [a, b] = uwb1.coordinates_calc(anchor_distance, arduinoData1)
    [c, d] = uwb2.coordinates_calc(anchor_distance, arduinoData2)
    [e, f] = uwb3.coordinates_calc(anchor_distance, arduinoData3)  # Calculate position for uwb3

    # Clear the screen
    screen.fill(BLACK)

    # Draw fixed dots with labels
    pygame.draw.circle(screen, GREEN, (fixed_dot1_x, fixed_dot1_y), 5)
    label = font.render('A', True, WHITE)
    screen.blit(label, (fixed_dot1_x + 10, fixed_dot1_y - 10))

    pygame.draw.circle(screen, GREEN, (fixed_dot2_x, fixed_dot2_y), 5)
    label = font.render('B', True, WHITE)
    screen.blit(label, (fixed_dot2_x + 10, fixed_dot2_y - 10))

    # Draw dynamic dots with labels using the zoom level variable
    pygame.draw.circle(screen, BLUE, (int(a * 20 * zoom_level) + fixed_dot1_x, int(b * 20 * zoom_level) + fixed_dot1_y), 5)
    label = font.render('UWB1', True, WHITE)
    screen.blit(label, (int(a * 20 * zoom_level) + fixed_dot1_x + 10, int(b * 20 * zoom_level) + fixed_dot1_y - 10))

    pygame.draw.circle(screen, RED, (int(c * 20 * zoom_level) + fixed_dot1_x, int(d * 20 * zoom_level) + fixed_dot1_y), 5)
    label = font.render('UWB2', True, WHITE)
    screen.blit(label, (int(c * 20 * zoom_level) + fixed_dot1_x + 10, int(d * 20 * zoom_level) + fixed_dot1_y - 10))

    pygame.draw.circle(screen, WHITE, (int(e * 20 * zoom_level) + fixed_dot1_x, int(f * 20 * zoom_level) + fixed_dot1_y), 5)
    label = font.render('UWB3', True, BLUE)  # Label for UWB3 (change color)
    screen.blit(label, (int(e * 20 * zoom_level) + fixed_dot1_x + 10, int(f * 20 * zoom_level) + fixed_dot1_y - 10))

    # Update the screen
    pygame.display.flip()

    # Reduce the frame rate for optimization
    clock.tick(120)  # Adjust the frame rate as needed

pygame.quit()
