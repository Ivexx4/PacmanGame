"""
Main controller for the Pacman game.

This module contains the PacmanGame class, which manages the main loop,
player input, state updates, and rendering to the terminal.
"""

from .pacman import Pacman
from .ghost import Ghost
from .map import Map
import os
from pynput import keyboard
from typing import List
import time
import queue

class PacmanGame:
    """
    Manages the main game loop and state.
    """

    def __init__(self, game_map, pacman_position: List[int], ghosts_positions: List[List[int]]) -> None:
        """
        Initializes the game.
        """
        if isinstance(game_map, Map):
            self.game_map = game_map
        else:
            self.game_map = Map(game_map)

        self.pacman_position = pacman_position
        self.ghosts = [Ghost(self.game_map, pos) for pos in ghosts_positions]
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
        if not self.game_map.is_movement_blocked(self.pacman_position, [r - 1, c]):
            moves.append('up')
        if not self.game_map.is_movement_blocked(self.pacman_position, [r + 1, c]):
            moves.append('down')
        if not self.game_map.is_movement_blocked(self.pacman_position, [r, c - 1]):
            moves.append('left')
        if not self.game_map.is_movement_blocked(self.pacman_position, [r, c + 1]):
            moves.append('right')
        return moves

    def print_game(self) -> None:
        """Prints the game state to the terminal."""
        # Print a newline to ensure the cursor is at the start of a line before clearing.
        print()
        os.system('cls' if os.name == 'nt' else 'clear') 
        ghost_positions = [ghost.ghost_position for ghost in self.ghosts]
        self.output_map = self.game_map.get_display_map(self.pacman_position, ghost_positions)
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
        print(f"Turn: {self.turn.capitalize()}'s Turn")

    def __check_victory(self) -> bool:
        """Checks if all pellets have been collected."""
        for row in self.game_map.tiles:
            for tile in row:
                if tile.has_pellet:
                    return False
        return True

    def run(self) -> None:
        """
        Runs the main game loop.
        """
        try:
            while True:
                self.print_game()

                if self.__check_victory():
                    print("CONGRATULATIONS, YOU WON!")
                    break

                if self.turn == "ghost":
                    time.sleep(0.5)
                    for ghost in self.ghosts:
                        self.output_map, lose = ghost.move_ghost(self.output_map)
                        if lose:
                            self.print_game()
                            print("YOU LOST")
                            # Use a return to exit the run method immediately
                            return
                    self.turn = "pacman"

                elif self.turn == "pacman":
                    try:
                        move = self.move_queue.get(timeout=60)
                        self.move_queue.task_done()
                    except queue.Empty:
                        continue

                    game_map_obj, output_map, pacman_position, lose = Pacman(
                        self.game_map, self.output_map, self.pacman_position, move
                    ).move_pacman()
                    self.game_map, self.output_map, self.pacman_position = game_map_obj, output_map, pacman_position
                    
                    if lose:
                        self.print_game()
                        print("YOU LOST")
                        break
                    self.turn = "ghost"

        finally:
            self.listener.stop()
