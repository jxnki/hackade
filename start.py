import pygame
import sys

pygame.init()

# Windowed screen setup
WIDTH, HEIGHT = 1280, 720  # Large window but not fullscreen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - Start Page")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
SKY_BLUE = (135, 206, 235)
BED_BROWN = (139, 69, 19)
BLANKET_RED = (255, 111, 97)
HEAD_COLOR = (253, 213, 177)
DARK_BLUE = (11, 61, 145)
DARK_BLUE_HOVER = (9, 47, 107)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont('Arial', 72)
button_font = pygame.font.SysFont('Arial', 48)

# Start button
button_width, button_height = 300, 80
button_rect = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 100, button_width, button_height)

# Cloud float variables
cloud_y = HEIGHT//2 - 200
cloud_direction = 1

def draw_gradient_cloud(surface, center, width, height):
    cloud_surface = pygame.Surface((width+100, height+50), pygame.SRCALPHA)
    for i in range(5):
        ellipse_width = width - i*20
        ellipse_height = height - i*15
        alpha = 255 - i*40
        pygame.draw.ellipse(cloud_surface, (255, 255, 255, alpha), 
                            (50 + i*10, 10 + i*5, ellipse_width, ellipse_height))
    surface.blit(cloud_surface, (center[0] - width//2 - 50, center[1] - height//2 - 25))

def draw_start_page():
    global cloud_y, cloud_direction

    screen.fill(SKY_BLUE)

    # Draw bed
    bed_rect = pygame.Rect(WIDTH//2 - 225, HEIGHT//2, 450, 75)
    pygame.draw.rect(screen, BED_BROWN, bed_rect, border_radius=10)

    # Draw person
    head_rect = pygame.Rect(WIDTH//2 - 35, HEIGHT//2 - 75, 70, 70)
    pygame.draw.ellipse(screen, HEAD_COLOR, head_rect)

    blanket_rect = pygame.Rect(WIDTH//2 - 55, HEIGHT//2 - 15, 110, 55)
    pygame.draw.rect(screen, BLANKET_RED, blanket_rect, border_radius=10)

    # Update cloud position for floating effect
    cloud_y += cloud_direction * 0.5
    if cloud_y > HEIGHT//2 - 180 or cloud_y < HEIGHT//2 - 220:
        cloud_direction *= -1

    # Draw dream cloud
    cloud_center = (WIDTH//2, int(cloud_y))
    draw_gradient_cloud(screen, cloud_center, 400, 180)

    # Draw Dream Dash text
    text_surface = font.render("Dream Dash", True, BLACK)
    text_rect = text_surface.get_rect(center=cloud_center)
    screen.blit(text_surface, text_rect)

    # Draw Start button
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, DARK_BLUE_HOVER, button_rect, border_radius=15)
    else:
        pygame.draw.rect(screen, DARK_BLUE, button_rect, border_radius=15)
    
    button_text = button_font.render("Start", True, WHITE)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

def start_game():
    print("Game Started!")
    # Replace with your actual game logic
    running_game = True
    while running_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0,0,0))
        pygame.display.flip()
        clock.tick(60)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                start_game()

    draw_start_page()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
