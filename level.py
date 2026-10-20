import pygame
from settings import *

# Уровень: (x, y, ширина, высота)
PLATFORMS = [
    (0, 550, 900, 50),     # стартовая земля
    (1000, 550, 1100, 50), # земля справа
    (350, 450, 150, 20),
    (600, 380, 150, 20),
    (850, 300, 150, 20),
    (1100, 250, 200, 20),
    (1400, 350, 150, 20),
    (1600, 450, 200, 20),
    (1300, 200, 100, 20),
]

# Монеты: (x, y)
COINS = [
    (400, 410),
    (450, 410),
    (650, 340),
    (700, 340),
    (900, 260),
    (950, 260),
    (1150, 210),
    (1200, 210),
    (1450, 310),
    (1700, 410),
    (1750, 410),
    (1330, 160),
]

LEVEL_WIDTH = 2100  # ширина уровня для камеры


class Level:
    def __init__(self):
        self.platforms = [pygame.Rect(x, y, w, h) for x, y, w, h in PLATFORMS]
        self.coins = [(x, y) for x, y in COINS]

    @property
    def collected_all(self):
        return len(self.coins) == 0

    def collect_coins(self, player_rect):
        """Забирает монеты, которых коснулся игрок."""
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin[0] - 12, coin[1] - 12, 24, 24)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)

    def draw(self, surface, camera_x):
        # Платформы
        for platform in self.platforms:
            x = platform.x - camera_x
            pygame.draw.rect(surface, PLATFORM_COLOR, (x, platform.y, platform.width, platform.height))
            # Тёмная полоска сверху для объёма
            pygame.draw.rect(surface, (50, 120, 60),
                             (x, platform.y, platform.width, 4))
        # Монеты
        for coin in self.coins:
            x = coin[0] - camera_x
            pygame.draw.circle(surface, COIN_COLOR, (int(x), coin[1]), 10)
            pygame.draw.circle(surface, (200, 150, 0), (int(x), coin[1]), 10, 2)
