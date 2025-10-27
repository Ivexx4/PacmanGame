"""
Pytest tests for the Ghost class.

This file specifically tests the ghost's movement logic:
- Finding valid move possibilities
- Moving to a new tile
- Colliding with Pacman
"""

from src.ghost import Ghost
from copy import deepcopy


def test_ghost_finds_valid_moves():
    """Tests the ghost's ability to see open vs. blocked paths."""
    test_map = [
        ['=', '=', '=', '=', '='],
        ['=', ' ', '=', ' ', '='],
        ['=', ' ', 'F', ' ', '='],  # Ghost at [2, 2]
        ['=', ' ', '=', ' ', '='],
        ['=', '=', '=', '=', '=']
    ]
    # In this map, the ghost has 3 valid moves: up, left, right. 'down' is a wall.

    g = Ghost(test_map, test_map, ghost_position=[2, 2])

    # We test the "private" method __get_ghost_move_possibilities
    # Note: Pacman ('P') is also a valid move tile for a ghost.

    possibilities = g._Ghost__get_ghost_move_possibilities()

    assert "up" in possibilities
    assert "left" in possibilities
    assert "right" in possibilities
    assert "down" not in possibilities  # Blocked by wall at [3, 2]
    assert len(possibilities) == 3


def test_ghost_is_corralled():
    """Tests that the ghost finds no valid moves when walled in."""
    test_map = [
        ['=', '=', '='],
        ['=', 'F', '='],
        ['=', '=', '=']
    ]
    g = Ghost(test_map, test_map, ghost_position=[1, 1])
    possibilities = g._Ghost__get_ghost_move_possibilities()

    # A ghost with no moves will cause an error with random.choice
    # This test confirms it finds no moves.
    # A more robust 'get_move' would handle an empty list.
    assert len(possibilities) == 0


def test_ghost_hits_pacman():
    """Tests if the 'lose' flag is set when a Ghost moves onto Pacman."""

    # Create a map where the ONLY valid move for the ghost is onto Pacman.
    # This avoids randomness and forces the desired outcome.
    test_map = [
        ['=', '=', '='],
        ['=', 'P', '='],  # Pacman at [1, 1]
        ['=', 'F', '='],  # Ghost at [2, 1]
        ['=', '=', '=']
    ]
    # Base map for restoring the tile
    base_map = deepcopy(test_map)
    base_map[1][1] = " "  # Pacman's tile is just an empty space on base map
    base_map[2][1] = " "  # Ghost's tile is just an empty space on base map

    ghost_pos = [2, 1]

    # The only valid move for the Ghost is 'up'
    g = Ghost(base_map, test_map, ghost_pos)
    new_output_map, new_ghost_pos, lose = g.move_ghost()

    assert lose is True
    assert new_ghost_pos == [1, 1]
    assert new_output_map[2][1] == " "  # Ghost's old spot is restored
    assert new_output_map[1][1] == "F"  # Ghost is on Pacman's old spot


def test_ghost_restores_pellet_after_moving():
    """Tests that the ghost leaves a pellet behind if it was on one."""
    test_map = [
        ['=', '=', '='],
        ['=', '.', '='],
        ['=', 'F', '='],  # Ghost at [2, 1]
        ['=', '=', '=']
    ]
    # Base map for restoring the tile
    base_map = [
        ['=', '=', '='],
        ['=', '.', '='],
        ['=', '.', '='],  # Ghost starts on a pellet at [2, 1]
        ['=', '=', '=']
    ]

    ghost_pos = [2, 1]
    g = Ghost(base_map, test_map, ghost_pos)

    # The only valid move is 'up'
    new_output_map, new_ghost_pos, lose = g.move_ghost()

    assert lose is False
    assert new_ghost_pos == [1, 1]
    assert new_output_map[2][1] == "."  # Ghost's old spot is restored to a pellet
    assert new_output_map[1][1] == "F"  # Ghost is on the new spot