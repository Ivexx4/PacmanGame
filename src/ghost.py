"""
Ghost Class Module

This module defines the Ghost class, which encapsulates the logic for
enemy movement (AI), collision detection, and interaction with map objects.

Each ghost has its own memory of the map, which it builds by exploring.
"""

import random
from typing import List, Tuple, Optional

ENEMY_BLOCKS = ["😋"]  # The Ghost's target (Pacman)
UNKNOWN_TILE = '?'
WALL_TILE = '='
FLOOR_TILE = ' '

class Ghost:
    """
    Calculates and applies the ghost's movement per turn, learning the map over time.
    """

    MAX_VISION_RANGE = 4

    def __init__(self, pacman_game, initial_position: List[int], map_dimensions: Tuple[int, int]) -> None:
        """
        Initializes the Ghost.

        Args:
            pacman_game: The main PacmanGame instance.
            initial_position: The starting [row, col] of the ghost.
            map_dimensions: A tuple of (height, width) for the map.
        """
        self.pacman_game = pacman_game
        self.position = initial_position

        # Initialize memory: a grid of unknown tiles
        map_height, map_width = map_dimensions
        self.memory = [[UNKNOWN_TILE for _ in range(map_width)] for _ in range(map_height)]

    def _update_memory(self) -> None:
        """
        The ghost "looks" at its current and adjacent tiles and updates its memory.
        """
        r, c = self.position
        # Update current tile
        self.memory[r][c] = FLOOR_TILE

        # Look at adjacent tiles
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            check_r, check_c = r + dr, c + dc
            if self.pacman_game.in_bounds([check_r, check_c]):
                is_wall = self.pacman_game.tiles[check_r][check_c].is_original_wall
                self.memory[check_r][check_c] = WALL_TILE if is_wall else FLOOR_TILE

    def _get_move_possibilities_from_memory(self) -> List[str]:
        """
        Returns a list of valid move directions based on the ghost's memory.
        It will not move into a known wall, but may try to move into an unknown tile.
        """
        possibilities: List[str] = []
        r, c = self.position

        potential_moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1]
        }

        for move, (new_r, new_c) in potential_moves.items():
            if self.pacman_game.in_bounds([new_r, new_c]):
                if self.memory[new_r][new_c] != WALL_TILE:
                    possibilities.append(move)

        return possibilities

    def _check_vision(self) -> Optional[str]:
        """
        Checks if Pac-Man is within line of sight, using the ghost's memory of walls.
        """
        pacman_r, pacman_c = self.pacman_game.pacman_position
        ghost_r, ghost_c = self.position

        directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}

        for move_dir, (dr, dc) in directions.items():
            for i in range(1, self.MAX_VISION_RANGE + 1):
                check_r, check_c = ghost_r + dr * i, ghost_c + dc * i

                if not self.pacman_game.in_bounds([check_r, check_c]):
                    break
                
                if self.memory[check_r][check_c] == WALL_TILE:
                    break

                if check_r == pacman_r and check_c == pacman_c:
                    return move_dir

        return None

    def get_move(self) -> Optional[str]:
        """
        Determines the ghost's next move based on vision and memory.
        """
        self._update_memory()

        possible_moves = self._get_move_possibilities_from_memory()
        if not possible_moves:
            return None

        seen_direction = self._check_vision()
        if seen_direction and seen_direction in possible_moves:
            return seen_direction

        # Prioritize exploring unknown tiles
        exploratory_moves = []
        r, c = self.position
        for move in possible_moves:
            moves_map = {"up": [r - 1, c], "down": [r + 1, c], "left": [r, c - 1], "right": [r, c + 1]}
            next_pos = moves_map[move]
            if self.memory[next_pos[0]][next_pos[1]] == UNKNOWN_TILE:
                exploratory_moves.append(move)
        
        if exploratory_moves:
            return random.choice(exploratory_moves)

        return random.choice(possible_moves)

    def move(self) -> bool:
        """
        Executes a single turn of logic and movement for the Ghost.
        Returns True if Pac-Man is caught.
        """
        chosen_move = self.get_move()
        if not chosen_move:
            return False

        r, c = self.position
        moves = {"up": [r - 1, c], "down": [r + 1, c], "left": [r, c - 1], "right": [r, c + 1]}
        new_pos = moves.get(chosen_move)

        if not new_pos or not self.pacman_game.in_bounds(new_pos):
            return False

        if self.pacman_game.is_movement_blocked(self.position, new_pos):
            self.memory[new_pos[0]][new_pos[1]] = WALL_TILE
            return False

        self.position = new_pos

        if self.position == self.pacman_game.pacman_position:
            return True

        return False
