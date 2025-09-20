# dark.py
import pygame
import sys
import random
import math
import os
import time

def run_dark(lives, duration=25):
    pygame.init()

    # Screen setup
    WIDTH, HEIGHT = 800, 500
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Dash - Dark Level with Torch Cone")

    clock = pygame.time.Clock()
    FPS = 60

    # Platform setup
    platform_height = 50
    platform_y = HEIGHT - platform_height
    platform_color = (20, 20, 20)

    # Player setup
    player_img = pygame.image.load("assets/players/player1.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, (80, 80))
    player_rect = player_img.get_rect(center=(WIDTH // 2, platform_y - 40))

    # Torch beam settings (narrow cone)
    beam_length = 1200
    beam_angle = math.radians(25)
    beam_direction = -math.pi / 2

    # Hidden objects
    object_files = [
        "assets/applee.png", "assets/candy.png", "assets/key.png", "assets/smile.png",
        "assets/stone.png", "assets/wood.png", "assets/arrow.png", "assets/bush.png"
    ]
    hidden_objects = []
    for i in range(10):
        img_path = random.choice(object_files)
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (40, 40))
        rect = img.get_rect()
        rect.x = random.randint(0, WIDTH - rect.width)
        rect.y = random.randint(0, platform_y - 450)
        hidden_objects.append({
            "img": img, "rect": rect, "found": False,
            "name": os.path.basename(img_path)
        })

    font = pygame.font.SysFont(None, 36)

    torch_moves = 0
    MAX_TORCH_MOVES = 2

    # --- Timer ---
    start_time = time.time()

    running = True
    while running:
        clock.tick(FPS)

        # --- End after duration ---
        if time.time() - start_time >= duration:
            return max(0, lives)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                clicked_object = None
                for obj in hidden_objects:
                    if not obj["found"] and obj["rect"].collidepoint(mx, my):
                        clicked_object = obj
                        break
                if clicked_object:
                    x, y = player_rect.center
                    dx = clicked_object["rect"].centerx - x
                    dy = clicked_object["rect"].centery - y
                    dist = math.hypot(dx, dy)
                    angle_to_obj = math.atan2(dy, dx)

                    def angle_diff(a, b):
                        return math.atan2(math.sin(a - b), math.cos(a - b))

                    if dist < beam_length and abs(angle_diff(angle_to_obj, beam_direction)) < beam_angle / 2:
                        clicked_object["found"] = True
                        if torch_moves < MAX_TORCH_MOVES:
                            if clicked_object["name"] in ["stone.png", "wood.png", "arrow.png", "bush.png"]:
                                lives -= 1
                            else:
                                lives = min(lives + 1, 5)
                            if lives <= 0:
                                return 0
                elif torch_moves < MAX_TORCH_MOVES:
                    dx = mx - player_rect.centerx
                    dy = my - player_rect.centery
                    beam_direction = math.atan2(dy, dx)
                    torch_moves += 1

        # Background
        screen.fill((0, 0, 0))

        # Platform
        pygame.draw.rect(screen, platform_color, (0, platform_y, WIDTH, platform_height))

        # Torch cone
        beam_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        x, y = player_rect.center
        left_dir = beam_direction - beam_angle / 2
        right_dir = beam_direction + beam_angle / 2
        points = [
            (x, y),
            (x + beam_length * math.cos(left_dir), y + beam_length * math.sin(left_dir)),
            (x + beam_length * math.cos(right_dir), y + beam_length * math.sin(right_dir))
        ]
        pygame.draw.polygon(beam_surface, (255, 255, 200, 90), points)
        screen.blit(beam_surface, (0, 0))

        # Reveal hidden objects
        for obj in hidden_objects:
            if not obj["found"]:
                dx = obj["rect"].centerx - x
                dy = obj["rect"].centery - y
                dist = math.hypot(dx, dy)
                angle_to_obj = math.atan2(dy, dx)

                def angle_diff(a, b):
                    return math.atan2(math.sin(a - b), math.cos(a - b))

                if dist < beam_length and abs(angle_diff(angle_to_obj, beam_direction)) < beam_angle / 2:
                    screen.blit(obj["img"], obj["rect"])

        # Draw player
        screen.blit(player_img, player_rect)

        # UI
        lives_text = font.render(f"Lives: {lives}", True, (255, 255, 0))
        screen.blit(lives_text, (10, 10))
        moves_text = font.render(f"Torch Moves Left: {MAX_TORCH_MOVES - torch_moves}", True, (200, 200, 255))
        screen.blit(moves_text, (10, 40))

        if torch_moves >= MAX_TORCH_MOVES:
            over_text = font.render("Your chances are over!", True, (255, 0, 0))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.delay(1500)
            return lives

        pygame.display.flip()
