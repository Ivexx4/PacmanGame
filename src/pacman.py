"""
Pacman Class Module

This module defines the Pacman class, responsible for:
- validating player movement attempts,
- applying changes to the map (removing pellets),
- updating the display map (output_map).
"""

from typing import List, Tuple, Optional

# Define tile types
ENEMY_BLOCKS = ["👻"]  # Tiles that cause Pacman to lose (ghosts)


class Pacman:
    """
    Calculates and applies Pacman's movement per turn.

    Main methods:
        - _validate_move: checks if the intended move is allowed.
        - move_pacman: applies the move and updates maps/state.
    """

    def __init__(
        self, pacman_game, output_map, pacman_position: List[int], move: str
    ) -> None:
        """
        Initializes the Pacman movement calculator.

        Args:
            pacman_game: PacmanGame instance (provides base tiles and utilities).
            output_map: current display map (with 'P' and 'F').
            pacman_position: current Pacman position [row, col].
            move: desired direction ("up", "down", "left", "right").
        """
        self.pacman_game = pacman_game
        self.output_map = output_map
        self.pacman_position = pacman_position
        self.move = move
        self.last_move: Optional[str] = None
        self.lose = False  # Flag to indicate if the move results in a loss

    @property
    def next_pacman_position_location(self) -> Optional[List[int]]:
        """
        Calculates the target position based on the stored move direction.

        Returns:
            [row, col] of the target position or None if the direction is invalid.
        """
        r, c = self.pacman_position
        moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1],
        }
        return moves.get(self.move)

    def _validate_move(self) -> bool:
        """
        Validates the intended move by checking for walls and enemies.
        """
        new_pos = self.next_pacman_position_location
        if new_pos is None:
            return False

        # Check for walls using the border-based method
        if self.pacman_game.is_movement_blocked(self.pacman_position, new_pos):
            return False

        # Check for enemies on the display map
        if self.output_map[new_pos[0]][new_pos[1]] in ENEMY_BLOCKS:
            self.lose = True
            # This is a valid move, but it results in a loss
            return True

        return True

    def move_pacman(self) -> Tuple[object, List[List[str]], List[int], bool]:
        """
        Executes a single tile of movement for Pacman.
        """
        if not self._validate_move():
            return self.pacman_game, self.output_map, self.pacman_position, self.lose

        new_pos = self.next_pacman_position_location
        if new_pos is None:
            return self.pacman_game, self.output_map, self.pacman_position, self.lose

        # If the move results in a loss, update state and return
        if self.lose:
            return self.pacman_game, self.output_map, self.pacman_position, self.lose

        # Update output_map: the old position becomes an empty space.
        r_old, c_old = self.pacman_position
        self.output_map[r_old][c_old] = " "

        # Place Pacman on the new tile
        self.output_map[new_pos[0]][new_pos[1]] = "😋"

        self.last_move = self.move

        return self.pacman_game, self.output_map, new_pos, self.lose
