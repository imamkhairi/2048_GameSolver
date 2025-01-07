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
            "monotonicity": 0.4,  # Original default values
            "smoothness": 2.5,
            "empty": 2.8,
            "max_corner": 0.9,
            "max_tile": 0.05,
            "node_average": 2.9,
            "node_access": 2.0
    }
    
    def __init__(self, board: list[list[int]] = None, weights: dict = None) -> None:
        self.root_node = self.Node(None, "root", board)
        if weights:
            self.weights = weights
    
    def update(self, board: list[list[int]], score: int) -> str:
        """
        Updates the MCTS root node and returns the best move after running simulations.
        """
        self.root_node = self.Node(None, "root", board)  # Update root node

        return self.run_mcts()

    def run_mcts(self, simulations: int = 50) -> str:
        """
        Runs MCTS simulations and returns the best move direction.
        Considers only moves that meet visit thresholds, have positive value, 
        and actually change the board state.
        """
        # valid_child = [
        # # valid_moves = [
        #     # move for move in ["left", "right", "up", "down"]
        #     # if self.is_move_valid(self.root_node.board, move)
            
        #     # child.move_direction for child in self.root_node.child
        #     # if child.board != self.root_node.board
        
        #     child for child in self.root_node.child if child.board != self.root_node.board
        
        # ]

        # # if not valid_moves:
        # if not valid_child:
        #     print("no valid move")
        #     return "left"

        for _ in range(simulations):
            node = self.selection(self.root_node)
            score = self.simulate(node, steps=150)
            self.backpropagate(node, score)

        valid_child = [
        # valid_moves = [
            # move for move in ["left", "right", "up", "down"]
            # if self.is_move_valid(self.root_node.board, move)
            
            # child.move_direction for child in self.root_node.child
            # if child.board != self.root_node.board
        
            child for child in self.root_node.child if child.board != self.root_node.board
        
        ]

        # if not valid_moves:
        if not valid_child:
            print("no valid move")
            move = random.choice(["left", "right", "up", "down"])
            return move

        # eligible_children = [
        #     child for child in self.root_node.child
        #     # and child.value > 0
        #     # and child.move_direction in valid_moves
        #     # if child.move_direction in valid_moves
        #     if child.visit >= 3 
        #     and child.value > 0
        # ]
        
        # print()
        # for child in self.root_node.child:
        #     print(f"move: {child.move_direction}, visit: {child.visit}, avg: {child.value/child.visit}")

        # if eligible_children:
        if valid_child:
            best_child = max(valid_child, key=lambda n: self.evaluate_board(n.board, n.value, n.visit))
            return best_child.move_direction
        # else:
        #     move = random.choice(valid_child)
        #     return move

    def evaluate_board(self, board, value, visit):
        start_time = time.time()

        # Weights for each component (adjust as needed)
        WEIGHT_MONOTONICITY = self.weights.get('monotonicity', 2.0)
        WEIGHT_SMOOTHNESS   = self.weights.get('smoothness', 2.0)
        WEIGHT_EMPTY        = self.weights.get('empty', 1.5)
        WEIGHT_MAX_CORNER   = self.weights.get('max_corner', 0.8)
        WEIGHT_MAX_TILE     = self.weights.get('max_tile', 0.5)
        WEIGHT_NODE_AVERAGE = self.weights.get('node_average', 1.3)
        WEIGHT_NODE_ACCESS = self.weights.get('node_access', 1.3)

        rows = board
        cols = list(zip(*board))
        
        # Calculate number of empty cells
        empty_count = sum(row.count(0) for row in rows)
        
        # Identify the maximum tile
        max_tile = max(max(row) for row in rows)
        
        # Check if max tile is in a corner
        corners = [rows[0][0], rows[0][-1], rows[-1][0], rows[-1][-1]]
        max_in_corner = 1 if max_tile in corners else 0

        # Monotonicity calculation
        def row_monotonicity(r):
            inc_cost = 0
            dec_cost = 0
            for i in range(len(r)-1):
                if r[i] > r[i+1]:
                    inc_cost += abs(r[i] - r[i+1])
                else:
                    dec_cost += abs(r[i] - r[i+1])
            return -min(inc_cost, dec_cost)

        monotonicity_score = 0
        for r in rows:
            monotonicity_score += row_monotonicity(r)
        for c in cols:
            monotonicity_score += row_monotonicity(c)
        
        # Smoothness calculation
        def smoothness_score_for_line(line):
            score_line = 0
            for i in range(len(line)-1):
                if line[i] != 0 and line[i+1] != 0:
                    score_line -= abs(line[i] - line[i+1])
            return score_line

        smoothness_score = 0
        for r in rows:
            smoothness_score += smoothness_score_for_line(r)
        for c in cols:
            c = list(c)
            smoothness_score += smoothness_score_for_line(c)
        
        # Empty cells score
        empty_score = empty_count
        
        # Max tile score: Using log2 for scaling
        max_tile_score = math.log2(max_tile) if max_tile > 0 else 0

        # Average node value (score/visit), safe division
        avg_node_value = value / visit if visit > 0 else 0

        # Combine the scores
        total_score = (WEIGHT_MONOTONICITY * monotonicity_score
                    + WEIGHT_SMOOTHNESS * smoothness_score
                    + WEIGHT_EMPTY * empty_score
                    + WEIGHT_MAX_CORNER * max_in_corner
                    + WEIGHT_MAX_TILE * max_tile_score
                    + WEIGHT_NODE_AVERAGE * avg_node_value
                    + WEIGHT_NODE_ACCESS * visit)
        
        end_time = time.time()

        print(f"Exec time = {end_time - start_time:.6f} seconds")
        return total_score


    def is_move_valid(self, board: list[list[int]], move_direction: str) -> bool:
        """
        Checks if applying move_direction to the board changes the board state.
        """
        # Simulate the move
        new_board, _ = self.simulate_move(board, move_direction)
        # Compare the new board with the original board
        return new_board != board

    def selection(self, current_node) -> 'Node':
        """
        Traverses the tree to a node that is expandable or a terminal node (game lost).
        """
        while len(current_node.possible_move) == 0 and not current_node.is_terminal:  # Fully expanded and not terminal
            uct_values = [self.UCT(child) for child in current_node.child]
            max_uct_index = uct_values.index(max(uct_values))
            current_node = current_node.child[max_uct_index]
        
        if current_node.is_terminal:
            return current_node  # Stop at terminal node
        
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
            node.value += score
            node = node.parent

    def UCT(self, node: 'Node') -> float:
        """
        Calculates the UCT value of a node.
        """
        if node.visit == 0:
            return float('inf')  # Encourage exploration of unvisited nodes
        return node.value / node.visit + math.sqrt(2 * math.log(node.parent.visit) / node.visit)


    class Node:
        # Attributes
        value: int
        visit: int
        board: list[list[int]]
        move_direction: str
        parent: 'Node'  # type: ignore
        child: list['Node'] # type: ignore
        possible_move: list[str]

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
