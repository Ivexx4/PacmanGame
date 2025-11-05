"""
Pacman Game - Entry Point

This script initializes and runs the Pacman game.
It defines the game map, sets the initial positions for Pacman and the Ghost,
and starts the main game loop from the PacmanGame class.

To run the game:
    python -m src
"""

from src.pacman_game import PacmanGame

# Define the starting position for Pacman [row, column]
p_start_position = [6, 1]

# Define the starting positions for the Ghosts as a list of [row, column]
ghost_start_positions = [[1, 6], [1, 1]]

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
PacmanGame(game_map, p_start_position, ghost_start_positions).run()
