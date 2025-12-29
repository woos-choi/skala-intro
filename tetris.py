# tetris.py (종료조건: 맨 윗 행(0행)까지 블록이 차면 게임오버)
# 주요 변경점:
#  - game_over 판정: "스폰 불가"가 아니라 "grid[0]에 블록이 존재하면 종료"

import random
import pygame

GRID_W, GRID_H = 10, 20
CELL = 30
SIDE_W = 260
WIN_W = GRID_W * CELL + SIDE_W
WIN_H = GRID_H * CELL
FPS = 60

FALL_MS_NORMAL = 500
FALL_MS_SOFT = 40

MUSIC_PATH = "bgm.ogg"
MUSIC_VOLUME = 0.35

BLACK = (0, 0, 0)
GRAY = (45, 45, 45)
WHITE = (240, 240, 240)

COLORS = {
    "I": (0, 240, 240),
    "O": (240, 240, 0),
    "T": (160, 0, 240),
    "S": (0, 240, 0),
    "Z": (240, 0, 0),
    "J": (0, 100, 240),
    "L": (240, 160, 0),
}

SHAPES = {
    "I": [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "O": [
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "T": [
        [0, 1, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "S": [
        [0, 1, 1, 0],
        [1, 1, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "Z": [
        [1, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "J": [
        [1, 0, 0, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "L": [
        [0, 0, 1, 0],
        [1, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
}

def rotate_cw(mat):
    return [list(row) for row in zip(*mat[::-1])]

def clone_grid():
    return [[None for _ in range(GRID_W)] for _ in range(GRID_H)]

def can_place(grid, shape_mat, px, py):
    for r in range(4):
        for c in range(4):
            if shape_mat[r][c]:
                gx, gy = px + c, py + r
                if gx < 0 or gx >= GRID_W or gy >= GRID_H:
                    return False
                if gy >= 0 and grid[gy][gx] is not None:
                    return False
    return True

def lock_piece(grid, shape_mat, px, py, color):
    for r in range(4):
        for c in range(4):
            if shape_mat[r][c]:
                gx, gy = px + c, py + r
                if gy >= 0:
                    grid[gy][gx] = color

def clear_lines(grid):
    new_rows = []
    cleared = 0
    for row in grid:
        if all(cell is not None for cell in row):
            cleared += 1
        else:
            new_rows.append(row)

    while len(new_rows) < GRID_H:
        new_rows.insert(0, [None for _ in range(GRID_W)])
    return new_rows, cleared

def score_for_clears(cleared):
    if cleared <= 0:
        return 0
    return 100 * cleared * cleared

def spawn_piece():
    key = random.choice(list(SHAPES.keys()))
    mat = [row[:] for row in SHAPES[key]]
    color = COLORS[key]
    px = GRID_W // 2 - 2
    py = -2
    return key, mat, color, px, py

def try_rotate(grid, mat, px, py):
    rotated = rotate_cw(mat)
    for dx in (0, -1, 1, -2, 2):
        if can_place(grid, rotated, px + dx, py):
            return rotated, px + dx
    return mat, px

def top_row_filled(grid):
    """종료 조건: 0행(맨 윗 행)에 블록이 하나라도 있으면 True"""
    return any(cell is not None for cell in grid[0])

def draw_cell(surf, x, y, color):
    rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, (20, 20, 20), rect, 2)

def draw_grid(surf, grid):
    surf.fill(BLACK)
    for y in range(GRID_H):
        for x in range(GRID_W):
            pygame.draw.rect(surf, GRAY, pygame.Rect(x * CELL, y * CELL, CELL, CELL), 1)
            if grid[y][x] is not None:
                draw_cell(surf, x, y, grid[y][x])

def draw_piece(surf, shape_mat, px, py, color):
    for r in range(4):
        for c in range(4):
            if shape_mat[r][c]:
                gx, gy = px + c, py + r
                if gy >= 0:
                    draw_cell(surf, gx, gy, color)

def draw_next_preview_on_board(surf, font, next_mat, next_color):
    px, py = 8, 8
    box_w, box_h = 140, 110
    box = pygame.Rect(px, py, box_w, box_h)

    pygame.draw.rect(surf, (18, 18, 18), box, border_radius=10)
    pygame.draw.rect(surf, (90, 90, 90), box, 2, border_radius=10)

    label = font.render("NEXT", True, (200, 200, 200))
    surf.blit(label, (px + 10, py + 8))

    preview_cell = 18
    filled = [(r, c) for r in range(4) for c in range(4) if next_mat[r][c]]
    if not filled:
        return
    min_r = min(r for r, _ in filled)
    min_c = min(c for _, c in filled)
    max_r = max(r for r, _ in filled)
    max_c = max(c for _, c in filled)

    shape_w = (max_c - min_c + 1) * preview_cell
    shape_h = (max_r - min_r + 1) * preview_cell
    cx = px + (box_w - shape_w) // 2
    cy = py + 38 + (box_h - 38 - shape_h) // 2

    for r in range(4):
        for c in range(4):
            if next_mat[r][c]:
                x = cx + (c - min_c) * preview_cell
                y = cy + (r - min_r) * preview_cell
                rect = pygame.Rect(x, y, preview_cell, preview_cell)
                pygame.draw.rect(surf, next_color, rect)
                pygame.draw.rect(surf, (20, 20, 20), rect, 2)

def draw_side_panel(surf, title_font, font, score, lines, music_on):
    panel_x = GRID_W * CELL
    pygame.draw.rect(surf, (15, 15, 15), pygame.Rect(panel_x, 0, SIDE_W, WIN_H))
    pygame.draw.line(surf, (80, 80, 80), (panel_x, 0), (panel_x, WIN_H), 2)

    x0 = panel_x + 16
    y = 18

    title = title_font.render("SCORE", True, (220, 220, 220))
    surf.blit(title, (x0, y))
    y += 40

    score_big = title_font.render(str(score), True, WHITE)
    surf.blit(score_big, (x0, y))
    y += 55

    lines_img = font.render(f"Lines: {lines}", True, WHITE)
    surf.blit(lines_img, (x0, y))
    y += 30

    mus = "ON" if music_on else "OFF"
    mus_img = font.render(f"Music: {mus}  (M)", True, (200, 200, 200))
    surf.blit(mus_img, (x0, y))

def draw_game_over_overlay(surf, title_font, font, score, lines, reason_text):
    overlay = pygame.Surface((GRID_W * CELL, GRID_H * CELL), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 190))
    surf.blit(overlay, (0, 0))

    box_w, box_h = 320, 250
    box_x = (GRID_W * CELL - box_w) // 2
    box_y = (GRID_H * CELL - box_h) // 2
    box = pygame.Rect(box_x, box_y, box_w, box_h)

    pygame.draw.rect(surf, (25, 25, 25), box, border_radius=14)
    pygame.draw.rect(surf, (120, 120, 120), box, 2, border_radius=14)

    title = title_font.render("GAME OVER", True, (255, 90, 90))
    surf.blit(title, (box_x + (box_w - title.get_width()) // 2, box_y + 16))

    reason = font.render(reason_text, True, (220, 220, 220))
    surf.blit(reason, (box_x + 24, box_y + 70))

    info1 = font.render(f"Final Score : {score}", True, WHITE)
    info2 = font.render(f"Total Lines : {lines}", True, WHITE)
    surf.blit(info1, (box_x + 24, box_y + 105))
    surf.blit(info2, (box_x + 24, box_y + 135))

    hint1 = font.render("Press R to Restart", True, (200, 200, 200))
    hint2 = font.render("Press ESC or Q to Quit", True, (200, 200, 200))
    surf.blit(hint1, (box_x + 24, box_y + 185))
    surf.blit(hint2, (box_x + 24, box_y + 210))

def init_music():
    try:
        pygame.mixer.init()
    except pygame.error:
        print("[안내] 오디오 초기화 실패: 음악 없이 진행합니다.")
        return False

    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.set_volume(MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
        return True
    except pygame.error:
        print(f"[안내] 음악 파일 로드 실패: {MUSIC_PATH} (게임은 정상 실행)")
        return False

def toggle_music(music_on):
    if not pygame.mixer.get_init():
        return False
    if music_on:
        pygame.mixer.music.pause()
        return False
    pygame.mixer.music.unpause()
    return True

def reset_game():
    grid = clone_grid()
    score = 0
    lines = 0
    cur_key, cur_mat, cur_color, cur_x, cur_y = spawn_piece()
    next_key, next_mat, next_color, _, _ = spawn_piece()
    fall_timer = 0
    game_over = False
    game_over_reason = ""
    return grid, score, lines, (cur_key, cur_mat, cur_color, cur_x, cur_y), (next_key, next_mat, next_color), fall_timer, game_over, game_over_reason

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Tetris (pygame)")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 20)
    title_font = pygame.font.SysFont("consolas", 34, bold=True)
    over_font = pygame.font.SysFont("consolas", 38, bold=True)

    music_on = init_music()

    grid, score, lines, cur, nxt, fall_timer, game_over, reason = reset_game()
    cur_key, cur_mat, cur_color, cur_x, cur_y = cur
    next_key, next_mat, next_color = nxt

    running = True
    while running:
        dt = clock.tick(FPS)
        fall_timer += dt

        keys = pygame.key.get_pressed()
        fall_ms = FALL_MS_SOFT if (not game_over and keys[pygame.K_DOWN]) else FALL_MS_NORMAL

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                if event.key == pygame.K_m:
                    music_on = toggle_music(music_on)

                if game_over and event.key == pygame.K_r:
                    grid, score, lines, cur, nxt, fall_timer, game_over, reason = reset_game()
                    cur_key, cur_mat, cur_color, cur_x, cur_y = cur
                    next_key, next_mat, next_color = nxt
                    continue

                if game_over:
                    continue

                if event.key == pygame.K_LEFT:
                    if can_place(grid, cur_mat, cur_x - 1, cur_y):
                        cur_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if can_place(grid, cur_mat, cur_x + 1, cur_y):
                        cur_x += 1
                elif event.key == pygame.K_UP:
                    cur_mat, cur_x = try_rotate(grid, cur_mat, cur_x, cur_y)
                elif event.key == pygame.K_SPACE:
                    while can_place(grid, cur_mat, cur_x, cur_y + 1):
                        cur_y += 1
                    lock_piece(grid, cur_mat, cur_x, cur_y, cur_color)

                    grid, cleared = clear_lines(grid)
                    if cleared:
                        lines += cleared
                        score += score_for_clears(cleared)

                    # 종료조건: "맨 윗 행(0행)에 블록이 있으면"
                    if top_row_filled(grid):
                        game_over = True
                        reason = "Top row filled."
                        continue

                    # 다음 블록
                    cur_key, cur_mat, cur_color, cur_x, cur_y = next_key, next_mat, next_color, GRID_W // 2 - 2, -2
                    next_key, next_mat, next_color, _, _ = spawn_piece()

        if not game_over and fall_timer >= fall_ms:
            fall_timer = 0
            if can_place(grid, cur_mat, cur_x, cur_y + 1):
                cur_y += 1
            else:
                lock_piece(grid, cur_mat, cur_x, cur_y, cur_color)

                grid, cleared = clear_lines(grid)
                if cleared:
                    lines += cleared
                    score += score_for_clears(cleared)

                # 종료조건: "맨 윗 행(0행)에 블록이 있으면"
                if top_row_filled(grid):
                    game_over = True
                    reason = "Top row filled."
                else:
                    cur_key, cur_mat, cur_color, cur_x, cur_y = next_key, next_mat, next_color, GRID_W // 2 - 2, -2
                    next_key, next_mat, next_color, _, _ = spawn_piece()

        draw_grid(screen, grid)
        if not game_over:
            draw_piece(screen, cur_mat, cur_x, cur_y, cur_color)

        draw_next_preview_on_board(screen, font, next_mat, next_color)
        draw_side_panel(screen, title_font, font, score, lines, music_on)

        if game_over:
            draw_game_over_overlay(screen, over_font, font, score, lines, reason)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
