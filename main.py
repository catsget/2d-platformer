import pygame
import sys
from settings import *
from player import Player
from level import Level, LEVEL_WIDTH


def draw_text(surface, text, size, x, y, color=TEXT_COLOR):
    font = pygame.font.SysFont("arial", size, bold=True)
    surface.blit(font.render(text, True, color), (x, y))


def create_camera_position(player, camera_x):
    """Плавная камера: lerp к цели (центрирование игрока) + clamp по краям уровня."""
    target_x = max(0.0, min(player.x + PLAYER_WIDTH / 2 - WIDTH / 2, LEVEL_WIDTH - WIDTH))
    camera_x += (target_x - camera_x) * CAMERA_SMOOTHING
    # Не даём камере дрожать на маленьких отклонениях
    if abs(target_x - camera_x) < 0.5:
        camera_x = target_x
    return max(0.0, min(camera_x, LEVEL_WIDTH - WIDTH))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player(100, 400)
    level = Level()
    score = 0
    total_coins = len(level.coins)
    camera_x = 0.0
    running = True

    while running:
        clock.tick(FPS)

        # --- События ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:  # рестарт уровня
                    player = Player(100, 400)
                    level = Level()
                    score = 0

        # --- Обновление ---
        won = level.collected_all
        if not won and player.rect.y < HEIGHT + 200:
            player.update(level.platforms)
            before = len(level.coins)
            level.collect_coins(player.rect)
            score += before - len(level.coins)

        camera_x = create_camera_position(player, camera_x)

        # --- Рендер ---
        screen.fill(BG_COLOR)
        level.draw(screen, int(camera_x))
        player.draw(screen, int(camera_x))

        draw_text(screen, f"Монеты: {score}/{total_coins}", 24, 15, 10)
        draw_text(screen, "A/D или стрелки — бег, W/Space — прыжок, R — рестарт", 16, 15, 40)

        if won:
            draw_text(screen, "ПОБЕДА! Все монеты собраны!", 42, WIDTH // 2 - 280, HEIGHT // 2 - 60)
            draw_text(screen, "Нажми R, чтобы играть заново", 24, WIDTH // 2 - 190, HEIGHT // 2)
        elif player.rect.y > HEIGHT + 200:
            draw_text(screen, "Ты упал! Нажми R, чтобы начать заново", 36, WIDTH // 2 - 260, HEIGHT // 2 - 40)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
