"""
Ghost Class Module

This module defines the base class for ghosts and their different AI personalities.
"""

import random
import collections
from typing import List, Tuple, Optional

UNKNOWN_TILE = "?"
WALL_TILE = "="
FLOOR_TILE = " "


class BaseGhost:
    """
    A base class for a ghost, handling memory, pathfinding, and basic movement logic.
    """

    MAX_VISION_RANGE = 4

    def __init__(
        self, pacman_game, initial_position: List[int], map_dimensions: Tuple[int, int]
    ) -> None:
        self.pacman_game = pacman_game
        self.position = initial_position
        map_height, map_width = map_dimensions
        self.memory = [
            [UNKNOWN_TILE for _ in range(map_width)] for _ in range(map_height)
        ]
        self.last_known_pacman_pos: Optional[List[int]] = None
        self.last_pacman_direction: Optional[str] = None

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
        other_ghost_positions = [
            g.position for g in self.pacman_game.ghosts if g is not self
        ]
        potential_moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1],
        }

        for move, new_pos in potential_moves.items():
            if not self.pacman_game.in_bounds(new_pos):
                continue
            if self.memory[new_pos[0]][new_pos[1]] == WALL_TILE:
                continue
            if new_pos in other_ghost_positions:
                continue
            possibilities.append(move)
        return possibilities

    def _check_vision(self, target_pos: List[int]) -> Optional[str]:
        ghost_r, ghost_c = self.position
        target_r, target_c = target_pos
        directions = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        for move_dir, (dr, dc) in directions.items():
            for i in range(1, self.MAX_VISION_RANGE + 1):
                check_r, check_c = ghost_r + dr * i, ghost_c + dc * i
                if (
                    not self.pacman_game.in_bounds([check_r, check_c])
                    or self.memory[check_r][check_c] == WALL_TILE
                ):
                    break
                if check_r == target_r and check_c == target_c:
                    return move_dir
        return None

    def _find_path(
        self, start_pos: List[int], target_pos: List[int]
    ) -> Optional[List[str]]:
        """
        Finds the shortest path from start to target using BFS on the ghost's memory.
        Returns the path as a list of moves (e.g., ['up', 'left', ...]).
        """
        if (
            not self.pacman_game.in_bounds(target_pos)
            or self.memory[target_pos[0]][target_pos[1]] == WALL_TILE
        ):
            return None

        q = collections.deque([(start_pos, [])])
        visited = {tuple(start_pos)}

        while q:
            current_pos, path = q.popleft()

            if current_pos == target_pos:
                return path

            r, c = current_pos
            potential_moves = {
                "up": [r - 1, c],
                "down": [r + 1, c],
                "left": [r, c - 1],
                "right": [r, c + 1],
            }

            for move, next_pos in potential_moves.items():
                if tuple(next_pos) not in visited and self.pacman_game.in_bounds(
                    next_pos
                ):
                    # Ghosts can only pathfind through what they know is a floor.
                    if self.memory[next_pos[0]][next_pos[1]] == FLOOR_TILE:
                        visited.add(tuple(next_pos))
                        new_path = path + [move]
                        q.append((next_pos, new_path))
        return None

    def get_move(self) -> Optional[str]:
        raise NotImplementedError("Subclasses must implement their own get_move logic.")

    def move(self) -> bool:
        self._update_memory()
        chosen_move = self.get_move()
        if not chosen_move:
            return False

        r, c = self.position
        moves = {
            "up": [r - 1, c],
            "down": [r + 1, c],
            "left": [r, c - 1],
            "right": [r, c + 1],
        }
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

        # Fallback to exploration/random
        exploratory_moves = [
            m
            for m in possible_moves
            if self.memory[self.pacman_game.pacman_position[0]][
                self.pacman_game.pacman_position[1]
            ]
            == UNKNOWN_TILE
        ]
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

        # Update last known position if Pac-Man is visible
        if pacman_visible:
            self.last_known_pacman_pos = self.pacman_game.pacman_position

        if pacman_visible:
            pacman_r, pacman_c = self.pacman_game.pacman_position
            if pacman_visible == "up":
                pacman_r -= self.AMBUSH_LEAD
            elif pacman_visible == "down":
                pacman_r += self.AMBUSH_LEAD
            elif pacman_visible == "left":
                pacman_c -= self.AMBUSH_LEAD
            elif pacman_visible == "right":
                pacman_c += self.AMBUSH_LEAD
            if self.pacman_game.in_bounds([pacman_r, pacman_c]):
                target_pos = [pacman_r, pacman_c]

        # If Pac-Man is not visible but we have a last known position, predict his next move
        elif self.last_known_pacman_pos and self.pacman_game.pacman.last_move:
            r, c = self.last_known_pacman_pos
            moves = {
                "up": [r - 1, c],
                "down": [r + 1, c],
                "left": [r, c - 1],
                "right": [r, c + 1],
            }
            predicted_pos = moves.get(self.pacman_game.pacman.last_move)

            if (
                predicted_pos
                and self.pacman_game.in_bounds(predicted_pos)
                and self.memory[predicted_pos[0]][predicted_pos[1]] != WALL_TILE
            ):
                target_pos = predicted_pos
            else:  # If prediction is invalid, target last known spot
                target_pos = self.last_known_pacman_pos

        path = self._find_path(self.position, target_pos)
        if path:
            return path[0]

        return random.choice(possible_moves)


class StrategicGhost(BaseGhost):
    """
    Switches between patrolling and hunting (First-Order Logic).
    Rule: IF Distance(self, pacman) < HUNT_RADIUS THEN state=HUNT ELSE state=PATROL.
    """

    HUNT_RADIUS = 10

    def __init__(
        self,
        pacman_game,
        initial_position: List[int],
        map_dimensions: Tuple[int, int],
        patrol_point: List[int],
    ) -> None:
        super().__init__(pacman_game, initial_position, map_dimensions)
        self.state = "PATROL"
        self.patrol_point = patrol_point

    def get_move(self) -> Optional[str]:
        possible_moves = self._get_move_possibilities_from_memory()
        if not possible_moves:
            return None

        path_to_pacman = self._find_path(
            self.position, self.pacman_game.pacman_position
        )

        # Update last known position if a path exists (implies visibility or recent knowledge)
        if path_to_pacman:
            self.last_known_pacman_pos = self.pacman_game.pacman_position

        if path_to_pacman and len(path_to_pacman) < self.HUNT_RADIUS:
            self.state = "HUNT"
        else:
            self.state = "PATROL"

        if self.state == "HUNT":
            if path_to_pacman:
                target_pos = self.pacman_game.pacman_position
            # If no path, predict based on last known position and Pac-Man's last move
            elif self.last_known_pacman_pos and self.pacman_game.pacman.last_move:
                r, c = self.last_known_pacman_pos
                moves = {
                    "up": [r - 1, c],
                    "down": [r + 1, c],
                    "left": [r, c - 1],
                    "right": [r, c + 1],
                }
                target_pos = moves.get(
                    self.pacman_game.pacman.last_move, self.last_known_pacman_pos
                )
            else:  # Fallback to patrol if no info
                target_pos = self.patrol_point
        else:  # PATROL state
            target_pos = self.patrol_point

        path_to_target = self._find_path(self.position, target_pos)
        if path_to_target:
            return path_to_target[0]

        return random.choice(possible_moves)
