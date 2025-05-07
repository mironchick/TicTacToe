import pygame
import sys
import time

pygame.init()

WIDTH, HEIGHT = 600, 700
BOARD_SIZE = 3
CELL_SIZE = WIDTH // BOARD_SIZE
LINE_WIDTH = 10
WIN_LINE_WIDTH = 15
X_WIDTH = 15
O_WIDTH = 10
ANIMATION_SPEED = 0.05

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BG_COLOR = (28, 28, 36)
LINE_COLOR = (70, 70, 90)
X_COLOR = (255, 85, 85)
O_COLOR = (85, 170, 255)
WIN_COLOR = (255, 255, 100)
TEXT_COLOR = (200, 200, 220)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крутые Крестики-Нолики")
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 60, bold=True)
small_font = pygame.font.SysFont('Arial', 30)


class TicTacToe:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'
        self.game_over = False
        self.winner = None
        self.win_line = None
        self.animation_progress = 0
        self.last_move_time = 0
        self.x_scores = []
        self.o_scores = []

    def reset(self):
        self.__init__()

    def draw_board(self):
        screen.fill(BG_COLOR)

        for i in range(1, BOARD_SIZE):
            pygame.draw.line(screen, LINE_COLOR,
                             (0, i * CELL_SIZE),
                             (WIDTH, i * CELL_SIZE),
                             LINE_WIDTH)
            pygame.draw.line(screen, LINE_COLOR,
                             (i * CELL_SIZE, 0),
                             (i * CELL_SIZE, HEIGHT - 100),
                             LINE_WIDTH)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == 'X':
                    self.draw_x(row, col)
                elif self.board[row][col] == 'O':
                    self.draw_o(row, col)

        if self.win_line and self.animation_progress < 1:
            self.animate_win_line()

        pygame.draw.rect(screen, (40, 40, 50), (0, HEIGHT - 100, WIDTH, 100))
        status_text = f"Ход: {self.current_player}"
        status_surface = font.render(status_text, True,
                                     X_COLOR if self.current_player == 'X' else O_COLOR)
        screen.blit(status_surface, (20, HEIGHT - 80))

        pygame.draw.rect(screen, (100, 100, 120), (WIDTH - 150, HEIGHT - 80, 130, 50))
        restart_text = small_font.render("Рестарт", True, WHITE)
        screen.blit(restart_text, (WIDTH - 140, HEIGHT - 70))

    def draw_x(self, row, col):
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2
        offset = CELL_SIZE // 3

        progress = min(1.0, (time.time() - self.last_move_time) / ANIMATION_SPEED)

        start_x1 = center_x - offset
        start_y1 = center_y - offset
        end_x1 = center_x + offset * progress
        end_y1 = center_y + offset * progress

        start_x2 = center_x + offset
        start_y2 = center_y - offset
        end_x2 = center_x - offset * progress
        end_y2 = center_y + offset * progress

        pygame.draw.line(screen, X_COLOR, (start_x1, start_y1),
                         (end_x1 if progress < 1 else center_x + offset,
                          end_y1 if progress < 1 else center_y + offset),
                         X_WIDTH)
        pygame.draw.line(screen, X_COLOR, (start_x2, start_y2),
                         (end_x2 if progress < 1 else center_x - offset,
                          end_y2 if progress < 1 else center_y + offset),
                         X_WIDTH)

    def draw_o(self, row, col):
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3

        progress = min(1.0, (time.time() - self.last_move_time) / ANIMATION_SPEED)

        pygame.draw.circle(screen, O_COLOR, (center_x, center_y),
                           int(radius * progress), O_WIDTH)

    def animate_win_line(self):
        if not self.win_line:
            return

        self.animation_progress = min(1.0, self.animation_progress + 0.02)

        start_row, start_col, end_row, end_col, direction = self.win_line

        start_x = start_col * CELL_SIZE + CELL_SIZE // 2
        start_y = start_row * CELL_SIZE + CELL_SIZE // 2
        end_x = end_col * CELL_SIZE + CELL_SIZE // 2
        end_y = end_row * CELL_SIZE + CELL_SIZE // 2

        if direction == 'row':
            animated_end_x = start_x + (end_x - start_x) * self.animation_progress
            pygame.draw.line(screen, WIN_COLOR,
                             (start_x, start_y),
                             (animated_end_x, start_y),
                             WIN_LINE_WIDTH)
        elif direction == 'col':
            animated_end_y = start_y + (end_y - start_y) * self.animation_progress
            pygame.draw.line(screen, WIN_COLOR,
                             (start_x, start_y),
                             (start_x, animated_end_y),
                             WIN_LINE_WIDTH)
        elif direction == 'diag_down':
            animated_end_x = start_x + (end_x - start_x) * self.animation_progress
            animated_end_y = start_y + (end_y - start_y) * self.animation_progress
            pygame.draw.line(screen, WIN_COLOR,
                             (start_x, start_y),
                             (animated_end_x, animated_end_y),
                             WIN_LINE_WIDTH)
        elif direction == 'diag_up':
            animated_end_x = start_x + (end_x - start_x) * self.animation_progress
            animated_end_y = start_y - (start_y - end_y) * self.animation_progress
            pygame.draw.line(screen, WIN_COLOR,
                             (start_x, start_y),
                             (animated_end_x, animated_end_y),
                             WIN_LINE_WIDTH)

    def make_move(self, row, col):
        if self.game_over or self.board[row][col] is not None:
            return False

        self.board[row][col] = self.current_player
        self.last_move_time = time.time()

        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
            self.show_win_effect()
            return True

        if self.is_board_full():
            self.game_over = True
            return True

        self.switch_player()
        return True

    def check_win(self, row, col):
        if all(self.board[row][c] == self.current_player for c in range(BOARD_SIZE)):
            self.win_line = (row, 0, row, BOARD_SIZE - 1, 'row')
            return True

        if all(self.board[r][col] == self.current_player for r in range(BOARD_SIZE)):
            self.win_line = (0, col, BOARD_SIZE - 1, col, 'col')
            return True

        if row == col and all(self.board[i][i] == self.current_player for i in range(BOARD_SIZE)):
            self.win_line = (0, 0, BOARD_SIZE - 1, BOARD_SIZE - 1, 'diag_down')
            return True

        if row + col == BOARD_SIZE - 1 and all(
                self.board[i][BOARD_SIZE - 1 - i] == self.current_player for i in range(BOARD_SIZE)):
            self.win_line = (0, BOARD_SIZE - 1, BOARD_SIZE - 1, 0, 'diag_up')
            return True

        return False

    def is_board_full(self):
        return all(self.board[row][col] is not None
                   for row in range(BOARD_SIZE) for col in range(BOARD_SIZE))

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def show_win_effect(self):
        pass

    def show_win_message(self):
        if not self.winner:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        win_text = font.render(f"Игрок {self.winner} победил!", True, WIN_COLOR)
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(win_text, text_rect)

        pygame.draw.rect(screen, (100, 100, 120), (WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 60))
        restart_text = font.render("Играть снова", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

        return restart_rect

    def show_draw_message(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        draw_text = font.render("Ничья!", True, WHITE)
        text_rect = draw_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(draw_text, text_rect)

        pygame.draw.rect(screen, (100, 100, 120), (WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 60))
        restart_text = font.render("Играть снова", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(restart_text, restart_rect)

        return restart_rect


def main():
    game = TicTacToe()
    running = True
    restart_rect = None

    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_over:
                    if restart_rect and restart_rect.collidepoint(mouse_pos):
                        game.reset()
                        restart_rect = None
                else:
                    if WIDTH - 150 <= mouse_pos[0] <= WIDTH - 20 and HEIGHT - 80 <= mouse_pos[1] <= HEIGHT - 30:
                        game.reset()
                    else:
                        if mouse_pos[1] < HEIGHT - 100:
                            col = mouse_pos[0] // CELL_SIZE
                            row = mouse_pos[1] // CELL_SIZE
                            game.make_move(row, col)

        game.draw_board()

        if game.game_over:
            if game.winner:
                restart_rect = game.show_win_message()
            else:
                restart_rect = game.show_draw_message()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()