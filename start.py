import pygame
from PIL import Image
import sys
import os
import math

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dream Dash - Start Page")
clock = pygame.time.Clock()

# Load GIF frames
def load_gif_frames(gif_path):
    pil_image = Image.open(gif_path)
    frames = []
    try:
        while True:
            pil_image.seek(pil_image.tell() + 1)
            frame = pil_image.convert("RGBA")
            mode, size = frame.mode, frame.size
            data = frame.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)
            py_image = pygame.transform.scale(py_image, (WIDTH, HEIGHT))
            frames.append(py_image)
    except EOFError:
        pass
    return frames

# === Load background GIF ===
gif_filename = r"assets/bgstart.gif"
background_frames = load_gif_frames(gif_filename)

# === Load person image ===
person_image_path = r"assets/players/person0.png"
person_image = pygame.image.load(person_image_path).convert_alpha()
person_image = pygame.transform.scale(person_image, (150, 150))

jump_amplitude = 20
jump_speed = 0.005
jump_time = 0

current_frame = 0
frame_delay = 150
last_update = pygame.time.get_ticks()

SOFT_PINK = (255, 182, 193)
BLACK = (0, 0, 0)
GLOW_COLOR = (255, 255, 255)
TEXT_COLOR = (51, 255, 255)

font = pygame.font.SysFont('Comic Sans MS', 75, bold=True)
button_font = pygame.font.SysFont('Comic Sans MS', 48)

button_width, button_height = 300, 80
button_rect = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 100, button_width, button_height)

def draw_text_with_glow(text, font, main_color, glow_color, position, glow_radius=3):
    x, y = position
    for dx in range(-glow_radius, glow_radius+1):
        for dy in range(-glow_radius, glow_radius+1):
            if dx == 0 and dy == 0:
                continue
            glow_surf = font.render(text, True, glow_color)
            glow_rect = glow_surf.get_rect(center=(x + dx, y + dy))
            screen.blit(glow_surf, glow_rect)
    main_surf = font.render(text, True, main_color)
    main_rect = main_surf.get_rect(center=position)
    screen.blit(main_surf, main_rect)

def draw_start_page():
    global current_frame, last_update, jump_time
    now = pygame.time.get_ticks()
    if now - last_update > frame_delay:
        current_frame = (current_frame + 1) % len(background_frames)
        last_update = now

    screen.blit(background_frames[current_frame], (0, 0))
    draw_text_with_glow("Dream Dash", font, TEXT_COLOR, GLOW_COLOR, (WIDTH//2, HEIGHT//2 - 200))

    jump_time += jump_speed * clock.get_time()
    jump_offset = int(jump_amplitude * math.sin(jump_time))
    person_rect = person_image.get_rect(center=(WIDTH//2, button_rect.top - 100 + jump_offset))
    screen.blit(person_image, person_rect)

    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 105, 180), button_rect, border_radius=15)
    else:
        pygame.draw.rect(screen, SOFT_PINK, button_rect, border_radius=15)

    button_text = button_font.render("Start", True, BLACK)
    button_text_rect = button_text.get_rect(center=button_rect.center)
    screen.blit(button_text, button_text_rect)

def run_start_page():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # go to next stage
        draw_start_page()
        pygame.display.flip()
        clock.tick(60)
