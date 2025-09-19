import pygame
import sys
import random
import time
from transition import portal_transition  # NEW


def run_normal(lives, duration=25):
    pygame.init()
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Runner Version")

    clock = pygame.time.Clock()
    FPS = 60

    # Platform
    platform_height = 50
    platform_y = HEIGHT - platform_height
    platform_scroll = 0
    platform_width = 200
    platform_speed = 5

    # Player animation frames
    player_frames = []
    for i in range(1, 5):
        img = pygame.image.load(f"assets/players/player{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (100, 100))
        player_frames.append(img)

    player_rect = player_frames[0].get_rect()
    player_rect.x = 100
    player_rect.y = platform_y - player_rect.height

    frame_counter = 0
    animation_speed = 0.2

    # Physics
    player_vel_y = 0
    gravity = 1
    jump_strength = 17

    # Obstacles
    stone_img = pygame.transform.scale(pygame.image.load("assets/stone.png").convert_alpha(), (50, 50))
    wood_img = pygame.transform.scale(pygame.image.load("assets/wood.png").convert_alpha(), (50, 50))
    obstacles = []
    obstacle_timer = 0
    obstacle_interval = 90

    # Font
    font = pygame.font.SysFont(None, 36)

    # Timer
    start_time = time.time()

    # --- Load portal frames once ---
    portal_frames = [
        pygame.image.load(f"assets/portal/portal{i}.png").convert_alpha()
        for i in range(1, 6)
    ]
    portal_index = 0
    portal_anim_speed = 0.15
    portal_counter = 0

    # Portal position (fixed near right edge above platform)
    portal_x = WIDTH - 100
    portal_y = platform_y - 120

    running = True
    while running:
        clock.tick(FPS)
        screen.fill((135, 206, 235))  # sky blue background

        # End after duration
        if time.time() - start_time >= duration:
            if lives > 0:
                # Trigger portal transition at portal location
                portal_rect = portal_frames[int(portal_index)].get_rect(center=(portal_x, portal_y))
                portal_transition(screen, player_rect, player_frames[int(frame_counter)], portal_frames,
                                  duration=1.5, blackout_ms=300)
            return max(0, lives)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0

        # Jump
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and player_rect.bottom >= platform_y:
            player_vel_y = -jump_strength

        # Gravity
        player_vel_y += gravity
        player_rect.y += player_vel_y
        if player_rect.bottom >= platform_y:
            player_rect.bottom = platform_y
            player_vel_y = 0

        # Scroll platforms
        platform_scroll += platform_speed
        if platform_scroll >= platform_width:
            platform_scroll = 0

        for i in range(-1, WIDTH // platform_width + 2):
            pygame.draw.rect(screen, (139, 69, 19),
                             (i * platform_width - platform_scroll, platform_y,
                              platform_width, platform_height))

        # Animate player
        frame_counter += animation_speed
        if frame_counter >= len(player_frames):
            frame_counter = 0
        player_img = player_frames[int(frame_counter)]
        screen.blit(player_img, player_rect)

        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= obstacle_interval:
            obstacle_timer = 0
            obs_img = random.choice([stone_img, wood_img])
            obs_rect = obs_img.get_rect()
            obs_rect.x = WIDTH + 50
            obs_rect.y = platform_y - obs_rect.height
            obstacles.append({
                "rect": obs_rect,
                "img": obs_img,
                "type": "stone" if obs_img == stone_img else "wood"
            })

        # Move & draw obstacles
        for obs in obstacles[:]:
            obs["rect"].x -= platform_speed
            screen.blit(obs["img"], obs["rect"])

            # --- Refined collision detection ---
            if player_rect.colliderect(obs["rect"]):
                # Shrink player hitbox more
                player_hitbox = player_rect.inflate(-25, -20)

                # Type-based obstacle adjustment
                if obs["type"] == "stone":
                    obs_hitbox = obs["rect"].inflate(-8, -8)
                elif obs["type"] == "wood":
                    obs_hitbox = obs["rect"].inflate(-10, -10)
                else:
                    obs_hitbox = obs["rect"]

                # Check refined overlap
                if player_hitbox.colliderect(obs_hitbox):
                    # Extra center distance check
                    px, py = player_rect.center
                    ox, oy = obs["rect"].center
                    dx = abs(px - ox)
                    dy = abs(py - oy)
                    min_dx = (player_rect.width + obs["rect"].width) // 2 - 15
                    min_dy = (player_rect.height + obs["rect"].height) // 2 - 15

                    if dx < min_dx and dy < min_dy:
                        obstacles.remove(obs)
                        lives -= 1
                        if lives <= 0:
                            return 0
            elif obs["rect"].right < 0:
                obstacles.remove(obs)

        # --- Animate & draw portal (always visible at right edge) ---
        portal_counter += portal_anim_speed
        if portal_counter >= len(portal_frames):
            portal_counter = 0
        portal_img = portal_frames[int(portal_counter)]
        portal_rect = portal_img.get_rect(center=(portal_x, portal_y))
        screen.blit(portal_img, portal_rect)

        # Lives
        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))

        pygame.display.update()
