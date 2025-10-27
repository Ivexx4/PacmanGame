"""
Pytest tests for Pacman game logic.

This file tests the core mechanics of Pacman movement, Ghost collisions,
wall collisions, and the game's victory condition.
"""

# Import the classes you want to test from your 'src' folder
from src.pacman import Pacman
from src.ghost import Ghost
from src.pacman_game import PacmanGame


# --- Test Fixtures (Reusable Setups) ---

def create_test_map():
    """Helper function to create a clean, reusable map for testing."""
    return [
        ['=', '=', '=', '=', '='],
        ['=', 'P', '.', 'F', '='],  # P at [1,1], Pellet at [1,2], F at [1,3]
        ['=', ' ', '=', ' ', '='],
        ['=', '.', ' ', '.', '='],
        ['=', '=', '=', '=', '=']
    ]


# --- Pacman Tests ---

def test_pacman_moves_into_empty_space():
    """Tests if Pacman successfully moves into an empty space."""
    game_map = create_test_map()
    # Create an output map by overlaying P and F
    output_map = create_test_map()
    pacman_pos = [1, 1]

    # Intend to move 'down' into the empty space at [2, 1]
    p = Pacman(game_map, output_map, pacman_pos, move="down", block=0)
    new_game_map, new_output_map, new_pos, block, lose = p.move_pacman()

    assert new_pos == [2, 1]  # Pacman is in the new position
    assert new_output_map[1][1] == " "  # Old position is now empty
    assert new_output_map[2][1] == "P"  # New position has Pacman
    assert lose is False
    assert block == 0  # No block was applied


def test_pacman_eats_pellet():
    """Tests if Pacman eats a pellet and it disappears from the base map."""
    game_map = create_test_map()
    output_map = create_test_map()
    pacman_pos = [1, 1]

    # Intend to move 'right' into the pellet at [1, 2]
    p = Pacman(game_map, output_map, pacman_pos, move="right", block=0)
    new_game_map, new_output_map, new_pos, block, lose = p.move_pacman()

    assert new_pos == [1, 2]  # Pacman moved to the pellet's position
    assert new_game_map[1][1] == " "  # Old position on base map is empty
    assert new_game_map[1][2] == " "  # Pellet is GONE from the BASE map
    assert new_output_map[1][2] == "P"  # Pacman is on the display map
    assert lose is False


def test_pacman_hits_wall():
    """Tests if Pacman hits a wall and his movement is blocked."""
    game_map = create_test_map()
    output_map = create_test_map()
    pacman_pos = [1, 1]

    # Intend to move 'up' into the wall at [0, 1]
    p = Pacman(game_map, output_map, pacman_pos, move="up", block=0)
    new_game_map, new_output_map, new_pos, block, lose = p.move_pacman()

    assert new_pos == [1, 1]  # Pacman did NOT move
    assert block == 2  # A 2-turn block was applied
    assert lose is False

    # Test that the block timer counts down
    p = Pacman(new_game_map, new_output_map, new_pos, move="down", block=block)
    _, _, _, block, _ = p.move_pacman()
    assert block == 1  # Timer counted down


def test_pacman_hits_ghost():
    """Tests if the 'lose' flag is set when Pacman moves onto a Ghost."""
    game_map = create_test_map()
    output_map = create_test_map()
    pacman_pos = [1, 1]  # Pacman starts at [1,1]

    # We will first move right (eat pellet), then move right again (hit ghost)
    p = Pacman(game_map, output_map, pacman_pos, move="right", block=0)
    new_game_map, new_output_map, new_pos, block, lose = p.move_pacman()

    # Now, move 'right' from [1, 2] into the Ghost at [1, 3]
    p_next = Pacman(new_game_map, new_output_map, new_pos, move="right", block=0)
    _, _, _, _, lose_next = p_next.move_pacman()

    assert lose_next is True


# --- Ghost Tests ---

def test_ghost_hits_pacman():
    """Tests if the 'lose' flag is set when a Ghost moves onto Pacman."""
    game_map = create_test_map()
    output_map = create_test_map()
    ghost_pos = [1, 3]

    # The Ghost at [1, 3] has two valid moves: 'left' or 'down'.
    # We can't guarantee it moves left, so we'll mock the 'choice' function
    # to force it.

    # A simple way to test is to create a map where the ONLY valid move
    # is onto Pacman.

    test_map = [
        ['=', '=', '='],
        ['=', 'P', '='],
        ['=', 'F', '='],  # Ghost at [2, 1]
        ['=', '=', '=']
    ]
    ghost_pos = [2, 1]

    # The only valid move for the Ghost is 'up'
    g = Ghost(test_map, test_map, ghost_pos)
    new_output_map, new_ghost_pos, lose = g.move_ghost()

    assert lose is True
    assert new_ghost_pos == [1, 1]
    assert new_output_map[2][1] == " "  # Ghost's old spot is now empty
    assert new_output_map[1][1] == "F"  # Ghost is on Pacman's old spot


# --- Game Logic Tests ---

def test_victory_condition():
    """Tests the __check_victory method."""
    # 1. Test a map that is NOT won (has pellets)
    game_map = create_test_map()
    game = PacmanGame(game_map, [1, 1], [1, 3])

    assert game._PacmanGame__check_victory() is False

    # 2. Test a map that IS won (no pellets)
    won_map = [
        ['=', '=', '='],
        ['=', ' ', '='],
        ['=', ' ', '='],
        ['=', '=', '=']
    ]
    game = PacmanGame(won_map, [1, 1], [2, 1])

    assert game._PacmanGame__check_victory() is True