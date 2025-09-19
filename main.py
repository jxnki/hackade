import pygame
import os
from ui import UIManager
from player import Player
from obstacle import ObstacleManager  # your obstacle logic

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dream Dash Combined Demo")
clock = pygame.time.Clock()

# Initialize UI
ui = UIManager()

# Initialize player above platform
platform_rect = pygame.Rect(100, 500, 600, 40)
player = Player(150, 460, platform_rect)  # starting on platform

# Initialize obstacles
obstacle_manager = ObstacleManager()

# Optionally load player image (fallback if Player class uses rects)
player_img_path = os.path.join("assets", "players", "player1.png")
if os.path.exists(player_img_path):
    player_img = pygame.image.load(player_img_path)
else:
    player_img = None  # will draw a rect instead

# Platform class for multiple platforms
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (50, 150, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Create platforms (ground + extra if needed)
platforms = [Platform(0, 550, 800, 50)]

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle player input
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()

    # Update obstacles
    obstacle_manager.update()

    # Fill background
    screen.fill((132, 213, 167))  # soft greenish background

    # Draw platforms
    for plat in platforms:
        plat.draw(screen)

    # Draw obstacles
    obstacle_manager.draw(screen)

    # Draw player
    if player_img:
        screen.blit(player_img, (player.rect.x, player.rect.y))
    else:
        pygame.draw.rect(screen, (255, 0, 0), player.rect)  # fallback red rectangle

    # Update and draw UI
    ui.update(player)
    ui.draw(screen)

    # Refresh display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
