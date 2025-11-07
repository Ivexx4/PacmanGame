"""
Main controller for the Pacman game.

This module contains the PacmanGame class, which manages the main loop,
player input, state updates, and rendering to the terminal.
"""

import os
import queue
import time
from typing import List

from pynput import keyboard

from .ghost import Ghost
from .pacman import Pacman

class Tile:
    """
    Represents a single tile in the game map, with walls on its borders.

    Attributes:
        has_pellet (bool): True if the tile contains a pellet.
        is_original_wall (bool): True if the tile was a wall in the initial map layout.
        wall_north, wall_south, wall_east, wall_west (bool): Wall presence on each border.
        display_char (str): The character to use for rendering this tile.
    """
    def __init__(self, character: str):
        self.has_pellet = (character == '.')
        self.is_original_wall = (character == '=')
        self.wall_north = False
        self.wall_south = False
        self.wall_east = False
        self.wall_west = False
        self.display_char = ' '  # Default display character

    def __str__(self) -> str:
        """Returns the display character for the tile."""
        return self.display_char

class PacmanGame:
    """
    Manages the main game loop and state.
    """

    def __init__(self, game_map, pacman_position: List[int], ghosts_positions: List[List[int]]) -> None:
        """
        Initializes the game.
        """
        self.tiles: List[List[Tile]] = [[Tile(char) for char in row] for row in game_map]
        self.rows = len(self.tiles)
        self.cols = len(self.tiles[0]) if self.rows > 0 else 0
        self._initialize_borders()
        self._set_display_chars()

        self.pacman_position = pacman_position
        self.ghosts_positions = ghosts_positions
        self.score = 0
        self.output_map = None
        self.turn = "ghost"
        self.move_queue = queue.Queue(maxsize=1)
        self.possible_moves = []
        self.listener = keyboard.Listener(on_press=self.on_press, daemon=True)
        self.listener.start()

    def on_press(self, key):
        """Callback function for pynput listener. Puts valid moves into a queue."""
        move = None
        try:
            char_key = key.char
            if char_key in ['w', 'a', 's', 'd']:
                move = {'w': 'up', 'a': 'left', 's': 'down', 'd': 'right'}[char_key]
        except AttributeError:
            if key == keyboard.Key.up:
                move = 'up'
            elif key == keyboard.Key.down:
                move = 'down'
            elif key == keyboard.Key.left:
                move = 'left'
            elif key == keyboard.Key.right:
                move = 'right'
        
        if move and move in self.possible_moves and self.turn == 'pacman':
            try:
                self.move_queue.put_nowait(move)
            except queue.Full:
                pass

    def __get_possible_moves(self) -> List[str]:
        """Returns a list of valid move directions for Pac-Man."""
        moves = []
        r, c = self.pacman_position
        if not self.is_movement_blocked(self.pacman_position, [r - 1, c]):
            moves.append('up')
        if not self.is_movement_blocked(self.pacman_position, [r + 1, c]):
            moves.append('down')
        if not self.is_movement_blocked(self.pacman_position, [r, c - 1]):
            moves.append('left')
        if not self.is_movement_blocked(self.pacman_position, [r, c + 1]):
            moves.append('right')
        return moves

    def print_game(self) -> None:
        """Prints the game state to the terminal."""
        # Print a newline to ensure the cursor is at the start of a line before clearing.
        print()
        os.system('cls' if os.name == 'nt' else 'clear') 
        self.output_map = self.get_display_map(self.pacman_position, self.ghosts_positions)
        if not self.output_map:
            print("(Map not initialized)\n")
            return
        
        for row in self.output_map:
            line = []
            for char in row:
                line.append(char)
                # Emojis are wide characters; don't add a space after them.
                if char not in ['😋', '👻']:
                    line.append(' ')
            print("".join(line).rstrip())
        print(f"\nScore: {self.score}\n")
        if self.turn == 'pacman':
            self.possible_moves = self.__get_possible_moves()

    def __check_victory(self) -> bool:
        """Checks if all pellets have been collected."""
        for row in self.tiles:
            for tile in row:
                if tile.has_pellet:
                    return False
        return True

    def run(self) -> None:
        """
        Runs the main game loop.
        """
        try:
            # Initialize the output_map without printing it
            self.output_map = self.get_display_map(self.pacman_position, self.ghosts_positions)
            while True:
                if self.__check_victory():
                    print("CONGRATULATIONS, YOU WON!")
                    break

                if self.turn == "ghost":
                    time.sleep(0.5)
                    
                    new_ghost_positions = []
                    turn_output_map = self.output_map
                    
                    for ghost_pos in self.ghosts_positions:
                        ghost = Ghost(self, turn_output_map, ghost_pos)
                        map_after_move, new_ghost_pos, lose = ghost.move_ghost()
                        
                        turn_output_map = map_after_move
                        new_ghost_positions.append(new_ghost_pos)
                        
                        if lose:
                            self.ghosts_positions = new_ghost_positions
                            self.print_game()
                            print("YOU LOST")
                            return

                    self.ghosts_positions = new_ghost_positions
                    self.turn = "pacman"
                    self.print_game()

                elif self.turn == "pacman":
                    try:
                        move = self.move_queue.get(timeout=60)
                        self.move_queue.task_done()
                    except queue.Empty:
                        continue

                    _, output_map, pacman_position, lose = Pacman(
                        self, self.output_map, self.pacman_position, move
                    ).move_pacman()
                    self.output_map, self.pacman_position = output_map, pacman_position
                    
                    # Check for pellets at the new position and update score
                    if self.remove_pellet(self.pacman_position):
                        self.score += 10

                    if lose:
                        self.print_game()
                        print("YOU LOST")
                        break
                    self.turn = "ghost"
                    self.print_game()

        finally:
            self.listener.stop()

    def _initialize_borders(self):
        """
        Sets wall flags on tile borders by checking for transitions between wall and non-wall tiles
        in the original map layout.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                # Check for a wall to the south
                if r < self.rows - 1:
                    if self.tiles[r][c].is_original_wall != self.tiles[r + 1][c].is_original_wall:
                        self.tiles[r][c].wall_south = True
                        self.tiles[r + 1][c].wall_north = True
                # Check for a wall to the east
                if c < self.cols - 1:
                    if self.tiles[r][c].is_original_wall != self.tiles[r][c + 1].is_original_wall:
                        self.tiles[r][c].wall_east = True
                        self.tiles[r][c + 1].wall_west = True

    def _set_display_chars(self):
        """
        Sets the character for displaying each tile, including oriented walls.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                if tile.is_original_wall:
                    # Display oriented walls for original wall tiles
                    has_neighbor_up = r > 0 and self.tiles[r - 1][c].is_original_wall
                    has_neighbor_down = r < self.rows - 1 and self.tiles[r + 1][c].is_original_wall
                    has_neighbor_left = c > 0 and self.tiles[r][c - 1].is_original_wall
                    has_neighbor_right = c < self.cols - 1 and self.tiles[r][c + 1].is_original_wall
 
                    is_vertical = has_neighbor_up or has_neighbor_down
                    is_horizontal = has_neighbor_left or has_neighbor_right
 
                    if is_vertical and not is_horizontal:
                        tile.display_char = '|'
                    elif is_horizontal and not is_vertical:
                        tile.display_char = '-'
                    else:
                        tile.display_char = '+'
                elif tile.has_pellet:
                    tile.display_char = '.'
                else:
                    tile.display_char = ' '

    def in_bounds(self, pos: List[int]) -> bool:
        """Returns True if the position is within the map boundaries."""
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_movement_blocked(self, from_pos: List[int], to_pos: List[int]) -> bool:
        """Checks if movement between two adjacent tiles is blocked by a wall or map bounds."""
        if not self.in_bounds(to_pos):
            return True  # Movement out of bounds is always blocked

        r_from, c_from = from_pos
        r_to, c_to = to_pos
        tile_from = self.tiles[r_from][c_from]

        if r_to == r_from - 1: return tile_from.wall_north
        if r_to == r_from + 1: return tile_from.wall_south
        if c_to == c_from - 1: return tile_from.wall_west
        if c_to == c_from + 1: return tile_from.wall_east

        return True  # Non-adjacent movement is not allowed

    def get_tile_char(self, row: int, col: int) -> str:
        """Returns the display character of the tile at the given position."""
        return self.tiles[row][col].display_char

    def remove_pellet(self, pos: List[int]) -> bool:
        """Removes a pellet from the given position and returns True if a pellet was removed."""
        if self.in_bounds(pos):
            r, c = pos
            tile = self.tiles[r][c]
            if tile.has_pellet:
                tile.has_pellet = False
                if not tile.is_original_wall:
                    tile.display_char = ' '
                return True
        return False

    def copy_tiles_as_str(self) -> List[List[str]]:
        """Returns a copy of the map's display characters."""
        return [[str(tile) for tile in row] for row in self.tiles]

    def get_display_map(self, pacman_pos: List[int], ghosts_positions: List[List[int]]) -> List[List[str]]:
        """
        Returns a copy of the map as characters with Pac-Man and the Ghost overlaid.
        """
        out = self.copy_tiles_as_str()
        if self.in_bounds(pacman_pos):
            r, c = pacman_pos
            out[r][c] = '😋' 
        # Place all ghosts on the map
        for ghost_pos in ghosts_positions:
            if self.in_bounds(ghost_pos):
                r, c = ghost_pos
                out[r][c] = '👻'
        return out
