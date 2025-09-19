import pygame

class UIManager:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 24)
        self.score = 0

    def update(self, player):
        # Example: score = distance traveled
        self.score = player.rect.x // 10

    def draw(self, screen):
        # Display "Find your character"
        text_surface = self.font.render("Find your character!", True, (0, 0, 0))
        screen.blit(text_surface, (10, 10))

        # Display Score
        score_surface = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(score_surface, (10, 40))
