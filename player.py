import pygame
from settings import *


class Player:
    """Игрок: плавный бег, прыжки, гравитация и коллизии с платформами.

    Позиция хранится во float (self.x, self.y), а self.rect синхронизируется
    с округлёнными значениями для точных коллизий.
    """

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.coyote_timer = 0    # кадры, оставшиеся для прыжка после схода с земли
        self.jump_buffer = 0     # кадры, оставшиеся в "памяти" нажатия прыжка

    def update(self, platforms):
        # --- Управление: плавное ускорение ---
        keys = pygame.key.get_pressed()
        move_dir = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        if move_dir:
            self.vel_x += move_dir * PLAYER_ACCEL
            self.vel_x = max(-PLAYER_SPEED, min(PLAYER_SPEED, self.vel_x))
        else:
            friction = PLAYER_FRICTION if self.on_ground else AIR_FRICTION
            self.vel_x *= (1.0 - friction)

        # --- Прыжок с coyote time и буфером нажатия ---
        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump_buffer = JUMP_BUFFER_FRAMES
        if self.on_ground:
            self.coyote_timer = COYOTE_FRAMES
        if self.jump_buffer > 0 and self.coyote_timer > 0:
            self.vel_y = JUMP_STRENGTH
            self.jump_buffer = 0
            self.coyote_timer = 0
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
        if self.coyote_timer > 0:
            self.coyote_timer -= 1

        # --- Гравитация ---
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # --- Движение по горизонтали + коллизии ---
        self.x += self.vel_x
        self.rect.topleft = (round(self.x), round(self.y))
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.vel_x > 0:
                    self.rect.right = platform.left
                elif self.vel_x < 0:
                    self.rect.left = platform.right
                self.x = float(self.rect.x)

        # --- Движение по вертикали + коллизии ---
        self.y += self.vel_y
        self.rect.topleft = (round(self.x), round(self.y))
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
                self.y = float(self.rect.y)

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
