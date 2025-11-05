"""
Ghost Class Module

This module defines the Ghost class, which encapsulates the logic for
enemy movement (AI), collision detection, and interaction with map objects.
"""

from random import choice
from typing import List, Tuple, Optional

ENEMY_BLOCKS = ["😋"]  # The Ghost's target (Pacman)

class Ghost:
    """
    Calculates and applies the ghost's movement per turn.
    """

    def __init__(self, game_map, output_map, ghost_position: List[int]) -> None:
        """
        Initializes the Ghost movement calculator.

        Args:
            game_map: Map instance (provides tile and wall data).
            output_map: current display map.
            ghost_position: current Ghost position [row, col].
        """
        self.game_map = game_map
        self.output_map = output_map
        self.ghost_position = ghost_position
        self.lose = False  # Flag to indicate if the move results in a loss

    def __get_ghost_move_possibilities(self) -> List[str]:
        """
        Returns a list of valid move directions that are not blocked by walls.
        """
        possibilities: List[str] = []
        r, c = self.ghost_position

        potential_moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1]
        }

        for move, new_pos in potential_moves.items():
            # Ghosts should not be blocked by walls, but can move through other ghosts
            is_blocked = self.game_map.is_movement_blocked(self.ghost_position, new_pos)
            if not is_blocked:
                possibilities.append(move)

        return possibilities

    def get_move(self) -> Optional[str]:
        """
        Randomly selects one of the valid move possibilities.
        """
        return choice(self.__get_ghost_move_possibilities() or [None])

    def get_next_ghost_position(self, move: str) -> Optional[List[int]]:
        """
        Converts a move string into a target [row, col] position.
        """
        r, c = self.ghost_position
        moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1]
        }
        return moves.get(move)

    def move_ghost(self) -> Tuple[List[List[str]], List[int], bool]:
        """
        Executes a single tile of movement for the Ghost.
        """
        chosen_move = self.get_move()

        if chosen_move is None:
            return self.output_map, self.ghost_position, self.lose

        new_pos = self.get_next_ghost_position(chosen_move)
        if new_pos is None:
            return self.output_map, self.ghost_position, self.lose

        # Check for collision with Pacman
        if self.output_map[new_pos[0]][new_pos[1]] in ENEMY_BLOCKS:
            self.lose = True

        # Restore the base tile character at the ghost's old position
        r_cur, c_cur = self.ghost_position
        self.output_map[r_cur][c_cur] = self.game_map.get_tile_char(r_cur, c_cur)

        # Draw the ghost at the new position
        self.output_map[new_pos[0]][new_pos[1]] = "👻"

        return self.output_map, new_pos, self.lose
