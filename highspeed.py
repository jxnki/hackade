# highspeed.py
import pygame
import sys
import random
import os
import time

def run_highspeed(lives, duration=25):
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - High Speed Runner")

    clock = pygame.time.Clock()
    FPS = 60

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

    obstacle_images = {
        'wood': pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "wood.png")).convert_alpha(), (50, 50)),
        'stone': pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "stone.png")).convert_alpha(), (55, 55)),
        'bush': pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "bush.png")).convert_alpha(), (45, 45)),
        'arrow': pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, "arrow.png")).convert_alpha(), (60, 30))
    }
    obstacle_types = ['wood', 'stone', 'bush']

    platform_height = 50
    platform_y = HEIGHT - platform_height
    platform_scroll = 0
    platform_width = 200
    platform_speed = 8
    speed_increase = 0.01

    player_frames = []
    for i in range(1, 5):
        img = pygame.image.load(f"assets/players/player{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (80, 80))
        player_frames.append(img)

    player_rect = player_frames[0].get_rect()
    player_rect.x = 100
    player_rect.y = platform_y - player_rect.height

    current_frame = 0
    frame_counter = 0
    animation_speed = 0.25

    player_vel_y = 0
    gravity = 1
    jump_strength = 18

    obstacles = []
    obstacle_timer = 0
    obstacle_interval = 70
    arrows = []
    arrow_timer = 0
    arrow_interval = 120
    last_obstacle_spawn = 0
    last_arrow_spawn = 0
    min_spacing = 60

    font = pygame.font.SysFont(None, 36)

    caution_img = pygame.image.load(os.path.join(ASSETS_DIR, "caution.png")).convert_alpha()
    caution_img = pygame.transform.scale(caution_img, (350, 250))

    game_started = False
    caution_timer = 0
    caution_display_time = 90

    start_time = time.time()
    running = True
    while running:
        clock.tick(FPS)
        screen.fill((132, 213, 167))

        if time.time() - start_time >= duration:
            return max(0, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0

        if not game_started:
            caution_timer += 1
            if caution_timer >= caution_display_time:
                game_started = True

        if game_started:
            platform_speed += speed_increase
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and player_rect.bottom >= platform_y:
                player_vel_y = -jump_strength

            player_vel_y += gravity
            player_rect.y += player_vel_y
            if player_rect.bottom >= platform_y and player_vel_y >= 0:
                player_rect.bottom = platform_y
                player_vel_y = 0
            platform_scroll += platform_speed
            if platform_scroll >= platform_width:
                platform_scroll = 0
        else:
            if player_rect.bottom >= platform_y:
                player_rect.bottom = platform_y
                player_vel_y = 0

        for i in range(-1, WIDTH // platform_width + 2):
            pygame.draw.rect(screen, (139, 69, 19),
                             (i * platform_width - platform_scroll, platform_y, platform_width, platform_height))

        frame_counter += animation_speed
        if frame_counter >= len(player_frames):
            frame_counter = 0
        current_frame = int(frame_counter)
        screen.blit(player_frames[current_frame], player_rect)

        if not game_started:
            caution_rect = caution_img.get_rect(center=(WIDTH//2, platform_y - 120))
            screen.blit(caution_img, caution_rect)

        if game_started:
            obstacle_timer += 1
            if obstacle_timer >= obstacle_interval and last_arrow_spawn >= min_spacing:
                obstacle_timer = 0
                last_obstacle_spawn = 0
                obstacle_type = random.choice(obstacle_types)
                obs_img = obstacle_images[obstacle_type]
                obs_size = obs_img.get_width()
                obs_rect = pygame.Rect(WIDTH + 50, platform_y - obs_size, obs_size, obs_size)
                obstacles.append({"rect": obs_rect, "type": obstacle_type, "image": obs_img})

        for obs in obstacles[:]:
            obs["rect"].x -= platform_speed
            screen.blit(obs["image"], obs["rect"])
            player_collision = player_rect.inflate(-25, -15)
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

        if game_started:
            arrow_timer += 1
            if arrow_timer >= arrow_interval and last_obstacle_spawn >= min_spacing:
                arrow_timer = 0
                last_arrow_spawn = 0
                arrow_img = obstacle_images['arrow']
                arrow_rect = pygame.Rect(WIDTH + 50, platform_y - 120, arrow_img.get_width(), arrow_img.get_height())
                arrows.append({"rect": arrow_rect, "type": "arrow", "image": arrow_img})

            last_obstacle_spawn += 1
            last_arrow_spawn += 1

        for arrow in arrows[:]:
            arrow["rect"].x -= platform_speed * 1.5
            screen.blit(arrow["image"], arrow["rect"])
            player_collision = player_rect.inflate(-25, -15)
            arrow_collision = arrow["rect"].inflate(-5, -3)
            if player_collision.colliderect(arrow_collision):
                arrows.remove(arrow)
                lives -= 1
                if lives <= 0:
                    return 0
            elif arrow["rect"].right < 0:
                arrows.remove(arrow)

        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))
        pygame.display.update()
