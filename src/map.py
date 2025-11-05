from typing import List

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

class Map:
    """
    Represents the game map using a grid of Tile objects with border walls.
    """

    def __init__(self, tiles_str: List[List[str]]) -> None:
        """
        Initializes the Map, setting up tiles and border walls from a character matrix.
        """
        self.tiles: List[List[Tile]] = [[Tile(char) for char in row] for row in tiles_str]
        self.rows = len(self.tiles)
        self.cols = len(self.tiles[0]) if self.rows > 0 else 0
        self._initialize_borders()
        self._set_display_chars()

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

    def remove_pellet(self, pos: List[int]) -> None:
        """Removes a pellet from the given position."""
        if self.in_bounds(pos):
            r, c = pos
            tile = self.tiles[r][c]
            if tile.has_pellet:
                tile.has_pellet = False
                if not tile.is_original_wall:
                    tile.display_char = ' '

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
