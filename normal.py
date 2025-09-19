import pygame
import sys
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - Runner Version")

clock = pygame.time.Clock()
FPS = 60

# Platform setup
platform_height = 50
platform_y = HEIGHT - platform_height
platform_scroll = 0
platform_width = 200
platform_speed = 5

# Load player animation frames
player_frames = []
num_frames = 4
for i in range(1, num_frames + 1):
    img = pygame.image.load(f"assets/players/player{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (100, 100))
    player_frames.append(img)

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

# Load obstacles
stone_img = pygame.image.load("assets/stone.png").convert_alpha()
stone_img = pygame.transform.scale(stone_img, (50, 50))
wood_img = pygame.image.load("assets/wood.png").convert_alpha()
wood_img = pygame.transform.scale(wood_img, (50, 50))

obstacles = []
obstacle_timer = 0
obstacle_interval = 90

# Lives
lives = 5
font = pygame.font.SysFont(None, 36)

# Game state
game_over = False

def reset_game():
    global lives, obstacles, player_rect, player_vel_y, game_over
    lives = 5
    obstacles = []
    player_rect.x = 100
    player_rect.y = platform_y - player_rect.height
    player_vel_y = 0
    game_over = False

running = True
while running:
    clock.tick(FPS)
    screen.fill((135, 206, 235))  # sky blue background

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC to quit
                running = False

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
            pygame.draw.rect(screen, (139, 69, 19),
                             (i * platform_width - platform_scroll, platform_y, platform_width, platform_height))

        # Animate player
        frame_counter += animation_speed
        if frame_counter >= len(player_frames):
            frame_counter = 0
        current_frame = int(frame_counter)
        player_img = player_frames[current_frame]

        # Draw player
        screen.blit(player_img, player_rect)

        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= obstacle_interval:
            obstacle_timer = 0
            obs_type = random.choice(["stone", "wood"])
            obs_img = stone_img if obs_type == "stone" else wood_img
            obs_rect = obs_img.get_rect()
            obs_rect.x = WIDTH + 50
            obs_rect.y = platform_y - obs_rect.height
            obstacles.append({"rect": obs_rect, "img": obs_img})

        # Move and draw obstacles
        for obs in obstacles[:]:
            obs["rect"].x -= platform_speed
            screen.blit(obs["img"], obs["rect"])


            # Improved collision: check rectangle overlap and center distance
            if player_rect.colliderect(obs["rect"]):
                player_center_x = player_rect.centerx
                player_center_y = player_rect.centery
                obs_center_x = obs["rect"].centerx
                obs_center_y = obs["rect"].centery

                distance_x = abs(player_center_x - obs_center_x)
                distance_y = abs(player_center_y - obs_center_y)

                min_distance_x = (player_rect.width + obs["rect"].width) // 2 - 10
                min_distance_y = (player_rect.height + obs["rect"].height) // 2 - 10

                if distance_x < min_distance_x and distance_y < min_distance_y:
                    obstacles.remove(obs)
                    lives -= 1
                    if lives <= 0:
                        game_over = True

            # Remove offscreen obstacles
            elif obs["rect"].right < 0:
                obstacles.remove(obs)

        # Draw lives
        lives_text = font.render(f"Lives: {lives}", True, (255, 0, 0))
        screen.blit(lives_text, (10, 10))

    else:
        # Game Over Screen
        game_over_text = font.render("GAME OVER!", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart or ESC to Quit", True, (0, 0, 0))
        screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 40))
        screen.blit(restart_text, (WIDTH//2 - 200, HEIGHT//2))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
        elif keys[pygame.K_q] or keys[pygame.K_ESCAPE]:
            running = False

    # Update display
    pygame.display.update()

pygame.quit()
sys.exit()
