# car_ride.py
import pygame
    # removed unused sys import
import random
import time

def run_car_ride(lives, duration=25):
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Car Ride")

    # Load and position carpic.png banner (after WIDTH, HEIGHT are defined)
    try:
        banner_img = pygame.image.load("assets/carpic.png").convert_alpha()
        banner_width = 700
        banner_height = 700
        banner_img = pygame.transform.scale(banner_img, (banner_width, banner_height))
        banner_rect = banner_img.get_rect()
        banner_rect.centerx = WIDTH // 2
        banner_rect.top = 4
    except Exception:
        banner_img = None

    banner_start_time = pygame.time.get_ticks()
    pygame.init()
    # Load arrow sound
    pygame.mixer.init()
    arrow_sound = pygame.mixer.Sound("assets/audio/arrow.mp3")

    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Car Ride")

    clock = pygame.time.Clock()
    FPS = 60

    BG_COLOR = (132, 213, 167)
    PLATFORM_COLOR = (139, 69, 19)

    # Player
    player_img = pygame.image.load("assets/players/player1.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (60, 60))
    player_rect = player_img.get_rect(midbottom=(100, HEIGHT - 50))

    player_speed = 4
    player_mode = "run"

    font = pygame.font.Font(None, 36)
    RED = (255, 0, 0)
    collision_flash = 0

    # Car
    car_only_img = pygame.image.load("assets/car_only.png").convert_alpha()
    car_only_img = pygame.transform.scale(car_only_img, (300, 200))
    car_with_player_img = pygame.image.load("assets/car.png").convert_alpha()
    car_with_player_img = pygame.transform.scale(car_with_player_img, (300, 200))
    car_rect = car_only_img.get_rect(midbottom=(400, HEIGHT - 50))

    # Physics
    vel_y = 0
    car_vel_y = 0
    gravity = 1
    jump_power = 15

    # Obstacles
    obstacles = []
    obstacle_speed = 6
    spawn_timer = 0
    SPAWN_INTERVAL = 90

    arrow_img = pygame.image.load("assets/arrow.png").convert_alpha()
    arrow_img = pygame.transform.scale(arrow_img, (40, 20))

    def spawn_obstacle():
        min_height = 50
        max_height = HEIGHT - 100
        arrow_y = random.randint(min_height, max_height)
        rect = pygame.Rect(WIDTH + 50, arrow_y, 40, 20)
        obstacles.append({'rect': rect, 'type': 'arrow', 'hit_player': False})

    start_time = time.time()
    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        # --- Draw banner at top center (disappear after 3s) ---
        if banner_img:
            if pygame.time.get_ticks() - banner_start_time < 3000:
                screen.blit(banner_img, banner_rect)

        # End after duration
        if time.time() - start_time >= duration:
            return max(0, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return 0

        keys = pygame.key.get_pressed()

        if player_mode == "run":
            if keys[pygame.K_UP] and player_rect.bottom >= HEIGHT - 50:
                vel_y = -jump_power
            vel_y += gravity
            player_rect.y += vel_y
            if player_rect.bottom > HEIGHT - 50:
                player_rect.bottom = HEIGHT - 50
                vel_y = 0
            player_rect.x += player_speed

            pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))
            screen.blit(player_img, player_rect)
            screen.blit(car_only_img, car_rect)

            if player_rect.colliderect(car_rect) and vel_y != 0:
                player_mode = "car"
            elif player_rect.x > car_rect.right + 50:
                player_mode = "normal_run"

        elif player_mode == "car":
            if keys[pygame.K_UP]:
                car_vel_y = -8
            elif keys[pygame.K_DOWN]:
                car_vel_y = 8
            else:
                car_vel_y *= 0.8
            car_rect.y += car_vel_y
            if car_rect.top < 0:
                car_rect.top = 0
                car_vel_y = 0
            elif car_rect.bottom > HEIGHT - 50:
                car_rect.bottom = HEIGHT - 50
                car_vel_y = 0
            car_rect.centerx = WIDTH // 2

            pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))

            spawn_timer += 1
            if spawn_timer >= SPAWN_INTERVAL:
                spawn_timer = 0
                spawn_obstacle()

            for obstacle in obstacles[:]:
                obstacle['rect'].x -= obstacle_speed
                screen.blit(arrow_img, obstacle['rect'])
                if car_rect.colliderect(obstacle['rect']) and not obstacle['hit_player']:
                    car_collision_rect = car_rect.inflate(-100, -80)
                    arrow_collision_rect = obstacle['rect'].inflate(-20, -12)
                    if car_collision_rect.colliderect(arrow_collision_rect):
                        lives -= 1
                        obstacle['hit_player'] = True
                        collision_flash = 10
                        if lives <= 0:
                            return 0
                if obstacle['rect'].right < 0:
                    # Play arrow sound when arrow passes the car
                    if obstacle['type'] == 'arrow':
                        arrow_sound.play()
                    obstacles.remove(obstacle)

            if collision_flash > 0:
                flash_surface = pygame.Surface(car_rect.size)
                flash_surface.fill((255, 0, 0))
                flash_surface.set_alpha(100)
                screen.blit(car_with_player_img, car_rect)
                screen.blit(flash_surface, car_rect)
                collision_flash -= 1
            else:
                screen.blit(car_with_player_img, car_rect)

        elif player_mode == "normal_run":
            if keys[pygame.K_UP] and player_rect.bottom >= HEIGHT - 50:
                vel_y = -jump_power
            vel_y += gravity
            player_rect.y += vel_y
            if player_rect.bottom > HEIGHT - 50:
                player_rect.bottom = HEIGHT - 50
                vel_y = 0

            pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))
            screen.blit(player_img, player_rect)

            spawn_timer += 1
            if spawn_timer >= SPAWN_INTERVAL:
                spawn_timer = 0
                spawn_obstacle()

            for obstacle in obstacles[:]:
                obstacle['rect'].x -= obstacle_speed
                screen.blit(arrow_img, obstacle['rect'])
                if player_rect.colliderect(obstacle['rect']) and not obstacle['hit_player']:
                    obstacle['hit_player'] = True
                    player_rect.x -= 10
                    if player_rect.x < 0:
                        player_rect.x = 0
                if obstacle['rect'].right < 0:
                    obstacles.remove(obstacle)

        lives_text = font.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_text, (10, 10))
        pygame.display.flip()

