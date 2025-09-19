import pygame
import sys
import random
import os

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - High Speed Runner")

clock = pygame.time.Clock()
FPS = 60

# --- Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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
    ),
    'arrow': pygame.transform.scale(
        pygame.image.load(os.path.join(ASSETS_DIR, "arrow.png")).convert_alpha(),
        (60, 30)
    )
}
obstacle_types = ['wood', 'stone', 'bush']

# Platform setup
platform_height = 50
platform_y = HEIGHT - platform_height
platform_scroll = 0
platform_width = 200
platform_speed = 8   # start fast
speed_increase = 0.01  # speed ramps up every frame

# Player setup
player_frames = []
num_frames = 4
for i in range(1, num_frames + 1):
    img = pygame.image.load(f"assets/players/player{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (80, 80))
    player_frames.append(img)

player_rect = player_frames[0].get_rect()
player_rect.x = 100
player_rect.y = platform_y - player_rect.height

# Animation variables
current_frame = 0
frame_counter = 0
animation_speed = 0.25

# Physics
player_vel_y = 0
gravity = 1
jump_strength = 18

# Obstacles
obstacles = []
obstacle_timer = 0
obstacle_interval = 70

# Flying arrows
arrows = []
arrow_timer = 0
arrow_interval = 120  # Less frequent than ground obstacles

# Spacing system to prevent simultaneous spawning
last_obstacle_spawn = 0
last_arrow_spawn = 0
min_spacing = 60  # Minimum frames between different obstacle types

# Lives
lives = 5
font = pygame.font.SysFont(None, 36)

# Game state
game_over = False

def reset_game():
    global lives, obstacles, arrows, player_rect, player_vel_y, game_over, platform_speed, last_obstacle_spawn, last_arrow_spawn
    lives = 5
    obstacles = []
    arrows = []
    player_rect.x = 100
    player_rect.y = platform_y - player_rect.height
    player_vel_y = 0
    last_obstacle_spawn = 0
    last_arrow_spawn = 0
    platform_speed = 8
    game_over = False

# Load caution image for platform display
caution_img = pygame.image.load(os.path.join(ASSETS_DIR, "caution.png")).convert_alpha()
caution_img = pygame.transform.scale(caution_img, (350, 250))  # Larger size for better visibility

# Game state variables
game_started = False
caution_timer = 0
caution_display_time = 90  # 1.5 seconds at 60 FPS - just enough to read

running = True
while running:
    clock.tick(FPS)
    screen.fill((132, 213, 167))  # soft greenish background (normal color)

    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if not game_over:
        # Show caution on platform for first 3 seconds
        if not game_started:
            caution_timer += 1
            if caution_timer >= caution_display_time:
                game_started = True
        
        # Only start game mechanics after caution period
        if game_started:
            # Increase platform speed over time
            platform_speed += speed_increase

            # Player jump
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player_rect.bottom >= platform_y:
                player_vel_y = -jump_strength

            # Apply gravity
            player_vel_y += gravity
            player_rect.y += player_vel_y

            # Collision with platform
            if player_rect.bottom >= platform_y and player_vel_y >= 0:
                player_rect.bottom = platform_y
                player_vel_y = 0

            # Scroll platform
            platform_scroll += platform_speed
            if platform_scroll >= platform_width:
                platform_scroll = 0
        else:
            # During caution period, keep player on platform but don't move
            if player_rect.bottom >= platform_y:
                player_rect.bottom = platform_y
                player_vel_y = 0

        # Draw scrolling platforms with brown color
        for i in range(-1, WIDTH // platform_width + 2):
            pygame.draw.rect(screen, (139, 69, 19),
                             (i * platform_width - platform_scroll, platform_y, platform_width, platform_height))

        # Animate player
        frame_counter += animation_speed
        if frame_counter >= len(player_frames):
            frame_counter = 0
        current_frame = int(frame_counter)
        screen.blit(player_frames[current_frame], player_rect)

        # Show caution image on platform during initial period
        if not game_started:
            # Display caution image on the platform
            caution_rect = caution_img.get_rect(center=(WIDTH//2, platform_y - 120))
            screen.blit(caution_img, caution_rect)

        # Only spawn obstacles after game starts
        if game_started:
            # Spawn obstacles (with spacing check to avoid arrows)
            obstacle_timer += 1
            if obstacle_timer >= obstacle_interval:
                # Check if enough time has passed since last arrow spawn
                if last_arrow_spawn >= min_spacing:
                    obstacle_timer = 0
                    last_obstacle_spawn = 0  # Reset counter for spacing
                    # Pick random obstacle type
                    obstacle_type = random.choice(obstacle_types)
                    obstacle_img = obstacle_images[obstacle_type]
                    obstacle_size = obstacle_img.get_width()
                    
                    obs_rect = pygame.Rect(WIDTH + 50, platform_y - obstacle_size, obstacle_size, obstacle_size)
                    obstacles.append({
                        "rect": obs_rect,
                        "type": obstacle_type,
                        "image": obstacle_img
                    })

        # Move + draw obstacles (always show existing obstacles)
        for obs in obstacles[:]:
            obs["rect"].x -= platform_speed
            # Draw the actual obstacle image instead of colored rectangle
            screen.blit(obs["image"], obs["rect"])

            # Collision - More accurate collision detection
            # Adjust player collision box to match visible sprite area
            player_collision = player_rect.inflate(-25, -15)  # Tighter fit around player sprite
            
            # Adjust obstacle collision box based on obstacle type for better accuracy
            if obs["type"] == "bush":
                obs_collision = obs["rect"].inflate(-8, -8)  # Bush has some transparent edges
            elif obs["type"] == "wood":
                obs_collision = obs["rect"].inflate(-5, -5)  # Wood is more solid
            elif obs["type"] == "stone":
                obs_collision = obs["rect"].inflate(-3, -3)  # Stone is most solid
            else:
                obs_collision = obs["rect"]
            
            if player_collision.colliderect(obs_collision):
                obstacles.remove(obs)
                lives -= 1
                if lives <= 0:
                    game_over = True

            elif obs["rect"].right < 0:
                obstacles.remove(obs)

        # Only spawn arrows and update counters after game starts
        if game_started:
            # Spawn flying arrows above the player (with spacing check to avoid obstacles)
            arrow_timer += 1
            if arrow_timer >= arrow_interval:
                # Check if enough time has passed since last obstacle spawn
                if last_obstacle_spawn >= min_spacing:
                    arrow_timer = 0
                    last_arrow_spawn = 0  # Reset counter for spacing
                    # Spawn arrow higher above the player level (flies horizontally above ground)
                    arrow_img = obstacle_images['arrow']
                    arrow_rect = pygame.Rect(WIDTH + 50, platform_y - 120, arrow_img.get_width(), arrow_img.get_height())
                    arrows.append({
                        "rect": arrow_rect,
                        "type": "arrow",
                        "image": arrow_img
                    })

            # Update spacing counters
            last_obstacle_spawn += 1
            last_arrow_spawn += 1

        # Move + draw arrows (always show existing arrows)
        for arrow in arrows[:]:
            arrow["rect"].x -= platform_speed * 1.5  # Arrows move faster
            # Draw the arrow
            screen.blit(arrow["image"], arrow["rect"])

            # Collision with arrows (when player jumps up and hits them)
            player_collision = player_rect.inflate(-25, -15)
            arrow_collision = arrow["rect"].inflate(-5, -3)  # Tight collision for arrows
            
            if player_collision.colliderect(arrow_collision):
                arrows.remove(arrow)
                lives -= 1
                if lives <= 0:
                    game_over = True

            elif arrow["rect"].right < 0:
                arrows.remove(arrow)

        # Draw lives with red text
        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))

    else:
        # Game Over Screen
        game_over_text = font.render("GAME OVER!", True, (139, 0, 0))  # Dark red
        restart_text = font.render("Press R to Restart or ESC to Quit", True, (0, 0, 0))  # Black text
        screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 40))
        screen.blit(restart_text, (WIDTH//2 - 200, HEIGHT//2))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
        elif keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            running = False

    pygame.display.update()

pygame.quit()
sys.exit()
