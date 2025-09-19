import pygame
import random
import os

class ObstacleManager:
    def __init__(self, screen_width=800, screen_height=400, platform_height=300):
        self.obstacles = []  # list of [surface, rect]
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.platform_height = platform_height

        asset_dir = os.path.join(os.path.dirname(__file__), "assets")

        # --- load & tile platform ---
        raw_platform = pygame.image.load(
            os.path.join(asset_dir, "platform.png")
        ).convert_alpha()

        # scale raw platform to fixed height but keep width ratio
        tile_height = platform_height
        tile_width = int(raw_platform.get_width() * (tile_height / raw_platform.get_height()))
        tile_img = pygame.transform.scale(raw_platform, (tile_width, tile_height))

        # create a surface full width of screen to hold all tiles
        self.platform_img = pygame.Surface((screen_width, platform_height), pygame.SRCALPHA)
        for x in range(0, screen_width, tile_img.get_width()):
            self.platform_img.blit(tile_img, (x, 0))

        # rect at bottom of the screen
        self.platform_rect = self.platform_img.get_rect(
            bottomleft=(0, screen_height)
        )

        # --- load & scale obstacles (stone, wood) ---
        stone_img = pygame.image.load(os.path.join(asset_dir, "stone.png")).convert_alpha()
        wood_img = pygame.image.load(os.path.join(asset_dir, "wood.png")).convert_alpha()
        # scale them to fit on top of platform
        stone_img = pygame.transform.scale(stone_img, (100, 100))
        wood_img = pygame.transform.scale(wood_img, (100, 100))

        self.images = [stone_img, wood_img]

    def spawn_obstacle(self):
   
        img = random.choice(self.images)
        rect = img.get_rect()

        # sink slightly to remove gap caused by transparency
        rect.bottomleft = (
        self.screen_width,
        self.platform_rect.top + 285  # adjust this number until it looks right
    )

        self.obstacles.append([img, rect])
# ...existing code...
    def update(self):
        """Move obstacles and randomly spawn new ones."""
        if random.randint(1, 100) < 2:  # ~2% chance per frame
            self.spawn_obstacle()

        # move existing obstacles
        for obs in self.obstacles:
            obs[1].x -= 5

        # remove off-screen
        self.obstacles = [o for o in self.obstacles if o[1].x > -o[1].width]

    def draw(self, screen):
        # draw platform first
        screen.blit(self.platform_img, self.platform_rect)
        # draw obstacles
        for img, rect in self.obstacles:
            screen.blit(img, rect)


# ---------------------------------
# Test your obstacle manager standalone
# ---------------------------------
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    clock = pygame.time.Clock()
    obstacle_manager = ObstacleManager()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        obstacle_manager.update()

        screen.fill((200, 230, 255)) # white background like your screenshot
        obstacle_manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
