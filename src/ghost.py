"""
Ghost Class Module

This module defines the Ghost class, which encapsulates the logic for
enemy movement (AI), collision detection, and interaction with map objects.
"""

from random import choice
from copy import deepcopy

# Define tile types
GOOD_BLOCKS = [".", " "]  # Tiles the Ghost can move onto (pellets, empty space)
BAD_BLOCKS = ["="]  # Tiles the Ghost cannot move onto (walls)
ENEMY_BLOCKS = ["P"]  # The Ghost's target (Pacman)


class Ghost:
    """
    Handles the Ghost's movement logic for a single turn.

    This class is instantiated by the main game loop each turn to calculate
    the result of the Ghost's move. The AI is a simple random choice
    of available valid moves.
    """

    def __init__(self, game_map, output_map, ghost_position):
        """
        Initializes the Ghost move calculator.

        Args:
            game_map (list[list[str]]): The base map (walls, pellets).
            output_map (list[list[str]]): The display map (with 'P' and 'F').
            ghost_position (list[int]): The Ghost's current [row, col].
        """
        self.game_map = game_map
        self.output_map = output_map
        self.ghost_position = ghost_position
        self.lose = False  # Flag to indicate if the move results in a loss

    def __get_ghost_move_possibilities(self):
        """
        Checks all four adjacent tiles and finds valid moves.

        A valid move is any adjacent tile that is not a wall.

        Returns:
            list[str]: A list of valid move strings (e.g., ["up", "right"]).
        """
        possibilities = []
        pacman_column = [l[self.ghost_position[1]] for l in self.output_map]
        pacman_line = self.output_map[self.ghost_position[0]]

        # Check the tile content in all 4 directions
        up_status = pacman_column[self.ghost_position[0] - 1]
        down_status = pacman_column[self.ghost_position[0] + 1]
        left_status = pacman_line[self.ghost_position[1] - 1]
        right_status = pacman_line[self.ghost_position[1] + 1]

        factory_status = {
            "up": up_status,
            "down": down_status,
            "left": left_status,
            "right": right_status
        }

        # Build a list of moves that don't lead into a wall
        for possibility, possibility_value in factory_status.items():
            if possibility_value not in BAD_BLOCKS:
                possibilities.append(possibility)

        return possibilities

    def get_move(self):
        """
        The core Ghost AI.

        Randomly selects one move from the list of valid possibilities.

        Returns:
            str: The chosen move (e.g., "up", "down", "left", "right").
        """
        return choice(self.__get_ghost_move_possibilities())

    def get_next_ghost_position_location(self, move):
        """
        Calculates the destination [row, col] coordinates for the chosen move.

        Args:
            move (str): The chosen move direction.

        Returns:
            list[int]: The target [row, col] position.
        """
        next_up_position = [self.ghost_position[0] - 1, self.ghost_position[1]]
        next_down_position = [self.ghost_position[0] + 1, self.ghost_position[1]]
        next_left_position = [self.ghost_position[0], self.ghost_position[1] - 1]
        next_right_position = [self.ghost_position[0], self.ghost_position[1] + 1]

        factory_position = {
            "up": next_up_position,
            "down": next_down_position,
            "left": next_left_position,
            "right": next_right_position
        }

        return factory_position.get(move)

    def move_ghost(self):
        """
        Executes the Ghost's move for the turn.

        It gets a random valid move, calculates the new position,
        and checks if that position is the player. It then updates
        the output_map to reflect the Ghost's new position.

        Returns:
            tuple: A tuple containing the new game state:
                   (output_map, next_ghost_position_location, lose)
        """
        # 1. Get the random move
        chosen_move = self.get_move()

        # 2. Calculate the target position
        next_ghost_position_location = self.get_next_ghost_position_location(chosen_move)

        # 3. Check if the target is Pacman
        if self.output_map[next_ghost_position_location[0]][next_ghost_position_location[1]] in ENEMY_BLOCKS:
            self.lose = True  # Ghost caught Pacman

        # 4. Update the display map
        # Restore the original tile (e.g., '.' or ' ') from the base map
        current_pos = self.ghost_position
        self.output_map[current_pos[0]][current_pos[1]] = deepcopy(self.game_map[current_pos[0]][current_pos[1]])

        # Draw the Ghost 'F' in its new position
        new_pos = next_ghost_position_location
        self.output_map[new_pos[0]][new_pos[1]] = "F"

        response = (self.output_map, next_ghost_position_location, self.lose)

        return response