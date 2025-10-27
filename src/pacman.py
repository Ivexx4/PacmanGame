"""
Pacman Class Module

This module defines the Pacman class, which encapsulates the logic for
player movement, collision detection, and interaction with map objects.
"""

# Define tile types
GOOD_BLOCKS = [".", " "]  # Tiles Pacman can move onto (pellets, empty space)
BAD_BLOCKS = ["="]  # Tiles Pacman cannot move onto (walls)
ENEMY_BLOCKS = ["F"]  # Tiles that cause Pacman to lose (ghosts)


class Pacman:
    """
    Handles Pacman's movement logic for a single turn.

    This class is instantiated by the main game loop each turn to calculate
    the result of a player's intended move.
    """

    def __init__(self, game_map, output_map, pacman_position, move, block):
        """
        Initializes the Pacman move calculator.

        Args:
            game_map (list[list[str]]): The base map (walls, pellets).
            output_map (list[list[str]]): The display map (with 'P' and 'F').
            pacman_position (list[int]): Pacman's current [row, col].
            move (str): The intended move ("up", "down", "left", "right").
            block (int): The current movement cooldown timer.
        """
        self.game_map = game_map
        self.output_map = output_map
        self.pacman_position = pacman_position
        self.move = move
        self.block = block
        self.lose = False  # Flag to indicate if the move results in a loss

    @property
    def current_move_status(self):
        """
        Checks the type of block at the target destination.

        Returns:
            str: The character on the output_map at the destination tile
                 (e.g., '=', '.', 'F', ' ').
        """
        pacman_column = [l[self.pacman_position[1]] for l in self.output_map]
        pacman_line = self.output_map[self.pacman_position[0]]

        up_status = pacman_column[self.pacman_position[0] - 1]
        down_status = pacman_column[self.pacman_position[0] + 1]
        left_status = pacman_line[self.pacman_position[1] - 1]
        right_status = pacman_line[self.pacman_position[1] + 1]

        factory_status = {
            "up": up_status,
            "down": down_status,
            "left": left_status,
            "right": right_status
        }

        return factory_status.get(self.move)

    @property
    def next_pacman_position_location(self):
        """
        Calculates the destination [row, col] coordinates for the move.

        Returns:
            list[int]: The target [row, col] position.
        """
        next_up_position = [self.pacman_position[0] - 1, self.pacman_position[1]]
        next_down_position = [self.pacman_position[0] + 1, self.pacman_position[1]]
        next_left_position = [self.pacman_position[0], self.pacman_position[1] - 1]
        next_right_position = [self.pacman_position[0], self.pacman_position[1] + 1]

        factory_position = {
            "up": next_up_position,
            "down": next_down_position,
            "left": next_left_position,
            "right": next_right_position
        }

        return factory_position.get(self.move)

    def _validate_move(self):
        """
        Validates the intended move and updates state flags.

        - If the destination is a wall, sets a 2-turn move block.
        - If the destination is an enemy, sets the lose flag.
        - If the destination is valid (good), returns True.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        if self.current_move_status in BAD_BLOCKS:
            self.block = 2  # Set 2-turn cooldown for hitting a wall
            return False

        elif self.current_move_status in ENEMY_BLOCKS:
            self.lose = True  # Player moved onto a ghost
            return False

        elif self.current_move_status in GOOD_BLOCKS:
            return True  # Move is valid

    def move_pacman(self):
        """
        Executes Pacman's move for the turn.

        If Pacman is on a move cooldown, it decrements the timer.
        If not on cooldown, it validates the move.
        If the move is valid, it updates the game_map (removes pellet)
        and output_map (moves 'P') and updates the pacman_position.

        Returns:
            tuple: A tuple containing the new game state:
                   (game_map, output_map, pacman_position, block, lose)
        """
        if self.block != 0:
            # Player is on cooldown, decrement timer and do nothing else
            self.block -= 1
            response = (self.game_map, self.output_map, self.pacman_position, self.block, self.lose)
        else:
            # Player is not on cooldown, attempt to move
            if self._validate_move():
                # Move is valid, update maps

                # Erase pellet '.' from the base map
                self.game_map[self.pacman_position[0]][self.pacman_position[1]] = " "

                # Erase 'P' from old position on display map
                self.output_map[self.pacman_position[0]][self.pacman_position[1]] = " "

                # Draw 'P' on new position on display map
                new_pos = self.next_pacman_position_location
                self.output_map[new_pos[0]][new_pos[1]] = "P"

                response = (self.game_map, self.output_map, new_pos, self.block, self.lose)

            else:
                # Move was invalid (hit wall) or player lost
                response = (self.game_map, self.output_map, self.pacman_position, self.block, self.lose)

        return response