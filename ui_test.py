import pygame
import os
from ui import UIManager

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dream Dash UI Demo")
clock = pygame.time.Clock()

# Initialize UI
ui = UIManager()

# Dummy player object for testing
class DummyPlayer:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)  # x, y, width, height

player = DummyPlayer(100, 500)

# Platform class
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (50, 150, 50)  # green

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Create a single platform (ground)
platforms = [Platform(0, 550, 800, 50)]

# Load player image (static)
player_img = pygame.image.load(os.path.join("assets", "players", "player1.png"))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background
    screen.fill((132, 213, 167))  # white

    # Draw platform(s)
    for plat in platforms:
        plat.draw(screen)

    # Draw player image at dummy position
    screen.blit(player_img, (player.rect.x, player.rect.y))

    # Update UI
    ui.update(player)
    ui.draw(screen)

    # Refresh screen
    pygame.display.flip()
    clock.tick(30)

pygame.quit()

