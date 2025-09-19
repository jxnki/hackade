import pygame
import sys
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - Car Ride")

clock = pygame.time.Clock()
FPS = 60

# Colors
BG_COLOR = (132, 213, 167)  # soft greenish background (same as other files)
PLATFORM_COLOR = (139, 69, 19)  # brown platform
ROCK_COLOR = (120, 120, 120)

# Player setup
player_img = pygame.image.load("assets/players/player1.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 60))
player_rect = player_img.get_rect(midbottom=(100, HEIGHT - 50))

player_speed = 4
player_mode = "run"  # can be "run" or "car"

# Lives system
lives = 5
font = pygame.font.Font(None, 36)
RED = (255, 0, 0)
collision_flash = 0  # For visual feedback when collision happens

# Car setup
car_only_img = pygame.image.load("assets/car_only.png").convert_alpha()
car_only_img = pygame.transform.scale(car_only_img, (300, 200))  # Extra large for better visibility
car_with_player_img = pygame.image.load("assets/car.png").convert_alpha()
car_with_player_img = pygame.transform.scale(car_with_player_img, (300, 200))  # Extra large for better visibility
car_rect = car_only_img.get_rect(midbottom=(400, HEIGHT - 50))

# Physics
vel_y = 0
car_vel_y = 0  # Car's vertical velocity
gravity = 1
jump_power = 15

# Obstacles (using actual images)
obstacles = []
obstacle_speed = 6
spawn_timer = 0
SPAWN_INTERVAL = 90

# Load obstacle images - flying arrows only
arrow_img = None
try:
    arrow_img = pygame.image.load("assets/arrow.png").convert_alpha()
    arrow_img = pygame.transform.scale(arrow_img, (40, 20))  # Smaller arrows
except pygame.error:
    arrow_img = None

def spawn_obstacle():
    # Spawn flying arrows at random heights
    min_height = 50  # Minimum height above ground
    max_height = HEIGHT - 100  # Maximum height (leave some space from top)
    arrow_y = random.randint(min_height, max_height)
    rect = pygame.Rect(WIDTH + 50, arrow_y, 40, 20)  # Smaller arrow size
    obstacles.append({'rect': rect, 'type': 'arrow', 'hit_player': False})

running = True
while running:
    clock.tick(FPS)
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and lives <= 0:
                running = False

    keys = pygame.key.get_pressed()
    
    # Don't process game logic if game over
    if lives <= 0:
        # Black screen for game over
        screen.fill((0, 0, 0))  # Black background
        
        # Display lives counter in red
        lives_text = font.render(f"Lives: {lives}", True, RED)
        screen.blit(lives_text, (10, 10))
        
        # Game over message
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - 150, HEIGHT//2))
        
        pygame.display.flip()
        continue

    if player_mode == "run":
        # Handle jumping with UP arrow key
        if keys[pygame.K_UP] and player_rect.bottom >= HEIGHT - 50:
            vel_y = -jump_power
        
        # Apply gravity
        vel_y += gravity
        player_rect.y += vel_y
        
        # Keep player on ground
        if player_rect.bottom > HEIGHT - 50:
            player_rect.bottom = HEIGHT - 50
            vel_y = 0
        
        # Player moves towards car
        player_rect.x += player_speed

        # Draw ground
        pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))

        # Draw player
        screen.blit(player_img, player_rect)

        # Draw empty car (before player enters)
        screen.blit(car_only_img, car_rect)

        # Check collision → enter car (only when jumping)
        if (player_rect.colliderect(car_rect) and 
            vel_y != 0):  # Player must be jumping (not on ground)
            player_mode = "car"
        
        # If player passes the car without entering, switch to normal running mode
        elif player_rect.x > car_rect.right + 50:
            player_mode = "normal_run"

    elif player_mode == "car":
        # Car can move up and down with arrow keys
        if keys[pygame.K_UP]:
            car_vel_y = -8  # Move up
        elif keys[pygame.K_DOWN]:
            car_vel_y = 8   # Move down
        else:
            car_vel_y *= 0.8  # Gradual deceleration when no key pressed
        
        # Apply movement (only vertical)
        car_rect.y += car_vel_y
        
        # Keep car within screen bounds
        if car_rect.top < 0:
            car_rect.top = 0
            car_vel_y = 0
        elif car_rect.bottom > HEIGHT - 50:  # Allow car to land on platform surface
            car_rect.bottom = HEIGHT - 50
            car_vel_y = 0
        
        # Keep car centered horizontally
        car_rect.centerx = WIDTH // 2
        
        # Keep car within screen bounds
        if car_rect.x > WIDTH - car_rect.width:
            car_rect.x = WIDTH - car_rect.width

        # Keep player hidden (inside car)
        # Ground
        pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))

        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            spawn_obstacle()

        # Move + draw obstacles (normal speed since car is stationary)
        for obstacle in obstacles[:]:
            obstacle['rect'].x -= obstacle_speed  # Normal obstacle movement speed
            
            # Draw arrow image or fallback rectangle
            if arrow_img:
                screen.blit(arrow_img, obstacle['rect'])
            else:
                pygame.draw.rect(screen, (255, 0, 0), obstacle['rect'])  # Red fallback for arrows

            # Car collision with obstacles (very precise collision detection)
            if car_rect.colliderect(obstacle['rect']) and not obstacle['hit_player']:
                # Create much smaller collision rectangles for very precise detection
                car_collision_rect = car_rect.inflate(-100, -80)  # Much smaller car hitbox
                arrow_collision_rect = obstacle['rect'].inflate(-20, -12)  # Much smaller arrow hitbox
                
                # Only decrease lives if the smaller rectangles actually collide
                if car_collision_rect.colliderect(arrow_collision_rect):
                    lives -= 1
                    obstacle['hit_player'] = True  # Prevent multiple hits from same obstacle
                    collision_flash = 10  # Flash effect for 10 frames

            if obstacle['rect'].right < 0:
                obstacles.remove(obstacle)

        # Draw car with player inside (with collision flash effect)
        if collision_flash > 0:
            # Flash red when collision happens
            flash_surface = pygame.Surface(car_rect.size)
            flash_surface.fill((255, 0, 0))
            flash_surface.set_alpha(100)
            screen.blit(car_with_player_img, car_rect)
            screen.blit(flash_surface, car_rect)
            collision_flash -= 1
        else:
            screen.blit(car_with_player_img, car_rect)

    elif player_mode == "normal_run":
        # Normal platformer mode - player faces obstacles
        
        # Handle jumping with UP arrow key
        if keys[pygame.K_UP] and player_rect.bottom >= HEIGHT - 50:
            vel_y = -jump_power
        
        # Apply gravity
        vel_y += gravity
        player_rect.y += vel_y
        
        # Keep player on ground
        if player_rect.bottom > HEIGHT - 50:
            player_rect.bottom = HEIGHT - 50
            vel_y = 0
        
        # Draw ground
        pygame.draw.rect(screen, PLATFORM_COLOR, (0, HEIGHT - 50, WIDTH, 50))
        
        # Draw player
        screen.blit(player_img, player_rect)
        
        # Spawn obstacles
        spawn_timer += 1
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            spawn_obstacle()

        # Move + draw obstacles  
        for obstacle in obstacles[:]:
            obstacle['rect'].x -= obstacle_speed
            
            # Draw arrow image or fallback rectangle
            if arrow_img:
                screen.blit(arrow_img, obstacle['rect'])
            else:
                pygame.draw.rect(screen, (255, 0, 0), obstacle['rect'])  # Red fallback for arrows

            # Player collision with obstacle (bounce back only, no life loss)
            if player_rect.colliderect(obstacle['rect']) and not obstacle['hit_player']:
                # Mark as hit to prevent multiple interactions
                obstacle['hit_player'] = True
                
                # Player bounces back slightly
                player_rect.x -= 10
                if player_rect.x < 0:
                    player_rect.x = 0

            if obstacle['rect'].right < 0:
                obstacles.remove(obstacle)

    # Display lives counter in red (only if game is still active)
    lives_text = font.render(f"Lives: {lives}", True, RED)
    screen.blit(lives_text, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
