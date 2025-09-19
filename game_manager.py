import start
import first
import normal
import control_shift
import neon
import slope
import pygame
import sys

def main():
    pygame.init()

    # Start screen
    start.run_start_page()

    lives = 5  # initial lives

    # First stage
    lives = first.run_first(lives)
    if lives <= 0:
        game_over()
        return

    # Normal stage for 25 seconds
    lives = normal.run_normal(lives, duration=5)
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

    # Control Shift stage for 25 seconds
    lives = control_shift.run_control_shift(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Neon stage for 25 seconds
    lives = neon.run_neon(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # Slope stage for 25 seconds
    lives = slope.run_slope(lives, duration=25)
    if lives <= 0:
        game_over()
        return

    # End screen if survived all
    game_over(survived=True, lives=lives)

def game_over(survived=False, lives=0):
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption("Game Over")
    font = pygame.font.SysFont(None, 48)
    running = True
    while running:
        screen.fill((0, 0, 0))
        if survived:
            msg = f"YOU SURVIVED with {lives} lives!"
            text = font.render(msg, True, (0, 255, 0))
        else:
            text = font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (400 - text.get_width()//2, 200 - text.get_height()//2))
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
