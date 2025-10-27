"""
Pacman Game - Entry Point

This script initializes and runs the Pacman game.
It defines the game map, sets the initial positions for Pacman and the Ghost,
and starts the main game loop from the PacmanGame class.

To run the game:
    python .
"""

from src.pacman_game import PacmanGame

# Define the starting position for Pacman [row, column]
p_start_position = [6, 1]

# Define the starting position for the Ghost [row, column]
f_start_position = [1, 6]

# Define the game map as a list of lists.
# Symbols:
#   '=': A wall (impassable)
#   '.': A pellet (collectible)
#   ' ': An empty space
game_map = [
    ['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '='],
    ['=', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '='],
    ['=', '.', '=', '=', '=', '=', '.', '.', '=', '.', '.', '='],
    ['=', '.', '=', '.', '.', '=', '.', '=', '=', '.', '.', '='],
    ['=', '.', '=', '.', '.', '=', '.', '=', '=', '.', '.', '='],
    ['=', '.', '=', '.', '.', '=', '.', '.', '=', '.', '.', '='],
    ['=', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '='],
    ['=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=', '=']]

# Create an instance of the game and run it.
PacmanGame(game_map, p_start_position, f_start_position).run()