from abc import ABC, abstractmethod
from typing import Tuple

import random
import pygame # type: ignore
import math

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
    # Attribute 
    root_node: 'Node'

    def __init__(self, board: list[list[int]] = None) -> None:
        self.root_node = self.Node(None, "root", board)
    
    def update(self, board: list[list[int]], score: int) -> str:
        """
        Updates the MCTS root node and returns the best move after running simulations.
        """
        self.root_node = self.Node(None, "root", board)  # Update root node

        return self.run_mcts()

    # def update(self, board: list[list[int]], score: int) -> str:
    #     """
    #     Updates the MCTS root node while reusing part of the tree if possible.
    #     If a child node matches the current board, it becomes the new root.
    #     Otherwise, reset the tree.
    #     """
    #     # Search for a matching child node in the current root
    #     matching_child = None
    #     for child in self.root_node.child:
    #         if child.board == board:
    #             matching_child = child
    #             break

    #     if matching_child:
    #         # Reuse the matching child as the new root
    #         self.root_node = matching_child
    #         self.root_node.parent = None  # Detach it from the previous root
    #         print("Reused a matching child node as the new root.")
    #     else:
    #         # No matching child found, reset the tree
    #         self.root_node = self.Node(None, "root", board)
    #         print("Reset the tree: no matching child found.")

    #     # Run MCTS simulations and return the best move
    #     return self.run_mcts()
    
    def run_mcts(self, simulations: int = 100) -> str:
        """
        Runs MCTS simulations and returns the best move direction.
        Considers only moves that meet visit thresholds, have positive value, 
        and actually change the board state.
        """
        # Step 1: Precompute valid moves
        valid_moves = [
            move for move in ["left", "right", "up", "down"]
            if self.is_move_valid(self.root_node.board, move)
        ]

        if not valid_moves:
            # If no valid moves exist, return a default move (game over scenario)
            return "left"

        # Step 2: Run MCTS simulations
        for _ in range(simulations):
            node = self.selection(self.root_node)
            score = self.simulate(node, steps=50)
            self.backpropagate(node, score)

        # Step 3: Filter eligible children based on:
        # - Minimum visit threshold (3)
        # - Positive value
        # - The move must be in the list of valid moves
        eligible_children = [
            child for child in self.root_node.child
            if child.visit >= 3
            and child.value > 0
            and child.move_direction in valid_moves
        ]

        # Debug: Print eligible children details
        # print()
        # for child in eligible_children:
        #     print(f"{child.move_direction}, avg: {child.value / child.visit}, visit: {child.visit}, value: {child.value}")

        # Step 4: Select the best move
        if eligible_children:
            # Select the child with the highest average value
            best_child = max(eligible_children, key=lambda n: n.value / n.visit)
            print(f"best child: {best_child.move_direction}")
            return best_child.move_direction
        else:
            random_direction = random.choice(valid_moves)
            print(f"random: {random_direction}") 
            # Fallback: Select a move from the list of valid moves
            return random_direction

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
            # Choose one unexplored move
            move_direction = random.choice(current_node.possible_move)
            
            # Simulate the move to get the resulting board
            new_board, score = self.simulate_move(current_node.board, move_direction)
            
            # Create the child node with the updated board
            child_node = self.Node(parent=current_node, move_direction=move_direction, board=new_board)
            
            # Add the child to the current node and remove the move from possible moves
            current_node.child.append(child_node)
            current_node.possible_move.remove(move_direction)
            
            return child_node
        return current_node

    def simulate(self, node: 'Node', steps: int = 50) -> int:
        """
        Simulates a series of random moves starting from the given node.
        """
        current_board = [row[:] for row in node.board]  # Copy the current board state
        total_score = 0

        for _ in range(steps):
            move = random.choice(valid_moves)
            new_board, score = self.simulate_move(current_board, move)
            
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
