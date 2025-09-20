import pygame
import sys
import random


def run_first(lives):
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Select the Correct Player")
    clock = pygame.time.Clock()
    FPS = 60

    # Platform
    platform_height = 50
    platform_y = HEIGHT - platform_height

    # Player sprite
    player_img = pygame.image.load("assets/players/player1.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (60, 60))

    class Player:
        def __init__(self, x, y, is_correct=False):
            self.rect = player_img.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.vel_y = 0
            self.selected = False
            self.is_correct = is_correct
            self.jump_offset = random.randint(0, 100)  # for idle animation randomness
            self.active = True

        def update(self):
            # Idle random jump if not the chosen correct one
            if not self.selected or not self.is_correct:
                if random.randint(1, 60) == 1 and self.rect.bottom >= platform_y:
                    self.vel_y = -random.randint(7, 12)
            # Apply gravity
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
    players = [Player(60 + i * 70, platform_y - 60, is_correct=(i == correct_idx)) for i in range(9)]

    # Portal
    portal_radius = 40
    portal_x = WIDTH - 100
    portal_y = platform_y - portal_radius
    portal_rect = pygame.Rect(portal_x, portal_y, portal_radius*2, portal_radius*2)

    # Load and position high.png banner
    try:
        banner_img = pygame.image.load("assets/high.png").convert_alpha()
        banner_width = 700
        banner_height = 700
        banner_img = pygame.transform.scale(banner_img, (banner_width, banner_height))
        banner_rect = banner_img.get_rect()
        banner_rect.centerx = WIDTH // 2
        banner_rect.top = 4
    except Exception:
        banner_img = None

    selected_idx = None

    banner_start_time = pygame.time.get_ticks()
    running = True
    while running:
        clock.tick(FPS)
        screen.fill((135, 206, 235))

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 0  # treat quit as game over
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for idx, p in enumerate(players):
                    if p.rect.collidepoint(mouse_pos):
                        selected_idx = idx
                for i, p in enumerate(players):
                    p.selected = (i == selected_idx)

        # --- Draw banner at top center (disappear after 3s) ---
        if banner_img:
            if pygame.time.get_ticks() - banner_start_time < 3000:
                screen.blit(banner_img, banner_rect)

        # --- Draw platform ---
        pygame.draw.rect(screen, (139, 69, 19), (0, platform_y, WIDTH, platform_height))

        # --- Draw portal ---
        pygame.draw.ellipse(screen, (0, 0, 0),
                           (portal_x - 20, 20, portal_radius*2 + 40, HEIGHT - 40))

        # --- Update & draw players ---
        keys = pygame.key.get_pressed()
        for idx, p in enumerate(players):
            if idx == selected_idx and p.is_correct and p.active:
                # Continuous movement controls
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    p.rect.x += 5
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    p.rect.x -= 5
                if (keys[pygame.K_UP] or keys[pygame.K_w]) and p.rect.bottom >= platform_y:
                    p.vel_y = -15
            p.update()
            if p.active:
                p.draw(screen)

        # --- Portal collision check ---
        if selected_idx is not None:
            p = players[selected_idx]
            if p.is_correct and p.rect.colliderect(portal_rect):
                return lives  # advance with same lives

        pygame.display.update()
