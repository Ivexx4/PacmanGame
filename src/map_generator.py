import random


class MapGenerator:
    """
    Generates a random map for the Pacman game.
    """

    def __init__(self, width: int, height: int):
        if width < 7 or height < 7:
            raise ValueError("Map dimensions must be at least 7x7.")
        self.width = width if width % 2 != 0 else width + 1
        self.height = height if height % 2 != 0 else height + 1
        self.map = [['=' for _ in range(self.width)] for _ in range(self.height)]

    def generate(self) -> list[list[str]]:
        """Generates a random map layout."""


        # Start with a grid of walls
        self.map = [['=' for _ in range(self.width)] for _ in range(self.height)]

        # Carve out paths using a randomized Prim's algorithm
        # Ensure the starting point has odd coordinates for the algorithm to work correctly
        start_x = random.choice(range(1, self.width - 1, 2))
        start_y = random.choice(range(1, self.height - 1, 2))
        self.map[start_y][start_x] = ' '

        frontiers = []
        for x, y in [(start_x, start_y)]:
            for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1:
                    frontiers.append((x + dx, y + dy))

        while frontiers:
            x, y = random.choice(frontiers)
            frontiers.remove((x, y))
            self.map[y][x] = ' '

            neighbors = []
            for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                if 0 < x - dx < self.width - 1 and 0 < y - dy < self.height - 1 and self.map[y - dy][x - dx] == ' ':
                    neighbors.append((x - dx, y - dy))
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                self.map[(y + ny) // 2][(x + nx) // 2] = ' '

            for dx, dy in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1 and self.map[y + dy][x + dx] == '=':
                    if (x + dx, y + dy) not in frontiers:
                        frontiers.append((x + dx, y + dy))

        # Convert empty spaces to pellets
        for r in range(self.height):
            for c in range(self.width):
                if self.map[r][c] == ' ':
                    self.map[r][c] = '.'

        return self.map

    def get_start_positions(self) -> tuple[list[int], list[list[int]]]:
        """Returns valid starting positions for Pac-Man and ghosts, ensuring a safe distance."""
        empty_cells = []
        for r in range(self.height):
            for c in range(self.width):
                if self.map[r][c] == '.':
                    empty_cells.append([r, c])
        
        if not empty_cells:
            return [self.height // 2, self.width // 2], [[1, 1]]

        pacman_start = random.choice(empty_cells)
        empty_cells.remove(pacman_start)
        
        # Ensure ghosts start at a safe distance from Pac-Man
        min_distance = (self.width + self.height) // 4  # Heuristic for safe distance
        safe_cells = []
        for cell in empty_cells:
            distance = abs(cell[0] - pacman_start[0]) + abs(cell[1] - pacman_start[1])
            if distance > min_distance:
                safe_cells.append(cell)

        # If not enough safe cells are found, take the farthest ones
        if len(safe_cells) < 3:
            empty_cells.sort(key=lambda cell: abs(cell[0] - pacman_start[0]) + abs(cell[1] - pacman_start[1]), reverse=True)
            safe_cells = empty_cells

        num_ghosts = min(3, len(safe_cells))
        ghost_starts = random.sample(safe_cells, num_ghosts)
            
        return pacman_start, ghost_starts
