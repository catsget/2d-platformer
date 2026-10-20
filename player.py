import pygame
from settings import *


class Player:
    """Игрок: бег, прыжки, гравитация и коллизии с платформами."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False

    def update(self, platforms):
        # --- Управление ---
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = PLAYER_SPEED

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH

        # --- Гравитация ---
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # --- Движение по горизонтали + коллизии ---
        self.rect.x += int(self.vel_x)
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                elif self.vel_x < 0:
                    self.rect.left = platform.right

        # --- Движение по вертикали + коллизии ---
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_y > 0:      # падаем — встаём на платформу
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:    # ударяемся головой
                    self.rect.top = platform.bottom
                    self.vel_y = 0

    def draw(self, surface, camera_x):
        x = self.rect.x - camera_x
        pygame.draw.rect(surface, PLAYER_COLOR, (x, self.rect.y, self.rect.width, self.rect.height))
        # Глаза, чтобы было видно направление
        if self.vel_x >= 0:
            eye_x = x + self.rect.width - 14
        else:
            eye_x = x + 6
        pygame.draw.circle(surface, (255, 255, 255), (eye_x + 4, self.rect.y + 14), 5)
        pygame.draw.circle(surface, (40, 40, 40), (eye_x + 6, self.rect.y + 14), 2)
