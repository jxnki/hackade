# end_message.py
import pygame
import sys
import os
import math
import time

def run_end_message():
    pygame.init()
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Over")

    # Load bgstart.gif (same as in start.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(script_dir, "assets", "bgstart.gif")
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    # Use a smaller font and wrap text if needed
    font = pygame.font.SysFont(None, 48)
    message = "Keep sleeping!!\nHope you liked the dream"

    start_time = time.time()
    running = True
    while running:
        screen.blit(bg_img, (0, 0))  # background image

        # Pulsing glow effect
        elapsed = time.time() - start_time
        glow_alpha = int((math.sin(elapsed * 2) + 1) * 127)  # 0–255

        # Render each line separately and stack vertically
        lines = message.split("\n")
        surfaces = [font.render(line, True, (0, 255, 255)) for line in lines]
        heights = [surf.get_height() for surf in surfaces]
        total_height = sum(heights) + (len(heights) - 1) * 10
        y_start = HEIGHT // 2 - total_height // 2
        for i, surf in enumerate(surfaces):
            x = WIDTH // 2 - surf.get_width() // 2
            y = y_start + sum(heights[:i]) + i * 10
            # Glow for each line
            glow_surface = pygame.transform.scale(surf, (surf.get_width() + 10, surf.get_height() + 10))
            glow_surface.set_alpha(glow_alpha)
            glow_rect = glow_surface.get_rect(center=(WIDTH // 2, y + surf.get_height() // 2))
            screen.blit(glow_surface, glow_rect)
            screen.blit(surf, (x, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    pygame.quit()
    sys.exit()
