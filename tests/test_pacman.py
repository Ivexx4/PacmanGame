"""
Pytest tests for the Pacman class.

This file specifically tests the player's movement logic, including:
- Moving into empty spaces
- Eating pellets
- Colliding with walls
- Colliding with ghosts
- Movement blocking (cooldown)
"""

# Import the class to be tested
from src.pacman import Pacman


def create_test_map():
    """Helper function to create a clean, reusable map for testing."""
    return [
        ['=', '=', '=', '=', '='],
        ['=', 'P', '.', 'F', '='],  # P at [1,1], Pellet at [1,2], F at [1,3]
        ['=', ' ', '=', ' ', '='],
        ['=', '.', ' ', '.', '='],
        ['=', '=', '=', '=', '=']
    ]


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


def test_pacman_block_cooldown():
    """Tests that the movement block timer counts down."""
    game_map = create_test_map()
    output_map = create_test_map()
    pacman_pos = [1, 1]

    # Simulate being on a 2-turn cooldown
    p = Pacman(game_map, output_map, pacman_pos, move="down", block=2)
    _, _, new_pos, block, _ = p.move_pacman()

    assert new_pos == [1, 1]  # Pacman did not move
    assert block == 1  # Timer counted down to 1

    # Test the next turn
    p_next = Pacman(game_map, output_map, new_pos, move="down", block=block)
    _, _, new_pos_next, block_next, _ = p_next.move_pacman()

    assert new_pos_next == [1, 1]  # Pacman did not move
    assert block_next == 0  # Timer counted down to 0

    # Test the turn after cooldown
    p_final = Pacman(game_map, output_map, new_pos_next, move="down", block=block_next)
    _, _, new_pos_final, block_final, _ = p_final.move_pacman()

    assert new_pos_final == [2, 1]  # Pacman finally moved
    assert block_final == 0  # Timer stays at 0


def test_pacman_hits_ghost():
    """Tests if the 'lose' flag is set when Pacman moves onto a Ghost."""
    game_map = create_test_map()
    output_map = create_test_map()
    # Pacman at [1, 2], Ghost at [1, 3]
    pacman_pos = [1, 2]
    output_map[1][1] = "."  # Move pacman to [1, 2] for the test
    output_map[1][2] = "P"

    # Intend to move 'right' from [1, 2] into the Ghost at [1, 3]
    p = Pacman(game_map, output_map, pacman_pos, move="right", block=0)
    _, _, new_pos, block, lose = p.move_pacman()

    assert lose is True
    assert new_pos == [1, 2]  # Pacman did not move
    assert block == 0  # No block for hitting a ghost