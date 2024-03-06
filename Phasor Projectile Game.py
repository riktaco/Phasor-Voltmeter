import pygame
import math
import random
import sys
import serial

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)  # Added for text color

# Game variables
target_x = random.randint(600, 750)
target_y = HEIGHT - 100
projectile_x, projectile_y = 100, HEIGHT - 100
hit_target = False

# Physics
g = 9.81  # Gravity

# Configure the serial port
try:
    ser = serial.Serial(
        port='COM6',  # Adjust this to your serial port
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )
except serial.SerialException as e:
    print(f"Error opening the serial port: {e}")
    sys.exit(1)

if ser.isOpen():
    print("Serial port is open.")
else:
    print("Failed to open serial port.")
    sys.exit(1)

def serial_read(ser):
    while True:
        strin = ser.readline()
        if strin:
            strin = strin.rstrip()
            strin = strin.decode()
            try:
                current_val = float(strin)
                yield current_val
            except ValueError:
                print("Non-numeric data received.")
        else:
            yield None

def calculate_projectile(angle, amplitude):
    angle_rad = math.radians(angle)
    velocity_x = amplitude * math.cos(angle_rad)
    velocity_y = amplitude * math.sin(angle_rad)

    time_of_flight = 2 * velocity_y / g
    steps = 100
    for step in range(steps):
        t = time_of_flight * (step / steps)
        x = projectile_x + (velocity_x * t)
        y = projectile_y - (velocity_y * t - 0.5 * g * t ** 2)
        pygame.draw.circle(screen, BLUE, (int(x), int(y)), 5)
        if abs(x - target_x) < 20 and abs(y - target_y) < 20:
            return True
    return False

def show_victory_screen(angle):
    screen.fill(GREEN)
    font = pygame.font.Font(None, 74)
    message = f"You Won! Angle: {angle:.2f}"
    text = font.render(message, True, WHITE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(2000)

def display_angle(angle):
    font = pygame.font.Font(None, 36)
    message = f"Angle: {angle:.2f}"
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH - text.get_width() - 10, 10))  # Top right corner

# Main game loop
running = True
serial_generator = serial_read(ser)
last_angle = None

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            ser.close()
            sys.exit()

    # Draw target
    pygame.draw.circle(screen, RED, (target_x, target_y), 10)

    if not hit_target:
        angle = next(serial_generator)
        if angle is not None:
            last_angle = angle
            display_angle(last_angle)  # Display the current angle
            amplitude = 80
            hit_target = calculate_projectile(angle, amplitude)
            if hit_target:
                show_victory_screen(last_angle)
                hit_target = False  # Reset for the next round
                target_x = random.randint(600, 750)  # Reset target
    else:
        if last_angle is not None:
            display_angle(last_angle)  # Ensure angle is displayed even after hitting the target

    pygame.display.flip()

pygame.quit()
