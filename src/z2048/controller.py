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
    
    def update(self, board:list[list[int]], score: int) -> str:
        return random.choice(["left", "right", "up", "down"])
    
    def test_printnode(self):
        # parent_node = self.Node(None, "root")
        # print("from instantiated")
        # child_node = self.expand(parent_node)
        # print(self.root_node.move_direction)
        
        # give root 4 child node 
        for i in range(4):
            child_node = self.expand(self.root_node)
            child_node.value = random.randrange(10)
            child_node.visit += 1
            # print(child_node.value)
            # print(child_node.visit)
            # print()
        
        # set random value and add visit value
        for child in self.root_node.child:
            self.root_node.visit += child.visit
            self.root_node.value += child.value
            print(child.move_direction)
        print()
        # print("root")
        # print(self.root_node.value)
        # print(self.root_node.visit)

        selected = self.selection(self.root_node)
        self.backtrack(selected)

    # Debug only
    def backtrack(self, current_node):
        current_node = current_node
        while(current_node.parent != None):
            print(current_node.move_direction)
            current_node = current_node.parent
        print(current_node.move_direction)

    # haven't consider the terminal condition
    def selection(self, current_node): # until explandable node or terminal (game lost)
        current_node = current_node
        while len(current_node.possible_move) == 0:
            uct_value = []
            for child in current_node.child:
                uct_value.append(self.UCT(child))
                max_uct_index = uct_value.index(max(uct_value))
            print(uct_value)
            print()
            current_node = current_node.child[max_uct_index]
        current_node = self.expand(current_node)
        return current_node

    def expand(self, current_node) -> 'Node':
        if len(current_node.possible_move) > 0:
            child_move_direction = random.choice(current_node.possible_move)
            child_node = self.Node(parent=current_node, move_direction=child_move_direction)
            
            current_node.child.append(child_node)
            current_node.possible_move.remove(child_move_direction)
            
            return child_node
        else:
            return "error"
    
    def UCT(self, node: 'Node'):
        return node.value / node.visit * math.sqrt(2*math.log(node.parent.visit) / node.visit)

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
