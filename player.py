import pygame
import os

class Player:
    def __init__(self, x, y, platform_rect):
        # Load sprites
        base_path = os.path.dirname(__file__)
        assets_path = os.path.join(base_path, "assets")

        # Running frames
        self.run_frames = [
            pygame.image.load(os.path.join(assets_path, "players/player1.png")),
            pygame.image.load(os.path.join(assets_path, "players/player2.png")),
            pygame.image.load(os.path.join(assets_path, "players/player3.png")),
            pygame.image.load(os.path.join(assets_path, "players/player4.png")),
        ]
        self.run_frames = [pygame.transform.scale(img, (40, 40)) for img in self.run_frames]

        # Jump frame (reuse player1 if no separate jump sprite)
        self.jump_frame = pygame.transform.scale(
            pygame.image.load(os.path.join(assets_path, "players/player1.png")),
            (40, 40)
        )

        self.frame_index = 0
        self.image = self.run_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement + physics
        self.speed = 5
        self.jump_power = 12
        self.gravity = 0
        self.on_ground = False
        self.animation_counter = 0

        # Movement limits
        self.min_x = 0
        self.max_x = 750 - 40  # stops 50px before screen end

        # Platform collision
        self.platform_rect = platform_rect

    def handle_input(self, keys):
        moved = False
        # Horizontal movement
        if keys[pygame.K_RIGHT] and self.rect.x < self.max_x:
            self.rect.x += self.speed
            moved = True
        if keys[pygame.K_LEFT] and self.rect.x > self.min_x:
            self.rect.x -= self.speed
            moved = True

        # Jump with SPACE or UP arrow
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.gravity = -self.jump_power
            self.on_ground = False

        # Animate
        if self.on_ground and moved:
            self.animate()
        elif not self.on_ground:
            self.image = self.jump_frame

    def animate(self):
        self.animation_counter += 1
        if self.animation_counter >= 8:  # controls animation speed
            self.animation_counter = 0
            self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            self.image = self.run_frames[self.frame_index]

    def update(self):
        # Apply gravity
        self.gravity += 0.5
        self.rect.y += self.gravity

        # Platform collision
        if self.rect.colliderect(self.platform_rect):
            # Only land on top
            if self.rect.bottom >= self.platform_rect.top and self.gravity >= 0:
                self.rect.bottom = self.platform_rect.top
                self.gravity = 0
                self.on_ground = True
        else:
            self.on_ground = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
