import pygame
import serial
import threading
import time
import random

# Configure the serial connection
ser = serial.Serial('COM9', 9600, timeout=1)  # Replace 'COMX' with your serial port

# Global variables for data
x_value = 512
y_value = 512
distance = 100  # Initial distance value
button_state = 1  # 1 = not pressed, 0 = pressed

def read_from_arduino():
    global x_value, y_value, distance, button_state
    while True:
        try:
            data = ser.readline().decode('utf-8').rstrip()
            if data:
                values = data.split(',')
                if len(values) == 4:
                    x_value = int(values[0])
                    y_value = int(values[1])
                    distance = float(values[2])
                    button_state = int(values[3])
        except Exception as e:
            print(f"Serial read error: {e}")

# Start a thread to read data from Arduino
thread = threading.Thread(target=read_from_arduino)
thread.daemon = True
thread.start()

# Initialize Pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Interactive Game with Ultrasonic Sensor")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 255, 0)
ITEM_COLOR = (255, 255, 0)
ENEMY_COLOR = (255, 0, 0)
SHIELD_COLOR = (0, 0, 255)  # Shield color (blue)

# Initial player position
player_pos = [screen_width // 2, screen_height // 2]
player_radius = 20

# Variable for the score
score = 0

# List for collectible items
items = []

# List for projectiles
bullets = []

# Fonts for the score and game over message
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# Variable for the game state
game_over = False

# Initial enemy position
enemy_pos = [random.randint(0, screen_width - 30), random.randint(0, screen_height - 30)]
enemy_size = 30
enemy_speed = 2  # Enemy speed

# Previous button state
previous_button_state = 1  # 1 = not pressed, 0 = pressed

# Variable for the shield
shield_active = False
shield_duration = 0  # Shield duration in frames

# Threshold to activate the shield (in centimeters)
SHIELD_DISTANCE_THRESHOLD = 10  # If the hand is within 10 cm from the sensor, the shield activates

# Function to generate a new item
def spawn_item():
    item_x = random.randint(20, screen_width - 20)
    item_y = random.randint(20, screen_height - 20)
    items.append([item_x, item_y])

# Timer for spawning items
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)  # Generate a new item every 2 seconds

# Main game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT and not game_over:
            spawn_item()
    # If the game is over
    if game_over:
        # Read joystick input to restart
        if y_value < 500:  # If the joystick is pushed up (value less than 500)
            # Reset game variables
            game_over = False
            score = 0
            player_pos = [screen_width // 2, screen_height // 2]
            items.clear()
            bullets.clear()
            enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]
            shield_active = False
            shield_duration = 0
        else:
            # Show the game over screen
            screen.fill(BLACK)
            game_over_text = game_over_font.render("GAME OVER", True, WHITE)
            instruction_text = font.render("Move the joystick up to start again", True, WHITE)
            screen.blit(game_over_text, ((screen_width - game_over_text.get_width()) // 2, screen_height // 2 - 50))
            screen.blit(instruction_text, ((screen_width - instruction_text.get_width()) // 2, screen_height // 2 + 20))
            pygame.display.flip()
            clock.tick(60)
            continue  # Skip the rest of the loop and wait for input to restart
    # Map joystick values (from 0-1023 to -1 to 1)
    x_mapped = (x_value - 512) / 512  # Values from -1 to 1
    y_mapped = (y_value - 512) / 512  # Values from -1 to 1
    # Constant player speed
    speed = 5  # Fixed speed
    # Update the player's position
    player_pos[0] += x_mapped * speed
    player_pos[1] += y_mapped * speed
    # Limit to screen edges
    player_pos[0] = max(0, min(player_pos[0], screen_width))
    player_pos[1] = max(0, min(player_pos[1], screen_height))
    # Enemy movement towards the player
    if enemy_pos[0] < player_pos[0]:
        enemy_pos[0] += enemy_speed
    elif enemy_pos[0] > player_pos[0]:
        enemy_pos[0] -= enemy_speed
    if enemy_pos[1] < player_pos[1]:
        enemy_pos[1] += enemy_speed
    elif enemy_pos[1] > player_pos[1]:
        enemy_pos[1] -= enemy_speed
    # Joystick button handling for shooting
    # Check if the button has just been pressed
    if button_state == 0 and previous_button_state == 1:
        # Create a new projectile
        bullet_pos = [player_pos[0], player_pos[1]]
        bullet_speed = -10  # Projectile speed (upwards)
        bullets.append({'pos': bullet_pos, 'speed': bullet_speed})
    # Update previous button state
    previous_button_state = button_state
    # Update the positions of the projectiles
    for bullet in bullets[:]:
        bullet['pos'][1] += bullet['speed']
        # Remove the projectile if it goes off-screen
        if bullet['pos'][1] < 0:
            bullets.remove(bullet)
        else:
            # Check collision with the enemy
            bullet_rect = pygame.Rect(bullet['pos'][0] - 5, bullet['pos'][1] - 10, 10, 10)
            enemy_rect = pygame.Rect(int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size)
            if bullet_rect.colliderect(enemy_rect):
                bullets.remove(bullet)
                # The enemy has been hit
                # Reposition the enemy to a new random location
                enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]
                # Increase the score or difficulty
                score += 5  # Increment the score
    # Protective Shield Handling
    if distance <= SHIELD_DISTANCE_THRESHOLD:
        shield_active = True
        shield_duration = 120  # The shield remains active for 2 seconds (60 FPS * 2)
    else:
        if shield_duration > 0:
            shield_duration -= 1
        else:
            shield_active = False
    # Draw on the screen
    screen.fill(BLACK)
    # Draw the items
    for item in items[:]:
        pygame.draw.circle(screen, ITEM_COLOR, (int(item[0]), int(item[1])), 10)
        # Check collision with the player
        distance_to_player = ((player_pos[0] - item[0]) ** 2 + (player_pos[1] - item[1]) ** 2) ** 0.5
        if distance_to_player < player_radius + 10:
            items.remove(item)
            score += 1  # Increment the score
    # Draw the player
    pygame.draw.circle(screen, PLAYER_COLOR, (int(player_pos[0]), int(player_pos[1])), player_radius)
    # Draw the shield if active
    if shield_active:
        pygame.draw.circle(screen, SHIELD_COLOR, (int(player_pos[0]), int(player_pos[1])), player_radius + 10, 2)
    # Draw the projectiles
    for bullet in bullets:
        pygame.draw.polygon(screen, WHITE, [
            (bullet['pos'][0], bullet['pos'][1]),
            (bullet['pos'][0] - 5, bullet['pos'][1] + 10),
            (bullet['pos'][0] + 5, bullet['pos'][1] + 10)
        ])
    # Draw the enemy
    pygame.draw.rect(screen, ENEMY_COLOR, (int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size))
    # Check collision between the player and the enemy
    enemy_rect = pygame.Rect(int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size)
    player_rect = pygame.Rect(int(player_pos[0] - player_radius), int(player_pos[1] - player_radius), player_radius * 2, player_radius * 2)
    if enemy_rect.colliderect(player_rect):
        if not shield_active:
            game_over = True
        else:
            # The enemy is repelled or repositioned
            enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]
    # Display the score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()
    # Control the frame rate
    clock.tick(60)
# Clean up
pygame.quit()
ser.close()
