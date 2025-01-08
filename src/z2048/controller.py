from abc import ABC, abstractmethod
from typing import Tuple

import random
import pygame # type: ignore
import math
import time

class Controller(ABC):
    @abstractmethod
    def update(self, board:list[list[int]], score: int) -> str:
        return random.choice(["left", "right", "up", "down"])


class Human(Controller):
    def __init__(self) -> None:
        super().__init__()

    def update(self, board:list[list[int]], score: int) -> str:
        pressedKeys = pygame.key.get_pressed()
        if pressedKeys[pygame.K_LEFT]:
            return "left"
        if pressedKeys[pygame.K_RIGHT]: 
            return "right"
        if pressedKeys[pygame.K_UP]:
            return "up"
        if pressedKeys[pygame.K_DOWN]:
            return "down"
        return ""

class MCTS():
    root_node: 'Node'
    weights = {
            "monotonicity": 1.0,  # Original default values
            "smoothness": 0.1,
            "empty": 2.7,
            "max_corner": 5.0,
            "max_tile": 1.0,
    }
    
    def __init__(self, board: list[list[int]], alpha: float, beta: float) -> None:
        self.root_node = self.Node(None, "root", board)
        self.alpha = alpha
        self.beta = beta
    
    def update(self, board: list[list[int]], score: int) -> str:
        """
        Updates the MCTS root node and returns the best move after running simulations.
        """
        self.root_node = self.Node(None, "root", board)  # Update root node

        return self.run_mcts()

    def run_mcts(self, simulations: int = 8) -> str:
        """
        Runs MCTS simulations and returns the best move direction.
        Considers only moves that meet visit thresholds, have positive value, 
        and actually change the board state.
        """

        for _ in range(simulations):
            node = self.selection(self.root_node)
            score = self.simulate(node, steps=1000)
            self.backpropagate(node, score)

        valid_child = [
            child for child in self.root_node.child if child.board != self.root_node.board and child.visit > 0
        ]


        # if not valid_moves:
        if not valid_child:
            print("no valid move")
            move = random.choice(["left", "right", "up", "down"])
            return move

        # print(f"\n test ini")
        # for child in valid_child:
        # #     # print(f"{child.move_direction}: {0.9*self.evaluate_board(child.board) + 0.05*(child.value / child.visit)}")
        #     print(f"{child.move_direction}: {alpha * self.evaluate_board(child.board)} |  {beta * (child.value/child.visit)}")

        if valid_child:
            # best_child = max(valid_child, key=lambda n: self.evaluate_board(n.board, n.value, n.visit))
            best_child = max(valid_child, key=lambda n:(self.alpha * self.evaluate_board(n.board)) + self.beta * (n.value/n.visit))
            return best_child.move_direction
        # else:
        #     move = random.choice(valid_child)
        #     return move


    def evaluate_board(self, board):
        # Weights for each component (adjust as needed)
        WEIGHT_MONOTONICITY = self.weights.get('monotonicity')
        WEIGHT_SMOOTHNESS   = self.weights.get('smoothness')
        WEIGHT_EMPTY        = self.weights.get('empty')
        WEIGHT_MAX_CORNER   = self.weights.get('max_corner')
        WEIGHT_MAX_TILE     = self.weights.get('max_tile')

        rows = board
        cols = list(zip(*board))
        
        # Calculate number of empty cells
        empty_count = sum(row.count(0) for row in rows)
        
        # Identify the maximum tile
        max_tile = max(max(row) for row in rows)
        
        # Check if max tile is in a corner
        corners = [rows[0][0], rows[0][-1], rows[-1][0], rows[-1][-1]]
        max_in_corner = 1 if max_tile in corners else 0

        # if empty_count > 8:
        #     WEIGHT_EMPTY = 3.0
        if max_tile >= 1024:
            WEIGHT_MAX_CORNER = 6.0
        elif max_tile >= 2048:
            WEIGHT_MAX_CORNER = 7.0

        # Monotonicity calculation
        def monotonicity(grid):
            # Scores for all four directions
            totals = [0, 0, 0, 0]  # [up, down, left, right]

            # Up/Down monotonicity (iterate over columns)
            for y in range(len(grid[0])):  # y represents the column index
                current = 0
                next = current + 1
                while next < len(grid):
                    # Skip empty cells
                    while next < len(grid) and grid[next][y] == 0:
                        next += 1
                    if next >= len(grid):
                        break

                    # Current and next values in log2
                    current_value = math.log2(grid[current][y]) if grid[current][y] != 0 else 0
                    next_value = math.log2(grid[next][y]) if grid[next][y] != 0 else 0

                    if current_value > next_value:
                        totals[0] += next_value - current_value  # Upward monotonicity
                    elif next_value > current_value:
                        totals[1] += current_value - next_value  # Downward monotonicity

                    current = next
                    next += 1

            # Left/Right monotonicity (iterate over rows)
            for x in range(len(grid)):  # x represents the row index
                current = 0
                next = current + 1
                while next < len(grid[0]):
                    # Skip empty cells
                    while next < len(grid[0]) and grid[x][next] == 0:
                        next += 1
                    if next >= len(grid[0]):
                        break

                    # Current and next values in log2
                    current_value = math.log2(grid[x][current]) if grid[x][current] != 0 else 0
                    next_value = math.log2(grid[x][next]) if grid[x][next] != 0 else 0

                    if current_value > next_value:
                        totals[2] += next_value - current_value  # Leftward monotonicity
                    elif next_value > current_value:
                        totals[3] += current_value - next_value  # Rightward monotonicity

                    current = next
                    next += 1

            # Combine scores: max of up/down and max of left/right
            return max(totals[0], totals[1]) + max(totals[2], totals[3])

        
        # Smoothness calculation
        def smoothness(grid):
            smoothness = 0
            for x in range(len(grid)):
                for y in range(len(grid[0])):
                    if grid[x][y] != 0:
                        log_value = math.log2(grid[x][y])
                        # Compare with the right neighbor
                        if y + 1 < len(grid[0]) and grid[x][y + 1] != 0:
                            neighbor_log_value = math.log2(grid[x][y + 1])
                            smoothness -= abs(log_value - neighbor_log_value)
                        # Compare with the bottom neighbor
                        if x + 1 < len(grid) and grid[x + 1][y] != 0:
                            neighbor_log_value = math.log2(grid[x + 1][y])
                            smoothness -= abs(log_value - neighbor_log_value)
            return smoothness

        # Empty cells score
        empty_score = empty_count
        
        # Max tile score: Using log2 for scaling
        max_tile_score = math.log2(max_tile) if max_tile > 0 else 0

        # Combine the scores
        total_score = (WEIGHT_MONOTONICITY * monotonicity(rows)
                    + WEIGHT_SMOOTHNESS * smoothness(rows)
                    + WEIGHT_EMPTY * empty_score
                    + WEIGHT_MAX_CORNER * max_in_corner 
                    + WEIGHT_MAX_TILE * max_tile_score 
                    )
        
        return total_score

    def selection(self, current_node) -> 'Node':
        """
        Traverses the tree to a node that is expandable or a terminal node (game lost).
        """
        if current_node.is_terminal:
            return current_node  # Stop at terminal node
        
        while len(current_node.possible_move) == 0 and not current_node.is_terminal:  # Fully expanded and not terminal
            uct_values = [self.UCT(child) for child in current_node.child]
            max_uct_index = uct_values.index(max(uct_values))
            current_node = current_node.child[max_uct_index]
        
        
        return self.expand(current_node)

    def expand(self, current_node) -> 'Node':
        """
        Expands a node by creating a child for one unexplored move.
        Sets the child node's board as the result of the move in move_direction.
        """
        if len(current_node.possible_move) > 0:
            move_direction = random.choice(current_node.possible_move)
            new_board, score = self.simulate_move(current_node.board, move_direction)
            child_node = self.Node(parent=current_node, move_direction=move_direction, board=new_board)
            current_node.child.append(child_node)
            current_node.possible_move.remove(move_direction)
            
            return child_node
        return current_node

    # random 
    def simulate(self, node: 'Node', steps: int = 50) -> int:
        """
        Simulates a series of random moves starting from the given node.
        """
        current_board = [row[:] for row in node.board]  # Copy the current board state
        total_score = 0

        for _ in range(steps):
            move = random.choice(["left", "right", "up", "down"])
            new_board, score = self.simulate_move(current_board, move)

            # new_board, score = self.next_move(current_board)
            
            if new_board == current_board:
                # Skip invalid moves (no change)
                continue
            
            current_board = new_board
            total_score += score

        # node.simulation_evaluation += self.evaluate_board(current_board, node.value, node.visit)

        return total_score

    @staticmethod
    def simulate_move(board: list[list[int]], direction: str) -> tuple[list[list[int]], int]:
        """
        Simulates a move in the given direction on the board and returns the resulting board and score.
        """
        SIZE = len(board)
        
        def slide_row_left(row: list[int]) -> tuple[list[int], int]:
            score = 0
            new_row = [i for i in row if i != 0]  # Remove zeros
            new_row += [0] * (SIZE - len(new_row))  # Shift left

            for i in range(SIZE - 1):
                if new_row[i] == new_row[i + 1] and new_row[i] != 0:
                    new_row[i] *= 2
                    score += new_row[i]
                    new_row[i + 1] = 0

            new_row = [i for i in new_row if i != 0]  # Remove zeros again
            new_row += [0] * (SIZE - len(new_row))  # Fill with zeros
            return new_row, score
        
        def add_new_tile(board):
            SIZE = len(board)
            empty_tiles = [
                (r, c)
                for r in range(SIZE)
                for c in range(SIZE)
                if board[r][c] == 0
            ]
            if empty_tiles: # check whether empty or not
                row, col = random.choice(empty_tiles) # only add 1 tile by random
                board[row][col] = 2 if random.random() < 0.9 else 4 # 90% 2, 10% 4

        # Make a copy of the board to avoid mutating the original
        new_board = [row[:] for row in board]
        score_gained = 0

        if direction == "left":
            for i in range(SIZE):
                new_board[i], score = slide_row_left(new_board[i])
                score_gained += score
        elif direction == "right":
            for i in range(SIZE):
                new_board[i] = new_board[i][::-1]
                new_board[i], score = slide_row_left(new_board[i])
                new_board[i] = new_board[i][::-1]
                score_gained += score
        elif direction == "up":
            transposed = list(zip(*new_board))  # Transpose to handle columns
            for i in range(SIZE):
                row, score = slide_row_left(list(transposed[i]))
                transposed[i] = row
                score_gained += score
            new_board = [list(row) for row in zip(*transposed)]  # Transpose back
        elif direction == "down":
            transposed = list(zip(*new_board))  # Transpose to handle columns
            for i in range(SIZE):
                reversed_row = list(transposed[i])[::-1]
                row, score = slide_row_left(reversed_row)
                transposed[i] = row[::-1]
                score_gained += score
            new_board = [list(row) for row in zip(*transposed)]  # Transpose back

        if new_board != board:
            add_new_tile(new_board)

        return new_board, score_gained
    

    def backpropagate(self, node: 'Node', score: int):
        """
        Propagates the simulation result back up the tree.
        """
        while node is not None:
            node.visit += 1
            node.value += math.log2(score) if score != 0 else 0
            node = node.parent

    def UCT(self, node: 'Node') -> float:
        """
        Calculates the UCT value of a node.
        """
        if node.visit == 0:
            return float('inf')  # Encourage exploration of unvisited nodes
        return node.value / node.visit + math.sqrt(4 * math.log(node.parent.visit) / node.visit)


    class Node:
        # Attributes
        value: int
        visit: int
        board: list[list[int]]
        move_direction: str
        parent: 'Node'  # type: ignore
        child: list['Node']  # type: ignore
        possible_move: list[str]
        is_terminal: bool
        simulation_evaluation: float  # New field for simulation evaluation

        # Constructor
        def __init__(self, parent: 'Node' = None, move_direction: str = "root", board: list[list[int]] = None): # type: ignore
            self.value = 0
            self.visit = 0
            self.board = board
            self.parent = parent
            self.move_direction = move_direction
            self.child = []  # Initialize the child list
            self.possible_move = ["left", "right", "up", "down"]
            self.is_terminal = not self.check_moves_available()
            self.simulation_evaluation = 0.0

        def check_moves_available(self) -> bool:
            """
            Check if there are any valid moves left on the board.
            """
            if self.board is None:
                return False  # If the board is None, no moves are possible
            
            if any(0 in row for row in self.board):
                return True  # Empty tile exists

            for i in range(len(self.board)):
                for j in range(len(self.board) - 1):
                    if (self.board[i][j] == self.board[i][j + 1] or 
                        self.board[j][i] == self.board[j + 1][i]):
                        return True  # Adjacent tiles can merge
            return False
