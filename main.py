import pygame
import sys
from settings import *
from player import Player
from level import Level, LEVEL_WIDTH, LEVEL_HEIGHT


def draw_text(surface, text, size, x, y, color=TEXT_COLOR):
    font = pygame.font.SysFont("arial", size, bold=True)
    surface.blit(font.render(text, True, color), (x, y))


def create_camera_position(player, camera_x, camera_y):
    """Плавная камера по обеим осям: lerp к цели + clamp по краям уровня."""
    target_x = max(0.0, min(player.x + PLAYER_WIDTH / 2 - WIDTH / 2, LEVEL_WIDTH - WIDTH))
    target_y = max(0.0, min(player.y + PLAYER_HEIGHT / 2 - HEIGHT / 2, LEVEL_HEIGHT - HEIGHT))
    camera_x += (target_x - camera_x) * CAMERA_SMOOTHING
    camera_y += (target_y - camera_y) * CAMERA_SMOOTHING
    # Не даём камере дрожать на маленьких отклонениях
    if abs(target_x - camera_x) < 0.5:
        camera_x = target_x
    if abs(target_y - camera_y) < 0.5:
        camera_y = target_y
    return (
        max(0.0, min(camera_x, LEVEL_WIDTH - WIDTH)),
        max(0.0, min(camera_y, LEVEL_HEIGHT - HEIGHT)),
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    player = Player(100, 1650)
    level = Level()
    score = 0
    deaths = 0
    total_coins = len(level.coins)
    camera_x = 0.0
    camera_y = LEVEL_HEIGHT - HEIGHT
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
                    player = Player(100, 1650)
                    level = Level()
                    score = 0
                    deaths = 0
                    camera_y = LEVEL_HEIGHT - HEIGHT

        # --- Состояния ---
        won = level.collected_all
        dead = (
            not won
            and (
                level.lava_fatal(player.rect)
                or player.y > LEVEL_HEIGHT + 100   # упал за границу мира
            )
        )

        # --- Обновление ---
        if not won and not dead:
            player.update(level.platforms, level.vines)
            before = len(level.coins)
            level.collect_coins(player.rect)
            score += before - len(level.coins)
            # Фиксируем смерть ровно один кадр
            if level.lava_fatal(player.rect) or player.y > LEVEL_HEIGHT + 100:
                deaths += 1

        camera_x, camera_y = create_camera_position(player, camera_x, camera_y)

        # --- Рендер ---
        screen.fill(BG_COLOR)
        level.draw(screen, int(camera_x), int(camera_y), pygame.time.get_ticks())
        player.draw(screen, int(camera_x), int(camera_y))

        draw_text(screen, f"Монеты: {score}/{total_coins}   Смертей: {deaths}", 24, 15, 10)
        draw_text(screen, "A/D — бег, W/Space — прыжок, по лианам W/S — лезть, Space — спрыгнуть, R — заново",
                  16, 15, 40)

        if won:
            draw_text(screen, "ПОБЕДА! Все монеты пещеры собраны!", 42, WIDTH // 2 - 300, HEIGHT // 2 - 60)
            draw_text(screen, "Нажми R, чтобы играть заново", 24, WIDTH // 2 - 190, HEIGHT // 2)
        elif dead:
            draw_text(screen, f"Лава! Смерть #{deaths}", 36, WIDTH // 2 - 150, HEIGHT // 2 - 60)
            draw_text(screen, "Нажми R, чтобы начать заново", 24, WIDTH // 2 - 190, HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
