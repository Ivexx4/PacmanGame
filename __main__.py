"""
Pacman Game - Entry Point

This script initializes and runs the Pacman game.
It defines the game map, sets the initial positions for Pacman and the Ghost,
and starts the main game loop from the PacmanGame class.

To run the game:
    python -m src
"""

from src.pacman_game import PacmanGame
from src.map_generator import MapGenerator

# Generates the map
map_generator = MapGenerator(10, 10)
game_map = map_generator.generate()

# Get starting positions for Pac-Man and ghosts
p_start_position, ghost_start_positions = map_generator.get_start_positions()

# Create an instance of the game and run it.
PacmanGame(game_map, p_start_position, ghost_start_positions).run()
