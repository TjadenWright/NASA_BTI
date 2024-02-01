import pygame
import sys
import math
import random
import time

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battery Status")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Battery dimensions
BATTERY_WIDTH = 100
BATTERY_HEIGHT = 50
BATTERY_X = 50
BATTERY_Y = 50

# Speedometer dimensions
SPEEDOMETER_RADIUS = 50
SPEEDOMETER_CENTER = (BATTERY_X + BATTERY_WIDTH + 100, BATTERY_Y + BATTERY_HEIGHT // 2)
SPEEDOMETER_START_ANGLE = 2 * math.pi  # Start angle for semicircle
SPEEDOMETER_END_ANGLE = math.pi  # End angle for semicircle
SPEEDOMETER_MAX_VALUE= 70

# Font
font = pygame.font.Font(None, 36)

# Function to draw battery
def draw_battery(screen, percent, charging):
    # Draw background
    screen.fill(BLACK)
    
    # Draw battery outline
    pygame.draw.rect(screen, WHITE, (BATTERY_X, BATTERY_Y, BATTERY_WIDTH, BATTERY_HEIGHT), 2)
    
    # Calculate fill width based on percent
    fill_width = (BATTERY_WIDTH - 4) * percent / 100
    
    # Determine color based on percent
    if percent <= 10:
        color = RED
    elif percent <= 25:
        color = YELLOW
    else:
        color = GREEN
    
    # Draw battery fill
    pygame.draw.rect(screen, color, (BATTERY_X + 2, BATTERY_Y + 2, fill_width, BATTERY_HEIGHT - 4))
    
    # Draw charge symbol if charging
    if charging:
        charge_x = BATTERY_X + BATTERY_WIDTH + 10
        charge_y = BATTERY_Y + BATTERY_HEIGHT // 2
        draw_charging_symbol(screen, charge_x, charge_y, WHITE)
    
    # Draw battery percentage text
    text = font.render(f"{percent}%", True, WHITE)
    text_rect = text.get_rect(center=(BATTERY_X + BATTERY_WIDTH // 2 + 5, BATTERY_Y - 20))
    screen.blit(text, text_rect)

    font_big = pygame.font.Font(None, 72)

    if(color == RED):
        txt = font_big.render("!", True, WHITE)
        tet_rect = txt.get_rect(center=(BATTERY_X + BATTERY_WIDTH // 2, BATTERY_Y + 28))
        screen.blit(txt, tet_rect)
    
def speedometer(speed, value="V", max_val = 70, x = BATTERY_X + BATTERY_WIDTH + 100, y = BATTERY_Y + BATTERY_HEIGHT // 2, fuse=0, r = 50):
    # Draw speedometer
    # pygame.draw.arc(screen, BLUE, (SPEEDOMETER_CENTER[0] - SPEEDOMETER_RADIUS, SPEEDOMETER_CENTER[1] - SPEEDOMETER_RADIUS, 2 * SPEEDOMETER_RADIUS, 2 * SPEEDOMETER_RADIUS), SPEEDOMETER_START_ANGLE, SPEEDOMETER_END_ANGLE, 2)

    # Fill the semicircle behind the indicator
    indicator_angle = SPEEDOMETER_START_ANGLE + ((max_val-speed) / max_val) * (SPEEDOMETER_END_ANGLE - SPEEDOMETER_START_ANGLE)
    indicator_pos = (int(x + r * math.cos(indicator_angle)), int(y + r * math.sin(indicator_angle)))

    if(fuse > 0):
        indicator_angle_fuse = SPEEDOMETER_START_ANGLE + ((max_val-fuse) / max_val) * (SPEEDOMETER_END_ANGLE - SPEEDOMETER_START_ANGLE)
        indicator_pos_fuse = (int(x + r * math.cos(indicator_angle_fuse)), int(y + r * math.sin(indicator_angle_fuse)))

    # Draw indicator on speedometer based on speed
    # pygame.draw.line(screen, WHITE, SPEEDOMETER_CENTER, indicator_pos, 2)

    # Draw line for the bottom of the semicircle
    bottom_point_left = (x - r, y)
    bottom_point_right = (x + r, y)
    # pygame.draw.line(screen, BLUE, bottom_point_left, bottom_point_right, 2)

    # Calculate points along the arc
    arc_points = []
    num_points = 100
    for i in range(num_points + 1):
        angle = SPEEDOMETER_END_ANGLE + 0.07 + (indicator_angle - SPEEDOMETER_END_ANGLE) * i / num_points
        x_new = x + (SPEEDOMETER_RADIUS-2) * math.cos(angle-.1)
        y_new = y + (SPEEDOMETER_RADIUS-2) * math.sin(angle-.1)
        arc_points.append((x_new, y_new))

    # Create a polygon to fill the area between the lines
    polygon_points = [bottom_point_left, (x, y), (x, y), indicator_pos]

    if(fuse == 0):
        if(speed <= 0.5*max_val):
            color = GREEN
        elif(speed <= 0.7*max_val and speed > 0.5*max_val):
            color = YELLOW
        else:
            color = RED
    else:
        if(speed <= 0.5*fuse):
            color = GREEN
        elif(speed <= fuse and speed > 0.5*fuse):
            color = YELLOW
        else:
            color = RED

    # Fill the polygon with color
    pygame.draw.polygon(screen, color, polygon_points)
    # Create a polygon from the points and fill it
    pygame.draw.polygon(screen, color, arc_points)

    pygame.draw.arc(screen, WHITE, (x - r, y - r, 2 * r, 2 * r), SPEEDOMETER_START_ANGLE, SPEEDOMETER_END_ANGLE, 2)
    pygame.draw.line(screen, WHITE, (x,y), indicator_pos, 2)
    pygame.draw.line(screen, WHITE, bottom_point_left, bottom_point_right, 2)

    if(fuse > 0):
        pygame.draw.line(screen, RED, (x,y), indicator_pos_fuse, 4)

    # Draw speed number
    font = pygame.font.Font(None, 36)
    text_surface = font.render(str(speed) + value, True, WHITE)
    text_rect = text_surface.get_rect(center=(x, y + 20))
    screen.blit(text_surface, text_rect)

    if(fuse > 0):
        text_surface = font.render(str(fuse) + value, True, RED)
        text_rect = text_surface.get_rect(center=(x, y + 45))
        screen.blit(text_surface, text_rect)

    font_big = pygame.font.Font(None, 72)

    if(color == RED):
        txt = font_big.render("!", True, WHITE)
        tet_rect = txt.get_rect(center=(x, y - 20))
        screen.blit(txt, tet_rect)


# Function to draw charging symbol with triangles
def draw_charging_symbol(screen, x, y, color):
    # Draw upper triangle
    pygame.draw.polygon(screen, color, [(x - 8, y), (x + 3, y), (x, y - 18)])
    # Draw lower triangle
    pygame.draw.polygon(screen, color, [(x - 3, y-4), (x + 8, y-4), (x, y + 14)])

# Main loop
def main():
    battery_percent = 10  # Example battery percentage, replace this with your variable
    charging = True  # Example charging status, replace this with your variable
    voltage = 48.7  # Example speed, replace this with your variable
    current = 80.4
    fuse_current = 80
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        battery_percent = random.randint(0, 100)
        voltage = round(random.uniform(0, 58.4), 2)
        current = round(random.uniform(0, 100), 2)
        fuse_current = round(random.uniform(75, 85), 2)
        charging = random.choice([True, False])

        draw_battery(screen, battery_percent, charging)
        speedometer(voltage)
        speedometer(current, "A", max_val=100, x=BATTERY_X + BATTERY_WIDTH + 220, y=BATTERY_Y + BATTERY_HEIGHT // 2, fuse=fuse_current)
        pygame.display.flip()

        time.sleep(2)

if __name__ == "__main__":
    main()
