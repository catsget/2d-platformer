import math
import pygame
from settings import *

# ===== Уровень "Пещера" =====
# Размер мира
LEVEL_WIDTH = 2100
LEVEL_HEIGHT = 1800

# ----- Этаж 1 (низ): прыжки по камням над лавой -----
# Платформы: (x, y, ширина, высота)
PLATFORMS = [
    # низ — старт и камни-острова над лавой
    (0, 1740, 260, 60),      # старт
    (350, 1740, 140, 60),    # остров
    (700, 1740, 140, 60),    # остров
    (1050, 1740, 140, 60),   # остров
    (1500, 1740, 160, 60),   # остров
    (1840, 1740, 260, 60),   # посадочная у лианы №1

    # ----- Этаж 2 (середина): змейкой справа налево -----
    (1700, 1240, 220, 40),
    (1400, 1180, 180, 40),
    (1000, 1240, 200, 40),
    (700, 1180, 180, 40),
    (400, 1240, 200, 40),    # подход к лиане №2

    # ----- Этаж 3 (верх): змейкой слева направо — финиш -----
    (250, 660, 240, 40),
    (600, 600, 220, 40),
    (950, 660, 200, 40),
    (1340, 600, 240, 40),
    (1650, 660, 200, 40),
]

# Лава: (x, y, ширина, высота) — прикосновение = смерть
LAVA = [
    (260, 1760, 1580, 40),   # большой провал между этажом 1
]

# Лианы: (x, y) — вертикальный прямоугольник VINE_WIDTH толщиной
# Лезть по ним, чтобы попасть на следующий этаж
VINE_SPANS = [
    (1900, 1150, 610),       # лиана №1: этаж 1 -> этаж 2 (у правого края)
    (300, 700, 560),         # лиана №2: этаж 2 -> этаж 3 (слева)
]

# Монеты: (x, y) — по всей змейке
COINS = [
    # этаж 1
    (380, 1690), (730, 1690), (1080, 1690), (1530, 1690),
    # лиана 1 / вход на этаж 2
    (1790, 1180),
    # этаж 2 (справа налево)
    (1490, 1120), (1090, 1180), (790, 1120), (490, 1180),
    # лиана 2 / вход на этаж 3
    (330, 640),
    # этаж 3 (слева направо)
    (340, 600), (690, 540), (1040, 600), (1430, 540), (1740, 600),
]

# Факелы: (x, y_подножия) — стоят на платформах вдоль маршрута
TORCH_SPOTS = [
    (120, 1740), (970, 1740), (1980, 1740),        # этаж 1
    (1650, 1240), (350, 1240),                     # этаж 2
    (170, 660), (1540, 600), (1800, 660),          # этаж 3
]


class Level:
    def __init__(self):
        self.platforms = [pygame.Rect(x, y, w, h) for x, y, w, h in PLATFORMS]
        self.lava = [pygame.Rect(x, y, w, h) for x, y, w, h in LAVA]
        self.vines = [pygame.Rect(x, y, VINE_WIDTH, span) for x, y, span in VINE_SPANS]
        self.coins = [(x, y) for x, y in COINS]
        self.torches = TORCH_SPOTS
        # Предрендер свечения факела в 4 фазах пульсации (экономим пересоздание)
        base = GLOW_RINGS[0][0] * 2
        self.glow_frames = []
        for phase in range(4):
            size = base + phase * 6
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx = size // 2
            for r, alpha in GLOW_RINGS:
                pygame.draw.circle(surf, (*GLOW_COLOR, alpha), (cx, cx), r + phase * 3)
            self.glow_frames.append(surf)

    @property
    def collected_all(self):
        return len(self.coins) == 0

    def collect_coins(self, player_rect):
        """Забирает монеты, которых коснулся игрок."""
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin[0] - 12, coin[1] - 12, 24, 24)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)

    def lava_fatal(self, player_rect):
        return any(player_rect.colliderect(pool) for pool in self.lava)

    def _draw_lava(self, surface, camera_x, camera_y, ticks):
        """Лава с волнующейся поверхностью."""
        for pool in self.lava:
            x = pool.x - camera_x
            y = pool.y - camera_y
            pygame.draw.rect(surface, LAVA_DARK, (x, y, pool.width, pool.height))
            # Волна на поверхности
            phase = ticks * 0.005
            wave = [(x, y)]
            for i in range(0, pool.width + 20, 20):
                wave_y = y + math.sin(phase + (x + i) * 0.05) * 3
                wave.append((x + i, wave_y))
            wave.append((x + pool.width, y + 10))
            pygame.draw.polygon(surface, LAVA_COLOR, wave)

    def _draw_vine(self, surface, vine, camera_x, camera_y):
        x = vine.x - camera_x
        y = vine.y - camera_y
        mid = x + vine.width // 2
        pygame.draw.line(surface, VINE_COLOR,
                         (mid, y), (mid, y + vine.height), 4)
        # Листья по сторонам через каждые 26px
        step = 0
        while True:
            leaf_y = y + 14 + step * 26
            if leaf_y > y + vine.height - 6:
                break
            side = x + vine.width if step % 2 else x
            pygame.draw.circle(surface, VINE_LEAF, (side, int(leaf_y)), 5)
            step += 1

    def _draw_stalactites(self, surface, camera_x, camera_y):
        """Сталактиты под некоторыми платформами — атмосфера пещеры."""
        for i, platform in enumerate(self.platforms):
            if i % 2:
                continue
            for j in range(3):
                tip_x = platform.x - camera_x + 30 + j * (platform.width - 60) // 2
                tip_y = platform.bottom - camera_y
                depth = (i + j) % 3 * 8 + 12
                pygame.draw.polygon(surface, STALACTITE_COLOR, [
                    (tip_x - 8, tip_y), (tip_x + 8, tip_y), (tip_x, tip_y + depth)
                ])

    def _draw_parallax(self, surface, camera_x, camera_y):
        """Дальние слои пещеры: сталактиты сверху и сталагмиты снизу,
        движутся медленнее камеры (factor слоя)."""
        w, h = surface.get_size()
        for layer in PARALLAX_LAYERS:
            factor = layer["factor"]
            color = layer["color"]
            offset_x = camera_x * factor
            # Небольшой вертикальный сдвиг от центра мира
            norm_y = (camera_y - (LEVEL_HEIGHT - HEIGHT) / 2) * factor * 0.3
            step = PARALLAX_STEP
            first = int(offset_x // step) - 1
            layers_count = w // step + 3
            for i in range(first, first + layers_count):
                x = i * step - offset_x
                # Детерминированная вариация высоты
                depth = 50 + (i * 37 % 70)
                if i % 3 == 0:
                    depth -= 25
                # Потолок
                top_y = 0 - norm_y
                pygame.draw.polygon(surface, color, [
                    (x, top_y), (x + 110, top_y), (x + 40, top_y + depth)
                ])
                # Пол дальнего плана
                bottom_y = h + norm_y
                pygame.draw.polygon(surface, color, [
                    (x, bottom_y), (x + 110, bottom_y), (x + 40, bottom_y - depth)
                ])

    def _draw_torch(self, surface, spot, camera_x, camera_y, ticks):
        """Факел: рукоять + дрожащее пламя + тёплое свечение."""
        x = spot[0] - camera_x
        y_base = spot[1] - camera_y
        if not (-80 < x < surface.get_width() + 80):
            return
        seed = spot[0] * 0.017
        # Свечение (4 фазы пульсации + BLEND_ADD как настоящий свет)
        phase = int((math.sin(ticks * 0.004 + seed) + 1) * 1.99)
        glow = self.glow_frames[phase]
        surface.blit(glow, (x - glow.get_width() // 2, y_base - 34 - glow.get_height() // 2),
                     special_flags=pygame.BLEND_ADD)
        # Рукоять
        pygame.draw.rect(surface, TORCH_HANDLE, (x - 2, y_base - 26, 5, 26))
        # Пламя (дрожит и покачивается)
        flick = math.sin(ticks * 0.02 + seed) * 2.5
        sway = math.sin(ticks * 0.013 + seed * 2) * 2
        tip_y = y_base - 26 - 14 + flick
        pygame.draw.polygon(surface, FLAME_COLOR, [
            (x - 4, y_base - 26), (x + 4, y_base - 26),
            (x + 3 + sway, tip_y), (x - 3 + sway, tip_y)
        ])
        pygame.draw.polygon(surface, FLAME_CORE, [
            (x - 2, y_base - 26), (x + 2, y_base - 26), (x + sway, tip_y + 3)
        ])

    def draw(self, surface, camera_x, camera_y, ticks):
        # Дальний план
        self._draw_parallax(surface, camera_x, camera_y)
        # Лианы (за платформами)
        for vine in self.vines:
            self._draw_vine(surface, vine, camera_x, camera_y)
        # Платформы
        for platform in self.platforms:
            x = platform.x - camera_x
            y = platform.y - camera_y
            pygame.draw.rect(surface, PLATFORM_COLOR, (x, y, platform.width, platform.height))
            pygame.draw.rect(surface, PLATFORM_EDGE, (x, y, platform.width, 4))
        # Сталактиты
        self._draw_stalactites(surface, camera_x, camera_y)
        # Факелы
        for spot in self.torches:
            self._draw_torch(surface, spot, camera_x, camera_y, ticks)
        # Лава поверх
        self._draw_lava(surface, camera_x, camera_y, ticks)
        # Монеты
        for coin in self.coins:
            x = coin[0] - camera_x
            y = coin[1] - camera_y
            pygame.draw.circle(surface, COIN_COLOR, (int(x), int(y)), 10)
            pygame.draw.circle(surface, (160, 120, 20), (int(x), int(y)), 10, 2)
