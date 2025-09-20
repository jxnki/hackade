import pygame
import sys
import os
import random
import time
from transition import portal_transition


def run_control_shift(lives, duration=25):
    """
    Ceiling-walking stage. Accepts current lives, runs for `duration` seconds (unless lives drop to 0),
    and returns remaining lives (or 0 if game over).
    """

    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ceiling-Walking Platformer")
    clock = pygame.time.Clock()
    FPS = 60

    # --- Paths ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PLAYER_DIR = os.path.join(SCRIPT_DIR, "assets", "players")
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

    # --- Load obstacle images (upside down for ceiling) ---
    obstacle_images = {
        'wood': pygame.transform.scale(
            pygame.transform.flip(
                pygame.image.load(os.path.join(ASSETS_DIR, "wood.png")).convert_alpha(),
                False, True
            ),
            (40, 40)
        ),
        'stone': pygame.transform.scale(
            pygame.transform.flip(
                pygame.image.load(os.path.join(ASSETS_DIR, "stone.png")).convert_alpha(),
                False, True
            ),
            (50, 50)
        ),
        'bush': pygame.transform.scale(
            pygame.transform.flip(
                pygame.image.load(os.path.join(ASSETS_DIR, "bush.png")).convert_alpha(),
                False, True
            ),
            (40, 40)
        )
    }

    # --- Load and flip player images ---
    player_images = [
        pygame.transform.scale(
            pygame.transform.flip(
                pygame.image.load(os.path.join(PLAYER_DIR, f"player{i}.png")).convert_alpha(),
                False, True
            ),
            (80, 80)
        )
        for i in range(1, 5)
    ]

    player_index = 0
    ANIM_SPEED = 0.15
    anim_timer = 0

    # --- Create brown rectangle platforms ---
    PLATFORM_HEIGHT = 80
    BROWN_COLOR = (139, 69, 19)  # Saddle brown color

    # Top platform (ceiling)
    top_platform_rect = pygame.Rect(0, 0, WIDTH, PLATFORM_HEIGHT)
    # Bottom platform (floor)
    bottom_platform_rect = pygame.Rect(0, HEIGHT - PLATFORM_HEIGHT, WIDTH, PLATFORM_HEIGHT)

    # --- Player setup ---
    player_rect = player_images[0].get_rect()
    player_rect.midtop = (WIDTH // 2, top_platform_rect.bottom)
    background_scroll = 0
    scroll_speed = 2
    gravity = 0
    jump_power = 12
    on_ceiling = True
    on_floor = False

    # --- Lives / invulnerability ---
    font = pygame.font.Font(None, 36)
    invulnerable_timer = 0
    invulnerable_duration = 60  # frames (approx 1s @ 60fps)

    # --- Obstacles setup ---
    obstacles = []
    obstacle_spawn_timer = 0
    obstacle_spawn_delay = 120  # spawn every 2 seconds @ 60 FPS
    obstacle_types = ['wood', 'stone', 'bush']

    start_time = time.time()

    # Load and position remo.png banner
    try:
        banner_img = pygame.image.load(os.path.join(ASSETS_DIR, "remo.png")).convert_alpha()
        banner_width = 300
        banner_height = 300
        banner_img = pygame.transform.scale(banner_img, (banner_width, banner_height))
        banner_rect = banner_img.get_rect()
        banner_rect.center = (WIDTH // 2, HEIGHT // 2)
    except Exception:
        banner_img = None

    banner_start_time = pygame.time.get_ticks()
    running = True
    while running:
        clock.tick(FPS)

        # End stage after duration elapsed
        if time.time() - start_time >= duration:
            return max(0, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # return 0 to indicate quit/stop to the manager
                return 0

        # --- Scrolling background (keeps looping, aesthetic only) ---
        background_scroll -= scroll_speed
        if background_scroll <= -WIDTH:
            background_scroll = 0

        # Keep player centered horizontally
        player_rect.centerx = WIDTH // 2

        # --- Spawn obstacles hanging from ceiling ---
        obstacle_spawn_timer += 1
        if obstacle_spawn_timer >= obstacle_spawn_delay:
            obstacle_type = random.choice(obstacle_types)
            obstacle_img = obstacle_images[obstacle_type]
            obstacle_rect = obstacle_img.get_rect()
            obstacle_rect.midtop = (WIDTH + 50, top_platform_rect.bottom)
            obstacles.append({'type': obstacle_type, 'rect': obstacle_rect, 'image': obstacle_img})
            obstacle_spawn_timer = 0

        # --- Move obstacles left ---
        for obstacle in obstacles[:]:
            obstacle['rect'].x -= scroll_speed * 2
            if obstacle['rect'].right < 0:
                obstacles.remove(obstacle)

        # --- Collision detection with invulnerability and refined check ---
        if invulnerable_timer <= 0:
            for obstacle in obstacles[:]:
                if player_rect.colliderect(obstacle['rect']):
                    # additional center-based check to avoid false positives
                    player_cx, player_cy = player_rect.center
                    obs_cx, obs_cy = obstacle['rect'].center
                    dx = abs(player_cx - obs_cx)
                    dy = abs(player_cy - obs_cy)
                    min_dx = (player_rect.width + obstacle['rect'].width) // 2 - 10
                    min_dy = (player_rect.height + obstacle['rect'].height) // 2 - 10
                    if dx < min_dx and dy < min_dy:
                        lives -= 1
                        invulnerable_timer = invulnerable_duration
                        obstacles.remove(obstacle)
                        break

        # Update invulnerability timer
        if invulnerable_timer > 0:
            invulnerable_timer -= 1

        # --- Check game over ---
        if lives <= 0:
            # Return 0 to indicate game over in this stage
            return 0

        # --- Input: inverted jump using DOWN key ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            if on_ceiling and gravity == 0:
                gravity = jump_power
                on_ceiling = False

        # Apply inverted gravity if mid-air
        if not on_ceiling and not on_floor:
            gravity -= 0.6
            player_rect.y += gravity

        # Ceiling collision
        if player_rect.top <= top_platform_rect.bottom and gravity < 0:
            player_rect.top = top_platform_rect.bottom
            gravity = 0
            on_ceiling = True
            on_floor = False

        # Floor collision
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

        # --- Drawing ---
        screen.fill((135, 206, 250))  # sky blue

        # --- Draw banner at center (disappear after 3s) ---
        if banner_img:
            if pygame.time.get_ticks() - banner_start_time < 3000:
                screen.blit(banner_img, banner_rect)

        # Platforms
        pygame.draw.rect(screen, BROWN_COLOR, top_platform_rect)
        pygame.draw.rect(screen, BROWN_COLOR, bottom_platform_rect)

        # Draw obstacles
        for obstacle in obstacles:
            screen.blit(obstacle['image'], obstacle['rect'])

        # Draw player with invulnerability flash
        if invulnerable_timer <= 0 or (invulnerable_timer % 10) < 5:
            screen.blit(player_images[player_index], player_rect)

        # Lives counter
        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))

        pygame.display.flip()

    # Fallback return (shouldn't reach here)
    return max(0, lives)
