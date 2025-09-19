import pygame
import sys
import os
import random

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Slope Platform Scene")
clock = pygame.time.Clock()
FPS = 60

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_DIR = os.path.join(SCRIPT_DIR, "assets", "players")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

# --- Load obstacle images ---
obstacle_images = {
    'wood': pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS_DIR, "wood.png")).convert_alpha(),
        (50, 50)
    ),
    'stone': pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS_DIR, "stone.png")).convert_alpha(),
        (55, 55)
    ),
    'bush': pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS_DIR, "bush.png")).convert_alpha(),
        (45, 45)
    )
}

# --- Load player images ---
player_images = [
    pygame.transform.scale(
        pygame.image.load(os.path.join(PLAYER_DIR, f"player{i}.png")).convert_alpha(),
        (80, 80)
    )
    for i in range(1, 5)
]

player_index = 0
ANIM_SPEED = 0.15
anim_timer = 0

# --- Create brown slope platform ---
BROWN_COLOR = (139, 69, 19)
slope_width = WIDTH * 6  # 6x screen width for longer slope
slope_height = 120  # Reduced from 180 to 120 to prevent jumping above screen
platform_thickness = 60  # Minimum platform thickness from bottom of screen
slope_x = 0
slope_y = HEIGHT - platform_thickness  # Start slope above bottom to maintain platform thickness

# --- Obstacles setup ---
obstacles = []
obstacle_spawn_timer = 0
obstacle_spawn_delay = 90  # Default spawn delay (unused but kept for reference)
obstacle_types = ['wood', 'stone', 'bush']

# Create slope points (ascending then descending only)
def create_slope_points(x, y):
    mid_point = slope_width // 2  # Peak is in middle of slope
    return [
        (x, y),                                    # Start: beginning of slope at surface level
        (x + mid_point, y - slope_height),        # Peak: middle top of slope
        (x + slope_width, HEIGHT),                # End: slope reaches bottom edge of screen
        (x, HEIGHT),                              # Screen bottom left edge
    ]

slope_points = create_slope_points(slope_x, slope_y)

# Function to get slope height at any X position
def get_slope_height_at_x(player_x, slope_x, slope_y):
    relative_x = player_x - slope_x
    
    if relative_x < 0 or relative_x > slope_width:
        return HEIGHT
    
    mid_point = slope_width // 2
    
    if relative_x <= mid_point:
        # Ascending section
        ascent_progress = relative_x / mid_point
        current_height = slope_y - (slope_height * ascent_progress)
    else:
        # Descending section - goes from peak down to bottom of screen
        descent_progress = (relative_x - mid_point) / mid_point
        peak_height = slope_y - slope_height
        # Interpolate from peak height down to HEIGHT (bottom of screen)
        current_height = peak_height + (HEIGHT - peak_height) * descent_progress
    
    return current_height

# --- Player setup ---
player_rect = player_images[0].get_rect()
player_x_pos = WIDTH // 3
player_rect.centerx = player_x_pos
slope_height_at_player = get_slope_height_at_x(player_x_pos, slope_x, slope_y)
player_rect.bottom = slope_height_at_player
gravity = 0
jump_power = 12
on_ground = True

# --- Speed variables ---
base_speed = 5
platform_speed = 8  # Medium speed for flat platform after descent
current_speed = base_speed
max_speed = 12

# --- Lives system ---
lives = 5
font = pygame.font.Font(None, 36)
invulnerable_timer = 0
invulnerable_duration = 60

# --- Game loop ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    # --- Jump ---
    if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground:
        gravity = jump_power
        on_ground = False

    # --- Gravity ---
    if not on_ground:
        gravity -= 0.5
        player_rect.y -= gravity

    # --- Ground collision with slope ---
    slope_height_at_player = get_slope_height_at_x(player_x_pos, slope_x, slope_y)
    
    if not on_ground:
        # Check if player lands on slope
        if player_rect.bottom >= slope_height_at_player:
            player_rect.bottom = slope_height_at_player
            gravity = 0
            on_ground = True
    else:
        # If on ground, keep player on slope surface
        player_rect.bottom = slope_height_at_player

    # --- Calculate speed based on slope section ---
    relative_x = player_x_pos - slope_x
    mid_point = slope_width // 2
    
    if 0 <= relative_x <= slope_width:  # Player is on slope
        if relative_x <= mid_point:  # Ascending section
            current_speed = base_speed
        else:  # Descending section
            # Calculate how far down the descent (0 = peak, 1 = bottom)
            descent_progress = (relative_x - mid_point) / mid_point
            current_speed = base_speed + (max_speed - base_speed) * descent_progress
    else:
        # Not on slope - use normal speed
        current_speed = base_speed

    # --- Move slope left (infinite loop) ---
    slope_x -= current_speed
    if slope_x + slope_width < 0:  # recycle when slope goes off screen
        slope_x = 0  # Reset to start position for seamless loop
    
    # Update slope points with new position
    slope_points = create_slope_points(slope_x, slope_y)

    # --- Spawn obstacles on slope ---
    obstacle_spawn_timer += 1
    
    # Determine current spawn delay based on slope section
    if 0 <= relative_x <= slope_width:  # Player is on slope
        if relative_x <= mid_point:  # Ascending section - more obstacles
            dynamic_spawn_delay = 60  # Every 1 second - higher frequency
        else:  # Descending section - fewer obstacles due to higher speed
            dynamic_spawn_delay = 120  # Every 2 seconds - lower frequency
    else:
        dynamic_spawn_delay = obstacle_spawn_delay  # Default frequency
    
    if obstacle_spawn_timer >= dynamic_spawn_delay:
        obstacle_type = random.choice(obstacle_types)
        obstacle_img = obstacle_images[obstacle_type]
        obstacle_rect = obstacle_img.get_rect()
        
        # Spawn obstacle at right edge of screen on slope surface
        obstacle_x = WIDTH + 50
        obstacle_slope_height = get_slope_height_at_x(obstacle_x, slope_x, slope_y)
        obstacle_rect.midbottom = (obstacle_x, obstacle_slope_height)
        
        obstacles.append({'type': obstacle_type, 'rect': obstacle_rect, 'image': obstacle_img})
        obstacle_spawn_timer = 0
    
    # --- Move obstacles from right to left ---
    for obstacle in obstacles[:]:
        obstacle['rect'].x -= current_speed
        
        # Update obstacle Y position to follow slope
        obstacle_slope_height = get_slope_height_at_x(obstacle['rect'].centerx, slope_x, slope_y)
        obstacle['rect'].bottom = obstacle_slope_height
        
        if obstacle['rect'].right < 0:
            obstacles.remove(obstacle)

    # --- Collision detection with obstacles ---
    if invulnerable_timer <= 0:
        for obstacle in obstacles[:]:
            if player_rect.colliderect(obstacle['rect']):
                # Precise collision - check actual overlap area
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                obstacle_center_x = obstacle['rect'].centerx
                obstacle_center_y = obstacle['rect'].centery
                
                distance_x = abs(player_center_x - obstacle_center_x)
                distance_y = abs(player_center_y - obstacle_center_y)
                
                # Strict contact requirements
                min_distance_x = (player_rect.width + obstacle['rect'].width) // 2 - 25
                min_distance_y = (player_rect.height + obstacle['rect'].height) // 2 - 25
                
                # Check overlap area
                overlap_x = min(player_rect.right, obstacle['rect'].right) - max(player_rect.left, obstacle['rect'].left)
                overlap_y = min(player_rect.bottom, obstacle['rect'].bottom) - max(player_rect.top, obstacle['rect'].top)
                
                # Only trigger on significant contact
                if (distance_x < min_distance_x and distance_y < min_distance_y and 
                    overlap_x > 15 and overlap_y > 15):
                    lives -= 1
                    invulnerable_timer = invulnerable_duration
                    obstacles.remove(obstacle)
                    break
    
    # --- Update invulnerability timer ---
    if invulnerable_timer > 0:
        invulnerable_timer -= 1
    
    # --- Check game over ---
    if lives <= 0:
        # Game over screen
        screen.fill((0, 0, 0))  # Black background
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))  # Red text
        restart_text = font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 30))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 10))
        pygame.display.flip()
        
        # Wait for restart or quit
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Restart game
                        lives = 5
                        obstacles.clear()
                        gravity = 0
                        on_ground = True
                        invulnerable_timer = 0
                        slope_x = 0
                        current_speed = base_speed
                        slope_height_at_player = get_slope_height_at_x(player_x_pos, slope_x, slope_y)
                        player_rect.bottom = slope_height_at_player
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        continue  # Skip the rest of the game loop

    # --- Animate player ---
    anim_timer += ANIM_SPEED
    if anim_timer >= len(player_images):
        anim_timer = 0
    player_index = int(anim_timer)

    # --- Draw ---
    screen.fill((135, 206, 250))  # sky blue
    pygame.draw.polygon(screen, BROWN_COLOR, slope_points)
    
    # Draw obstacles
    for obstacle in obstacles:
        screen.blit(obstacle['image'], obstacle['rect'])
    
    # Draw player with invulnerability flashing
    if invulnerable_timer <= 0 or invulnerable_timer % 10 < 5:
        screen.blit(player_images[player_index], player_rect)
    
    # Draw lives counter
    lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
    screen.blit(lives_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
