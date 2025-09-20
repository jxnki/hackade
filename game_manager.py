import start
import first
import normal
import control_shift
import dark
import neon
import slope
import car_ride
import highspeed
import end_message   # NEW FILE
import pygame
import sys

def main():
    pygame.init()

    # Start screen
    start.run_start_page()

    lives = 100  # initial lives

    # First stage
    lives = first.run_first(lives)
    if lives <= 0:
        game_over()
        return

    # Normal stage
    lives = normal.run_normal(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # --- short blackout before control_shift ---
    screen = pygame.display.set_mode((800, 400))
    black = pygame.Surface(screen.get_size())
    black.fill((0, 0, 0))
    screen.blit(black, (0, 0))
    pygame.display.flip()
    pygame.time.delay(300)

    # Control Shift stage
    lives = control_shift.run_control_shift(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Dark stage
    lives = dark.run_dark(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Neon stage
    lives = neon.run_neon(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Slope stage
    lives = slope.run_slope(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Car Ride stage
    lives = car_ride.run_car_ride(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # High Speed stage
    lives = highspeed.run_highspeed(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # If survived all -> go to dream ending
    end_message.run_end_message()

def game_over():
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Oh NO!")

    import os, math, time
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(script_dir, "assets", "bgstart.gif")
    bg_img = pygame.image.load(bg_path).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    font = pygame.font.SysFont(None, 80)  # big font
    message = "Oh NO! You have woken up!!"

    start_time = time.time()
    running = True
    while running:
        screen.blit(bg_img, (0, 0))

        elapsed = time.time() - start_time
        glow_alpha = int((math.sin(elapsed * 2) + 1) * 127)

        text_surface = font.render(message, True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        glow_surface = font.render(message, True, (255, 0, 0))
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


if __name__ == "__main__":
    main()
