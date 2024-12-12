import pygame # type: ignore
import random
from dataclasses import dataclass
from z2048.controller import Controller, Human, MCTS

@dataclass
class GameConfig:
    SIZE: int = 4
    TILE_SIZE: int = 100
    GAP_SIZE: int = 10
    MARGIN: int = 20
    BACKGROUND_COLOR: tuple[int, int, int] = (255, 251, 240)
    EMPTY_TILE_COLOR: tuple[int, int, int] = (205, 192, 180)
    FONT_COLOR: tuple[int, int, int] = (0, 0, 0)
    SCORE_COLOR: tuple[int, int, int] = (119, 110, 101)


class Game2048:
    TILE_COLORS = {
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 204, 97),
        512: (237, 200, 80),
        1024: (237, 197, 63),
        2048: (237, 194, 46),
    }

    def __init__(self, controller: Controller):
        pygame.init()
        self.config = GameConfig()
        self.screen_size = (
            self.config.SIZE * self.config.TILE_SIZE
            + (self.config.SIZE + 1) * self.config.GAP_SIZE
            + 2 * self.config.MARGIN
        )
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size + 60))
        pygame.display.set_caption("2048")
        self.font = pygame.font.SysFont("arial", 40)
        self.score_font = pygame.font.SysFont("arial", 24)
        self.board = [[0] * self.config.SIZE for _ in range(self.config.SIZE)]
        self.score = 0
        self.controller = controller
        self.init_game()

    def init_game(self):
        self.board = [[0] * self.config.SIZE for _ in range(self.config.SIZE)] # initializing board 2 x 2 array
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def draw_tile(self, value: int, x: int, y: int):
        color = self.TILE_COLORS.get(value, (60, 58, 50)) # (60, 58,50) -> default value
        rect = pygame.Rect(x, y, self.config.TILE_SIZE, self.config.TILE_SIZE) # width, height 
        pygame.draw.rect(self.screen, color, rect)
        if value != 0:
            text = self.font.render(str(value), True, self.config.FONT_COLOR)
            text_rect = text.get_rect( # Return the size and offset of rendered text
                center=(x + self.config.TILE_SIZE / 2, y + self.config.TILE_SIZE / 2)
            )
            self.screen.blit(text, text_rect)

    def draw_score(self):
        score_text = self.score_font.render(
            f"Score: {self.score}", True, self.config.SCORE_COLOR
        )
        self.screen.blit(score_text, (20, self.screen_size + 20))

    def draw_board(self):
        self.screen.fill(self.config.BACKGROUND_COLOR)
        for row in range(self.config.SIZE):
            for col in range(self.config.SIZE):
                value = self.board[row][col]
                x = ( # x screen
                    self.config.MARGIN
                    + self.config.GAP_SIZE
                    + col * (self.config.TILE_SIZE + self.config.GAP_SIZE)
                    # + col * (self.config.TILE_SIZE)
                )
                y = ( # y screen
                    self.config.MARGIN
                    + self.config.GAP_SIZE
                    + row * (self.config.TILE_SIZE + self.config.GAP_SIZE)
                )
                self.draw_tile(value, x, y)
        self.draw_score()

    def add_new_tile(self):
        empty_tiles = [
            (r, c)
            for r in range(self.config.SIZE)
            for c in range(self.config.SIZE)
            if self.board[r][c] == 0
        ]
        if empty_tiles: # check whether empty or not
            row, col = random.choice(empty_tiles) # only add 1 tile by random
            self.board[row][col] = 2 if random.random() < 0.9 else 4 # 90% 2, 10% 4

    def slide_row_left(self, row: list[int]) -> tuple[list[int], int]:
        score = 0
        new_row = [i for i in row if i != 0] # take != 0 value
        new_row += [0] * (self.config.SIZE - len(new_row)) # shift to left and add 0 to the rest

        for i in range(self.config.SIZE - 1):
            if new_row[i] == new_row[i + 1] and new_row[i] != 0:
                new_row[i] *= 2
                score += new_row[i]
                new_row[i + 1] = 0

        new_row = [i for i in new_row if i != 0]
        new_row += [0] * (self.config.SIZE - len(new_row))
        return new_row, score

    #DEBUG
    def print_board(self, board):
        for row in board:
            print(row)
        print()

    def move(self, direction: str) -> bool:
        original_board = [row[:] for row in self.board]

        # board
        # [.......]
        # [.......]
        # [.......]
        # [.......]

        score_gained = 0

        if direction == "left":
            for i in range(self.config.SIZE):
                self.board[i], score = self.slide_row_left(self.board[i])
                score_gained += score
        elif direction == "right":
            for i in range(self.config.SIZE):
                self.board[i] = self.board[i][::-1]
                self.board[i], score = self.slide_row_left(self.board[i])
                self.board[i] = self.board[i][::-1]
                score_gained += score
        elif direction == "up":
            self.board = list(zip(*self.board))
            # * self.board -> unpack each row (unpacking operator)
            # zip -> aggregate element for each row 
            # therefore this will transpose the matrix
            # self.print_board(self.board)

            for i in range(self.config.SIZE):
                row, score = self.slide_row_left(list(self.board[i]))
                self.board[i] = row
                score_gained += score
            self.board = [list(row) for row in zip(*self.board)]

        elif direction == "down":
            self.board = list(zip(*self.board)) # transpose 
            for i in range(self.config.SIZE):
                self.board[i] = list(self.board[i])[::-1] # reverse 
                row, score = self.slide_row_left(self.board[i])
                self.board[i] = row[::-1] # reveres 
                score_gained += score
            self.board = [list(row) for row in zip(*self.board)] # transpose

        if self.board != original_board:
            self.score += score_gained
            return True
        return False

    def check_moves_available(self) -> bool:
        if any(0 in row for row in self.board):
            return True

        for i in range(self.config.SIZE):
            for j in range(self.config.SIZE - 1):
                if (
                    self.board[i][j] == self.board[i][j + 1]
                    or self.board[j][i] == self.board[j + 1][i]
                ):
                    return True
        return False

    def run(self):
        clock = pygame.time.Clock()
        running = True
        lost = False

        while running:
            moved = False
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
                if isinstance(self.controller, Human) and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        moved = self.move("left") # function move 
                    elif event.key == pygame.K_RIGHT:
                        moved = self.move("right")
                    elif event.key == pygame.K_UP:
                        moved = self.move("up")
                    elif event.key == pygame.K_DOWN:
                        moved = self.move("down")
        
            if not isinstance(self.controller, Human):
                # Debug (step by step)
                # waiting_for_input = True
                # while waiting_for_input:
                #     for event in pygame.event.get():
                #         if event.type == pygame.QUIT:
                #             pygame.quit()
                #             exit(0)
                #         if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                #             waiting_for_input = False
                # AI_move_direction = self.controller.update(self.board, self.score)
                # moved = self.move(AI_move_direction)
                # print(f"AI choose to move: {AI_move_direction}, result: ")
                # Debug

                # Real below
                moved = self.move(self.controller.update(self.board, self.score))
                # Real end

            if moved:
                self.add_new_tile()
                # DEBUG check moved result
                # for row in self.board:
                #     print(row)
                # print(f"--------------------------\n")
                # DEBUG
                lost = not self.check_moves_available()

            self.draw_board()

            if lost:
                print(f"score {self.score}")
                exit(0)

            pygame.display.flip()
            clock.tick(60)
            # clock.tick(30)

        pygame.quit()

class RandomPlayer(Controller):
    def __init__(self) -> None:
        super().__init__()

    def update(self, board:list[list[int]], score: int) -> str:
        return random.choice(["left", "right", "up", "down"])

class AIPlayer(Controller):

    def __init__(self) -> None:
        super().__init__()
        self.mcts = None

    
    def update(self, board: list[list[int]], score: int) -> str:
        if self.mcts is None:
            self.mcts = MCTS(board)
        return self.mcts.update(board, score)
    # def update(self, board:list[list[int]], score: int) -> str: #mungkin di sini kasih referensi ke game itself
    #     testMCTS = MCTS(board)
    #     # Debug
    #     print("Root node board: ")
    #     for row in testMCTS.root_node.board:
    #         print(row)
    #     print()
    #     # DEBUG
    #     return random.choice(["left", "right", "up", "down"])

if __name__ == "__main__":
    # 人間でプレイしたいとき
    # Game2048(Human()).run()

    # ランダムプレイヤーでプレイしたいとき
    # Game2048(RandomPlayer()).run()
    Game2048(AIPlayer()).run()

    # testMCTS = MCTS()
    # testMCTS.test_printnode()
