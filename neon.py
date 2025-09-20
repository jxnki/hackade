import pygame
import sys
import random
import os
import time
from transition import portal_transition

def run_neon(lives, duration=25):
    pygame.init()

    # Screen setup
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Full Neon Mode")

    clock = pygame.time.Clock()
    FPS = 60

    # --- Paths ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

    # Load and position neon.png banner (after WIDTH, HEIGHT, ASSETS_DIR are defined)
    try:
        banner_img = pygame.image.load(os.path.join(ASSETS_DIR, "neon.png")).convert_alpha()
        banner_width = 700
        banner_height = 700
        banner_img = pygame.transform.scale(banner_img, (banner_width, banner_height))
        banner_rect = banner_img.get_rect()
        banner_rect.centerx = WIDTH // 2
        banner_rect.top = 4
    except Exception:
        banner_img = None

    banner_start_time = pygame.time.get_ticks()

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
    obstacle_types = ['wood', 'stone', 'bush']

    # Platform setup
    platform_height = 50
    platform_y = HEIGHT - platform_height
    platform_scroll = 0
    platform_width = 200
    platform_speed = 5

    # Player setup (always neon cyan)
    player_frames = []
    num_frames = 4
    CYAN = (0, 255, 255)  # neon cyan fixed

    for i in range(1, num_frames + 1):
        img = pygame.image.load(os.path.join(ASSETS_DIR, f"players/player{i}.png")).convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
        tinted_img = img.copy()
        tinted_img.fill(CYAN + (0,), special_flags=pygame.BLEND_RGB_MULT)
        player_frames.append(tinted_img)

    player_rect = player_frames[0].get_rect()
    player_rect.x = 100
    player_rect.y = platform_y - player_rect.height

    # Animation variables
    current_frame = 0
    frame_counter = 0
    animation_speed = 0.2

    # Player physics
    player_vel_y = 0
    gravity = 1
    jump_strength = 17

    # Obstacles
    obstacles = []
    obstacle_timer = 0
    obstacle_interval = 90

    # Font
    font = pygame.font.SysFont(None, 36)

    # Neon colors (exclude cyan since player is cyan)
    neon_colors = [
        (255, 20, 147),   # neon pink
        (57, 255, 20),    # neon green
        (255, 140, 0),    # neon orange
        (138, 43, 226),   # neon purple
        (255, 255, 0),    # neon yellow
    ]

    bg_color = random.choice(neon_colors)
    platform_color = random.choice([c for c in neon_colors if c != bg_color])
    color_timer = 0
    color_interval = 30  # ~0.5 sec

    start_time = time.time()
    game_over = False

    running = True
    while running:
        clock.tick(FPS)

        # End after duration
        if time.time() - start_time >= duration:
            return max(0, lives)

        # --- Neon background/platform flicker ---
        color_timer += 1
        if color_timer >= color_interval:
            color_timer = 0
            new_bg = random.choice(neon_colors)
            while new_bg == bg_color:
                new_bg = random.choice(neon_colors)
            bg_color = new_bg
            platform_color = random.choice([c for c in neon_colors if c != bg_color])

        screen.fill(bg_color)

        # --- Draw banner at top center (disappear after 3s) ---
        if banner_img:
            if pygame.time.get_ticks() - banner_start_time < 3000:
                screen.blit(banner_img, banner_rect)

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0

        if not game_over:
            # Player jump
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player_rect.bottom >= platform_y:
                player_vel_y = -jump_strength

            # Gravity
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

            # Draw scrolling platforms
            for i in range(-1, WIDTH // platform_width + 2):
                pygame.draw.rect(screen, platform_color,
                                 (i * platform_width - platform_scroll, platform_y, platform_width, platform_height))

            # Animate player
            frame_counter += animation_speed
            if frame_counter >= len(player_frames):
                frame_counter = 0
            current_frame = int(frame_counter)
            player_img = player_frames[current_frame]
            screen.blit(player_img, player_rect)

            # Spawn obstacles
            obstacle_timer += 1
            if obstacle_timer >= obstacle_interval:
                obstacle_timer = 0
                obstacle_type = random.choice(obstacle_types)
                obstacle_img = obstacle_images[obstacle_type]
                obs_rect = pygame.Rect(WIDTH + 50, platform_y - obstacle_img.get_height(),
                                       obstacle_img.get_width(), obstacle_img.get_height())
                obstacles.append({"rect": obs_rect, "type": obstacle_type, "image": obstacle_img})

            # Move + draw obstacles
            for obs in obstacles[:]:
                obs["rect"].x -= platform_speed
                screen.blit(obs["image"], obs["rect"])

                # Collision
                player_collision = player_rect.inflate(-30, -20)
                if obs["type"] == "bush":
                    obs_collision = obs["rect"].inflate(-8, -8)
                elif obs["type"] == "wood":
                    obs_collision = obs["rect"].inflate(-5, -5)
                elif obs["type"] == "stone":
                    obs_collision = obs["rect"].inflate(-3, -3)
                else:
                    obs_collision = obs["rect"]

                if player_collision.colliderect(obs_collision):
                    obstacles.remove(obs)
                    lives -= 1
                    if lives <= 0:
                        return 0
                elif obs["rect"].right < 0:
                    obstacles.remove(obs)

            # Draw lives
            lives_text = font.render(f"Lives: {lives}", True, (0, 0, 0))
            screen.blit(lives_text, (10, 10))

        pygame.display.update()

    return max(0, lives)
