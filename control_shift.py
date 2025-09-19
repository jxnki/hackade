import pygame
import sys
import os

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ceiling-Walking Platformer")
clock = pygame.time.Clock()
FPS = 60

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYER_DIR = os.path.join(SCRIPT_DIR, "assets", "players")
PLATFORM_PATH = os.path.join(SCRIPT_DIR, "assets", "platform.png")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

# --- Load obstacle images (upside down for ceiling) ---
obstacle_images = {
    'wood': pygame.transform.scale(
        pygame.transform.flip(
            pygame.image.load(os.path.join(ASSETS_DIR, "wood.png")).convert_alpha(),
            False, True  # vertical flip for upside-down
        ),
        (40, 40)  # Bigger than before but still smaller than player (80x80)
    ),
    'stone': pygame.transform.scale(
        pygame.transform.flip(
            pygame.image.load(os.path.join(ASSETS_DIR, "stone.png")).convert_alpha(),
            False, True  # vertical flip for upside-down
        ),
        (50, 50)  # Make stone bigger than wood and bush but still smaller than player (80x80)
    ),
    'bush': pygame.transform.scale(
        pygame.transform.flip(
            pygame.image.load(os.path.join(ASSETS_DIR, "bush.png")).convert_alpha(),
            False, True  # vertical flip for upside-down
        ),
        (40, 40)  # Bigger than before but still smaller than player (80x80)
    )
}

# --- Load and flip player images ---
player_images = [
    pygame.transform.scale(
        pygame.transform.flip(
            pygame.image.load(os.path.join(PLAYER_DIR, f"player{i}.png")).convert_alpha(),
            False, True  # vertical flip for upside-down
        ),
        (80, 80)  # Make player bigger - 80x80 pixels
    )
    for i in range(1, 5)
]

player_index = 0
ANIM_SPEED = 0.15
anim_timer = 0

# --- Create brown rectangle platforms ---
PLATFORM_HEIGHT = 80
BROWN_COLOR = (139, 69, 19)  # Saddle brown color

# Top platform (ceiling) - brown rectangle at the very top
top_platform_rect = pygame.Rect(0, 0, WIDTH, PLATFORM_HEIGHT)

# Bottom platform (floor) - brown rectangle at the very bottom  
bottom_platform_rect = pygame.Rect(0, HEIGHT - PLATFORM_HEIGHT, WIDTH, PLATFORM_HEIGHT)

# --- Player setup ---
player_rect = player_images[0].get_rect()
player_rect.midtop = (WIDTH // 2, top_platform_rect.bottom)  # Stand on bottom edge of ceiling platform - stays centered
background_scroll = 0  # For scrolling background effect
scroll_speed = 2  # Speed of background scrolling
gravity = 0
jump_power = 12
on_ceiling = True  # player sticks to ceiling initially
on_floor = False   # player can also be on floor

# --- Lives system ---
lives = 5  # Start with 5 lives
font = pygame.font.Font(None, 36)  # Font for displaying lives
invulnerable_timer = 0  # Timer for invulnerability after getting hit
invulnerable_duration = 60  # 1 second of invulnerability at 60 FPS

# --- Obstacles setup ---
import random
obstacles = []  # List to store obstacle data
obstacle_spawn_timer = 0
obstacle_spawn_delay = 120  # Spawn obstacle every 2 seconds at 60 FPS
obstacle_types = ['wood', 'stone', 'bush']

# --- Game loop ---
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Create scrolling background effect ---
    background_scroll -= scroll_speed
    if background_scroll <= -WIDTH:
        background_scroll = 0
    
    # --- Player stays centered horizontally ---
    player_rect.centerx = WIDTH // 2  # Keep player at center of screen
    
    # --- Spawn obstacles hanging from ceiling ---
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer >= obstacle_spawn_delay:
        obstacle_type = random.choice(obstacle_types)
        obstacle_img = obstacle_images[obstacle_type]
        obstacle_rect = obstacle_img.get_rect()
        obstacle_rect.midtop = (WIDTH + 50, top_platform_rect.bottom)  # Start from right side, hanging from ceiling
        obstacles.append({'type': obstacle_type, 'rect': obstacle_rect, 'image': obstacle_img})
        obstacle_spawn_timer = 0
    
    # --- Move obstacles from right to left ---
    for obstacle in obstacles[:]:  # Use slice copy to avoid modification during iteration
        obstacle['rect'].x -= scroll_speed * 2  # Move obstacles faster than background
        if obstacle['rect'].right < 0:  # Remove obstacles that have gone off screen
            obstacles.remove(obstacle)
    
    # --- Collision detection with obstacles (only on actual touching) ---
    if invulnerable_timer <= 0:  # Only check collision if not invulnerable
        for obstacle in obstacles[:]:
            # Use original rectangles but check for actual overlap, not just proximity
            if player_rect.colliderect(obstacle['rect']):
                # Double-check with center points to ensure actual contact
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                obstacle_center_x = obstacle['rect'].centerx
                obstacle_center_y = obstacle['rect'].centery
                
                # Calculate distance between centers
                distance_x = abs(player_center_x - obstacle_center_x)
                distance_y = abs(player_center_y - obstacle_center_y)
                
                # Only trigger if objects are very close (actual touching)
                min_distance_x = (player_rect.width + obstacle['rect'].width) // 2 - 10
                min_distance_y = (player_rect.height + obstacle['rect'].height) // 2 - 10
                
                if distance_x < min_distance_x and distance_y < min_distance_y:
                    lives -= 1  # Lose a life only on actual touching
                    invulnerable_timer = invulnerable_duration  # Start invulnerability period
                    obstacles.remove(obstacle)  # Remove the obstacle that was hit
                    break  # Exit loop after first collision
    
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
                        on_ceiling = True
                        on_floor = False
                        invulnerable_timer = 0
                        player_rect.midtop = (WIDTH // 2, top_platform_rect.bottom)
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
        continue  # Skip the rest of the game loop
    
    # --- Jump controls only ---
    keys = pygame.key.get_pressed()

    # --- Inverted jump mechanics ---
    if keys[pygame.K_DOWN]:  # Changed from UP to DOWN key
        if on_ceiling and gravity == 0:  # Only jump if standing on ceiling
            gravity = jump_power  # Jump down from ceiling (positive = down)
            on_ceiling = False

    # --- Apply inverted gravity (pulls back to ceiling) ---
    if not on_ceiling and not on_floor:
        gravity -= 0.6  # Inverted gravity - always pulls back up to ceiling
        player_rect.y += gravity  # Positive gravity = move down, negative = move up

    # --- Platform collisions ---
    # Top platform (ceiling) collision - player lands back on ceiling
    if player_rect.top <= top_platform_rect.bottom and gravity < 0:
        player_rect.top = top_platform_rect.bottom
        gravity = 0
        on_ceiling = True
        on_floor = False
    
    # Bottom platform (floor) collision - prevent going through floor
    if player_rect.bottom >= bottom_platform_rect.top and gravity > 0:
        player_rect.bottom = bottom_platform_rect.top
        gravity = 0
        on_floor = True
        on_ceiling = False

    # --- Animate player ---
    anim_timer += ANIM_SPEED
    if anim_timer >= len(player_images):
        anim_timer = 0
    player_index = int(anim_timer)

    # --- Draw ---
    screen.fill((135, 206, 250))  # sky blue
    
    pygame.draw.rect(screen, BROWN_COLOR, top_platform_rect)     # Draw top brown platform
    pygame.draw.rect(screen, BROWN_COLOR, bottom_platform_rect)  # Draw bottom brown platform
    
    # --- Draw obstacles hanging from ceiling ---
    for obstacle in obstacles:
        screen.blit(obstacle['image'], obstacle['rect'])
    
    # --- Draw player with invulnerability flashing effect ---
    if invulnerable_timer <= 0 or invulnerable_timer % 10 < 5:  # Flash during invulnerability
        screen.blit(player_images[player_index], player_rect)
    
    # --- Draw lives counter ---
    lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))  # Red text
    screen.blit(lives_text, (10, 10))  # Top-left corner

    pygame.display.flip()
pygame.quit()
sys.exit()
