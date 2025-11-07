"""
Ghost Class Module

This module defines the base class for ghosts and their different AI personalities.
"""

import random
from typing import List, Tuple, Optional

UNKNOWN_TILE = '?'
WALL_TILE = '='
FLOOR_TILE = ' '

class BaseGhost:
    """
    A base class for a ghost, handling memory and basic movement logic.
    This class is not meant to be instantiated directly.
    """

    MAX_VISION_RANGE = 4

    def __init__(self, pacman_game, initial_position: List[int], map_dimensions: Tuple[int, int]) -> None:
        self.pacman_game = pacman_game
        self.position = initial_position
        map_height, map_width = map_dimensions
        self.memory = [[UNKNOWN_TILE for _ in range(map_width)] for _ in range(map_height)]

    def _update_memory(self) -> None:
        r, c = self.position
        self.memory[r][c] = FLOOR_TILE
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            check_r, check_c = r + dr, c + dc
            if self.pacman_game.in_bounds([check_r, check_c]):
                is_wall = self.pacman_game.tiles[check_r][check_c].is_original_wall
                self.memory[check_r][check_c] = WALL_TILE if is_wall else FLOOR_TILE

    def _get_move_possibilities_from_memory(self) -> List[str]:
        possibilities: List[str] = []
        r, c = self.position
        potential_moves = {"up": [r - 1, c], "down": [r + 1, c], "left": [r, c - 1], "right": [r, c + 1]}
        for move, (new_r, new_c) in potential_moves.items():
            if self.pacman_game.in_bounds([new_r, new_c]) and self.memory[new_r][new_c] != WALL_TILE:
                possibilities.append(move)
        return possibilities

    def _check_vision(self, target_pos: List[int]) -> Optional[str]:
        ghost_r, ghost_c = self.position
        target_r, target_c = target_pos
        directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        for move_dir, (dr, dc) in directions.items():
            for i in range(1, self.MAX_VISION_RANGE + 1):
                check_r, check_c = ghost_r + dr * i, ghost_c + dc * i
                if not self.pacman_game.in_bounds([check_r, check_c]) or self.memory[check_r][check_c] == WALL_TILE:
                    break
                if check_r == target_r and check_c == target_c:
                    return move_dir
        return None

    def get_move(self) -> Optional[str]:
        raise NotImplementedError("Subclasses must implement their own get_move logic.")

    def move(self) -> bool:
        self._update_memory()
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
        return self.position == self.pacman_game.pacman_position

class HunterGhost(BaseGhost):
    """
    Hunts Pac-Man directly (Propositional Logic).
    Rule: IF Pac-Man is seen, THEN move towards him.
    """
    def get_move(self) -> Optional[str]:
        possible_moves = self._get_move_possibilities_from_memory()
        if not possible_moves:
            return None

        seen_direction = self._check_vision(self.pacman_game.pacman_position)
        if seen_direction and seen_direction in possible_moves:
            return seen_direction

        exploratory_moves = [m for m in possible_moves if self.memory[self.pacman_game.pacman_position[0]][self.pacman_game.pacman_position[1]] == UNKNOWN_TILE]
        if exploratory_moves:
            return random.choice(exploratory_moves)

        return random.choice(possible_moves)

class AmbusherGhost(BaseGhost):
    """
    Tries to get ahead of Pac-Man (Propositional Logic).
    Rule: IF Pac-Man is seen, THEN move to where he is going.
    """
    AMBUSH_LEAD = 4

    def get_move(self) -> Optional[str]:
        possible_moves = self._get_move_possibilities_from_memory()
        if not possible_moves:
            return None

        pacman_visible = self._check_vision(self.pacman_game.pacman_position)
        target_pos = self.pacman_game.pacman_position

        if pacman_visible:
            pacman_r, pacman_c = self.pacman_game.pacman_position
            if pacman_visible == "up": pacman_r -= self.AMBUSH_LEAD
            elif pacman_visible == "down": pacman_r += self.AMBUSH_LEAD
            elif pacman_visible == "left": pacman_c -= self.AMBUSH_LEAD
            elif pacman_visible == "right": pacman_c += self.AMBUSH_LEAD
            
            if self.pacman_game.in_bounds([pacman_r, pacman_c]):
                target_pos = [pacman_r, pacman_c]

        best_move = None
        min_dist = float('inf')
        r, c = self.position
        moves_map = {"up": [r - 1, c], "down": [r + 1, c], "left": [r, c - 1], "right": [r, c + 1]}

        for move in possible_moves:
            new_pos = moves_map[move]
            dist = abs(new_pos[0] - target_pos[0]) + abs(new_pos[1] - target_pos[1])
            if dist < min_dist:
                min_dist = dist
                best_move = move

        if best_move:
            return best_move

        exploratory_moves = [m for m in possible_moves if self.memory[moves_map[m][0]][moves_map[m][1]] == UNKNOWN_TILE]
        if exploratory_moves:
            return random.choice(exploratory_moves)

        return random.choice(possible_moves)

class StrategicGhost(BaseGhost):
    """
    Switches between patrolling and hunting (First-Order Logic).
    Rule: IF Distance(self, pacman) < HUNT_RADIUS THEN state=HUNT ELSE state=PATROL.
    """
    HUNT_RADIUS = 8

    def __init__(self, pacman_game, initial_position: List[int], map_dimensions: Tuple[int, int], patrol_point: List[int]) -> None:
        super().__init__(pacman_game, initial_position, map_dimensions)
        self.state = 'PATROL'
        self.patrol_point = patrol_point

    def get_move(self) -> Optional[str]:
        possible_moves = self._get_move_possibilities_from_memory()
        if not possible_moves:
            return None

        # First-Order Logic: Update state based on relation (distance)
        dist_to_pacman = abs(self.position[0] - self.pacman_game.pacman_position[0]) + abs(self.position[1] - self.pacman_game.pacman_position[1])
        if dist_to_pacman < self.HUNT_RADIUS:
            self.state = 'HUNT'
        else:
            self.state = 'PATROL'

        # Set target based on state
        if self.state == 'HUNT':
            target_pos = self.pacman_game.pacman_position
        else: # PATROL
            target_pos = self.patrol_point

        # Move towards the target
        best_move = None
        min_dist = float('inf')
        r, c = self.position
        moves_map = {"up": [r - 1, c], "down": [r + 1, c], "left": [r, c - 1], "right": [r, c + 1]}

        for move in possible_moves:
            new_pos = moves_map[move]
            dist = abs(new_pos[0] - target_pos[0]) + abs(new_pos[1] - target_pos[1])
            if dist < min_dist:
                min_dist = dist
                best_move = move

        if best_move:
            return best_move

        return random.choice(possible_moves)
