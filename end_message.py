# end_message.py
import pygame
import sys
import os
import math
import time

def run_end_message():
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dream Over")

    # Load bgstart.gif (same as in start.py)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(script_dir, "assets", "bgstart.gif")
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    font = pygame.font.SysFont(None, 80)  # big font
    message = "Keep sleeping!! Hope you liked the dream"

    start_time = time.time()
    running = True
    while running:
        screen.blit(bg_img, (0, 0))  # background image

        # Pulsing glow effect
        elapsed = time.time() - start_time
        glow_alpha = int((math.sin(elapsed * 2) + 1) * 127)  # 0–255

        text_surface = font.render(message, True, (0, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        # Glow (draw text slightly bigger with alpha)
        glow_surface = font.render(message, True, (0, 255, 255))
        glow_surface = pygame.transform.scale(glow_surface, (text_rect.width + 10, text_rect.height + 10))
        glow_rect = glow_surface.get_rect(center=text_rect.center)
        glow_surface.set_alpha(glow_alpha)

        screen.blit(glow_surface, glow_rect)
        screen.blit(text_surface, text_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

    pygame.quit()
    sys.exit()
