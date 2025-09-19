
import pygame
import sys
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - Select the Correct Player")

clock = pygame.time.Clock()
FPS = 60

# Platform setup
platform_height = 50
platform_y = HEIGHT - platform_height

# Load one player sprite (all identical)
player_img = pygame.image.load("assets/players/player1.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (60, 60))

# Player data
class Player:
    def __init__(self, x, y, is_correct=False):
        self.rect = player_img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.selected = False
        self.is_correct = is_correct
        self.jump_offset = random.randint(0, 100)
        self.active = True

    def update(self):
        # Idle random jump
        if not self.selected or not self.is_correct:
            if random.randint(1, 60) == 1 and self.rect.bottom >= platform_y:
                self.vel_y = -random.randint(7, 12)
        # Gravity
        self.vel_y += 1
        self.rect.y += self.vel_y
        # Floor collision
        if self.rect.bottom >= platform_y:
            self.rect.bottom = platform_y
            self.vel_y = 0

    def draw(self, surf):
        surf.blit(player_img, self.rect)
        if self.selected:
            pygame.draw.rect(surf, (255, 215, 0), self.rect, 4)  # gold border

# Create 9 players
correct_idx = random.randint(0, 8)
players = []
for i in range(9):
    x = 60 + i * 70
    y = platform_y - 60
    players.append(Player(x, y, is_correct=(i == correct_idx)))

# Portal (black circle)
portal_radius = 40
portal_x = WIDTH - 100
portal_y = platform_y - portal_radius
portal_rect = pygame.Rect(portal_x, portal_y, portal_radius * 2, portal_radius * 2)

# Next frame placeholder
def next_frame():
    print("Next frame triggered!")
    # Add next level logic here

selected_idx = None

running = True
while running:
    clock.tick(FPS)
    screen.fill((135, 206, 235))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for idx, p in enumerate(players):
                if p.rect.collidepoint(mouse_pos):
                    selected_idx = idx
            for i, p in enumerate(players):
                p.selected = (i == selected_idx)
        # Remove discrete right movement, handle continuous motion below

    # Draw platform
    pygame.draw.rect(screen, (139, 69, 19), (0, platform_y, WIDTH, platform_height))

    # Draw portal
    pygame.draw.circle(screen, (0, 0, 0), (portal_x + portal_radius, portal_y + portal_radius), portal_radius)


    # Update and draw players
    keys = pygame.key.get_pressed()
    for idx, p in enumerate(players):
        # Continuous forward motion for correct selected player
        if idx == selected_idx and p.is_correct and p.active:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                p.rect.x += 5
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                p.rect.x -= 5
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and p.rect.bottom >= platform_y:
                p.vel_y = -15
        p.update()
        if p.active:
            p.draw(screen)

    # Check portal collision for selected
    if selected_idx is not None:
        p = players[selected_idx]
        if p.is_correct and p.rect.colliderect(portal_rect):
            p.active = False
            selected_idx = None
            next_frame()

    pygame.display.update()

pygame.quit()
sys.exit()
