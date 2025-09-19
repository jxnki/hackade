# transition.py
import pygame
import sys
import time

def portal_transition(screen, player_rect, player_surf, portal_frames,
                      duration=1.5, blackout_ms=300):
    """
    Animate the player moving into a portal (no overlapping ghost images).
    - Player slides directly into the portal while portal grows.
    """
    clock = pygame.time.Clock()
    start = time.time()
    WIDTH, HEIGHT = screen.get_size()

    # Portal position (right edge, vertically centered)
    portal_center = (WIDTH - 120, HEIGHT // 2)

    frame_time = duration / max(1, len(portal_frames))

    while True:
        clock.tick(60)
        elapsed = time.time() - start
        t = min(1.0, elapsed / duration)

        # Handle quit/escape
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # Keep last game frame as background
        overlay = screen.copy()

        # --- Portal drawing ---
        frame_idx = min(len(portal_frames) - 1, int(elapsed / frame_time))
        portal_img = portal_frames[frame_idx]

        # Grow portal until ~3/4 window height
        target_height = int(HEIGHT * 0.75)
        final_scale = target_height / portal_img.get_height()
        scale = 0.3 + t * (final_scale - 0.3)

        portal_scaled = pygame.transform.smoothscale(
            portal_img,
            (int(portal_img.get_width() * scale), int(portal_img.get_height() * scale))
        )
        portal_rect = portal_scaled.get_rect(center=portal_center)
        overlay.blit(portal_scaled, portal_rect)

        # --- Player movement (single sprite, no overlap) ---
        new_x = int(player_rect.centerx + t * (portal_center[0] - player_rect.centerx))
        new_y = int(player_rect.centery + t * (portal_center[1] - player_rect.centery))
        player_rect_new = player_surf.get_rect(center=(new_x, new_y))
        overlay.blit(player_surf, player_rect_new)

        # Draw everything
        screen.blit(overlay, (0, 0))
        pygame.display.flip()

        if elapsed >= duration:
            break

    # --- Fade to black ---
    black = pygame.Surface(screen.get_size())
    black.fill((0, 0, 0))
    screen.blit(black, (0, 0))
    pygame.display.flip()
    pygame.time.delay(blackout_ms)
