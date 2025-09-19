import pygame
from player import Player

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()

    # Platform rectangle (UI/Obstacle person can draw it)
    platform_rect = pygame.Rect(100, 300, 600, 40)

    # Create player above platform
    player = Player(150, 260, platform_rect)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Draw everything
        screen.fill((200, 230, 255))
        pygame.draw.rect(screen, (100, 200, 100), platform_rect)  # simple platform visual
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
