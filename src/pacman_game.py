"""
Pacman Game Controller

This module contains the main game class, PacmanGame, which manages the
game loop, state, rendering, and player/enemy interactions.
"""

from src.pacman import Pacman
from src.ghost import Ghost

import os
import time
import keyboard
from copy import deepcopy

# Maps keyboard input keys to movement direction strings
move_dict = {
    'w': 'up',
    'a': 'left',
    's': 'down',
    'd': 'right',
}


class PacmanGame:
    """
    Manages the main game loop, game state, and rendering to the terminal.

    Attributes:
        game_map (list[list[str]]): The base map, storing walls and pellets.
        pacman_position (list[int]): Pacman's current [row, col] position.
        ghost_position (list[int]): The Ghost's current [row, col] position.
        block (int): A cooldown timer for Pacman's movement after hitting a wall.
        output_map (list[list[str]]): A copy of the game_map used for display,
                                      with Pacman 'P' and Ghost 'F' overlaid.
    """

    def __init__(self, game_map, pacman_position, ghost_position):
        """
        Initializes the PacmanGame.

        Args:
            game_map (list[list[str]]): The static game board.
            pacman_position (list[int]): The starting [row, col] for Pacman.
            ghost_position (list[int]): The starting [row, col] for the Ghost.
        """
        self.game_map = game_map
        self.pacman_position = pacman_position
        self.ghost_position = ghost_position
        self.block = 0  # Movement cooldown timer, starts at 0.
        self.output_map = None

    def __get_output_map(self):
        """
        Generates the display map by placing Pacman and the Ghost.

        Creates a deep copy of the base game_map and overlays the 'P' (Pacman)
        and 'F' (Ghost) characters at their current positions.

        Returns:
            list[list[str]]: The map to be printed to the console.
        """
        output_map = deepcopy(self.game_map)

        output_map[self.pacman_position[0]][self.pacman_position[1]] = 'P'
        output_map[self.ghost_position[0]][self.ghost_position[1]] = 'F'

        return output_map

    def print_game(self):
        """Prints the current game state (the output_map) to the console."""

        # Join each row into a string and print, separating characters with a space
        for row in self.output_map:
            print(" ".join(row))

        print("\n")  # Add a newline for spacing

        if self.block != 0:
            # Inform the player if their movement is on cooldown
            print(f"Movimento bloqueado por {self.block} rodadas")

    def __check_victory(self):
        """
        Checks if the player has won the game.

        Victory is achieved when no pellets ('.') remain on the base game_map.

        Returns:
            bool: True if all pellets are eaten, False otherwise.
        """
        for line in self.game_map:
            if "." in line:
                return False  # Found a pellet, game is not over
        return True  # No pellets found, player wins

    def run(self):
        """Starts and manages the main game loop."""

        # Generate the initial map for display
        self.output_map = self.__get_output_map()

        while True:
            # 1. Render the game
            self.print_game()

            # 2. Check for victory condition
            if not self.__check_victory():

                # 3. Wait for and process player input
                # keyboard.read_key() blocks until a key is pressed
                key_pressed = keyboard.read_key()
                if key_pressed in move_dict:
                    move = move_dict.get(key_pressed)

                    # 4. Calculate Pacman's move
                    # A new Pacman object is created to calculate the next state
                    game_map, output_map, pacman_position, block, lose = Pacman(
                        self.game_map, self.output_map,
                        self.pacman_position,
                        move, self.block
                    ).move_pacman()

                    # 5. Update game state from Pacman's move
                    self.game_map = game_map
                    self.output_map = output_map
                    self.pacman_position = pacman_position
                    self.block = block

                    # 6. Check for lose condition (Pacman hit by Ghost)
                    if lose:
                        print("VOCÊ PERDEU")
                        break

                    # 7. Calculate Ghost's move
                    # A new Ghost object is created to calculate its next move
                    output_map, ghost_position, lose = Ghost(
                        self.game_map,
                        self.output_map,
                        self.ghost_position
                    ).move_ghost()

                    # 8. Update game state from Ghost's move
                    self.output_map = output_map
                    self.ghost_position = ghost_position

                    # 9. Check for lose condition (Ghost hit Pacman)
                    if lose:
                        print("VOCÊ PERDEU")
                        break
            else:
                # Victory condition was met
                print("PARABENS VOCÊ VENCEU")
                break

            # 10. Clear the console for the next frame
            os.system('cls' if os.name == 'nt' else 'clear')