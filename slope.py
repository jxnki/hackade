import pygame
import sys
import os
import random
import time
from transition import portal_transition  # kept import, not used here but harmless

def run_slope(lives, duration=15):
    pygame.init()
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Slope Platform Scene")
    clock = pygame.time.Clock()
    FPS = 60

    # --- Paths ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PLAYER_DIR = os.path.join(SCRIPT_DIR, "assets", "players")
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

    # --- Load jump sound ---
    pygame.mixer.init()
    jump_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "audio/jump.mp3"))
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

    # --- Create slope platform ---
    BROWN_COLOR = (139, 69, 19)
    slope_width = WIDTH * 6
    slope_height = 120
    platform_thickness = 60
    slope_x = 0
    slope_y = HEIGHT - platform_thickness

    # --- Obstacles setup ---
    obstacles = []
    obstacle_spawn_timer = 0
    obstacle_types = ['wood', 'stone', 'bush']

    def create_slope_points(x, y):
        mid_point = slope_width // 2
        return [
            (x, y),
            (x + mid_point, y - slope_height),
            (x + slope_width, HEIGHT),
            (x, HEIGHT),
        ]

    slope_points = create_slope_points(slope_x, slope_y)

    def get_slope_height_at_x(player_x, slope_x, slope_y):
        relative_x = player_x - slope_x
        if relative_x < 0 or relative_x > slope_width:
            return HEIGHT
        mid_point = slope_width // 2
        if relative_x <= mid_point:
            ascent_progress = relative_x / mid_point
            return slope_y - (slope_height * ascent_progress)
        else:
            descent_progress = (relative_x - mid_point) / mid_point
            peak_height = slope_y - slope_height
            return peak_height + (HEIGHT - peak_height) * descent_progress

    # --- Player setup ---
    player_rect = player_images[0].get_rect()
    player_x_pos = WIDTH // 3
    player_rect.centerx = player_x_pos
    player_rect.bottom = get_slope_height_at_x(player_x_pos, slope_x, slope_y)
    gravity = 0
    jump_power = 12
    on_ground = True

    # --- Speed variables ---
    base_speed = 5
    current_speed = base_speed
    max_speed = 12

    # --- Lives ---
    font = pygame.font.Font(None, 36)
    invulnerable_timer = 0
    invulnerable_duration = 60

    # --- Oval (special big visual) setup ---
    oval_active = False
    oval_rect = None
    # Oval size (big)
    OVAL_WIDTH = 260
    OVAL_HEIGHT = 160
    # Color for oval (you can tweak)
    OVAL_COLOR = (20, 20, 30)  # dark oval (visible against sky)

    start_time = time.time()

    running = True
    while running:
        clock.tick(FPS)

        # --- Timer & end-of-stage ---
        time_elapsed = time.time() - start_time
        if time_elapsed >= duration:
            return max(0, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground:
            gravity = jump_power
            on_ground = False

        if not on_ground:
            gravity -= 0.5
            player_rect.y -= gravity

        slope_height_at_player = get_slope_height_at_x(player_x_pos, slope_x, slope_y)
        if not on_ground and player_rect.bottom >= slope_height_at_player:
            player_rect.bottom = slope_height_at_player
            gravity = 0
            jump_sound.play()
            on_ground = True
        elif on_ground:
            player_rect.bottom = slope_height_at_player

        relative_x = player_x_pos - slope_x
        mid_point = slope_width // 2
        if 0 <= relative_x <= slope_width:
            if relative_x <= mid_point:
                current_speed = base_speed
            else:
                descent_progress = (relative_x - mid_point) / mid_point
                current_speed = base_speed + (max_speed - base_speed) * descent_progress
        else:
            current_speed = base_speed

        slope_x -= current_speed
        if slope_x + slope_width < 0:
            slope_x = 0
        slope_points = create_slope_points(slope_x, slope_y)

        obstacle_spawn_timer += 1
        if relative_x <= mid_point:
            dynamic_spawn_delay = 60
        else:
            dynamic_spawn_delay = 120
        if obstacle_spawn_timer >= dynamic_spawn_delay:
            obstacle_type = random.choice(obstacle_types)
            obstacle_img = obstacle_images[obstacle_type]
            obstacle_rect = obstacle_img.get_rect()
            obstacle_x = WIDTH + 50
            obstacle_slope_height = get_slope_height_at_x(obstacle_x, slope_x, slope_y)
            obstacle_rect.midbottom = (obstacle_x, obstacle_slope_height)
            obstacles.append({'type': obstacle_type, 'rect': obstacle_rect, 'image': obstacle_img})
            obstacle_spawn_timer = 0

        for obstacle in obstacles[:]:
            obstacle['rect'].x -= current_speed
            obstacle['rect'].bottom = get_slope_height_at_x(obstacle['rect'].centerx, slope_x, slope_y)
            if obstacle['rect'].right < 0:
                obstacles.remove(obstacle)

        # --- Oval spawn at duration - 2 seconds (e.g. 23s) ---
        # Spawn only once
        if (not oval_active) and (time_elapsed >= max(0, duration - 2)):
            # Start slightly off-screen to the right so it scrolls in
            spawn_x = WIDTH + 50
            spawn_midbottom_y = get_slope_height_at_x(spawn_x, slope_x, slope_y)
            oval_rect = pygame.Rect(0, 0, OVAL_WIDTH, OVAL_HEIGHT)
            oval_rect.midbottom = (spawn_x, spawn_midbottom_y)
            oval_active = True

        # Move oval like other obstacles (if active)
        if oval_active and oval_rect:
            oval_rect.x -= int(current_speed)  # move left at current_speed
            # Update vertical position so it follows slope surface
            oval_rect.bottom = get_slope_height_at_x(oval_rect.centerx, slope_x, slope_y)
            # Remove if fully off left edge
            if oval_rect.right < 0:
                oval_active = False
                oval_rect = None

        # --- Collision / lives (unchanged) ---
        if invulnerable_timer <= 0:
            for obstacle in obstacles[:]:
                if player_rect.colliderect(obstacle['rect']):
                    lives -= 1
                    invulnerable_timer = invulnerable_duration
                    obstacles.remove(obstacle)
                    break

        if invulnerable_timer > 0:
            invulnerable_timer -= 1

        if lives <= 0:
            return 0

        anim_timer += ANIM_SPEED
        if anim_timer >= len(player_images):
            anim_timer = 0
        player_index = int(anim_timer)

        # --- Draw ---
        screen.fill((135, 206, 250))
        pygame.draw.polygon(screen, BROWN_COLOR, slope_points)

        for obstacle in obstacles:
            screen.blit(obstacle['image'], obstacle['rect'])

        # Draw the oval (above obstacles so it's noticeable)
        if oval_active and oval_rect:
            # Draw filled ellipse
            pygame.draw.ellipse(screen, OVAL_COLOR, oval_rect)
            # Optional: draw a thin outline for visibility
            pygame.draw.ellipse(screen, (0, 0, 0), oval_rect, 3)

        if invulnerable_timer <= 0 or invulnerable_timer % 10 < 5:
            screen.blit(player_images[player_index], player_rect)
        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))

        pygame.display.flip()

    return max(0, lives)
