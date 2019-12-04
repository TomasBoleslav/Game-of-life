
from typing import Tuple
import time
import math
from tkinter import *
import sys
try:
    from PIL import Image as Img
    from PIL import ImageTk, ImageDraw
except ImportError:
    messagebox.showinfo(message = 'Pillow library is missing.')
    sys.exit()


def max(x: int, y: int):
    """Return the maximum of two integers."""
    if x > y:
        return x
    else:
        return y

def min(x: int, y: int):
    """Return the minimum of two integers."""
    if x < y:
        return x
    else:
        return y


class Board:
    """Represents a game board."""

    def __init__(self) -> None:
        """Initialize instance variables."""

        self.__current = []
        self.__next = []

        self.__height = 0
        self.__width = 0

        self.__birth_rule = set()
        self.__remain_rule = set()

        self.__living = []
        self.__generation = 0

    # PROPERTIES
    # region
    @property
    def height(self) -> int:
        return self.__height

    @property
    def width(self) -> int:
        return self.__width

    @property
    def birth_rule(self) -> set:
        return self.__birth_rule.copy()

    @birth_rule.setter
    def birth_rule(self, value: set) -> None:
        self.__birth_rule = value

    @property
    def remain_rule(self) -> set:
        return self.__remain_rule.copy()

    @remain_rule.setter
    def remain_rule(self, value: set) -> None:
        self.__remain_rule = value

    @property
    def living(self) -> list:
        return self.__living

    @property
    def generation(self) -> int:
        return self.__generation
    #endregion

    def __create_empty(self, height: int, width: int) -> list:
        """Create an empty grid with given dimensions."""

        return [[False] * width for x in range(height)]

    def __remove_living(self) -> None:
        """Remove all living cells from the board."""

        for cell in self.__living:
            i, j = cell
            self.__current[i][j] = False
        self.__living = []

    def empty_board(self, height: int, width: int) -> None:
        """Create a new empty grid with given dimensions."""

        self.__height = height
        self.__width = width

        self.__current = self.__create_empty(height, width)
        self.__next = self.__create_empty(height, width)

        self.__living = []
        self.__generation = 0
    
    def copy(self, board: 'Board') -> None:
        """Copy values from the given board to this board."""

        self.__height = board.height
        self.__width = board.width

        self.__current = board.grid_copy()
        self.__next = self.__create_empty(board.height, board.width)

        self.__birth_rule = board.birth_rule
        self.__remain_rule = board.remain_rule

        self.__living = board.living.copy()
        self.__generation = board.generation

    def grid_copy(self) -> list:
        """Return a copy of the current grid."""

        return [row.copy() for row in self.__current]

    def add(self, i: int, j: int) -> None:
        """Add a new cell at the position (i, j)."""

        if (i < 0 or self.__height <= i or
            j < 0 or self.__width <= j):
            return

        if not self.__current[i][j]:
            self.__living.append((i, j))
            self.__current[i][j] = True

    def remove(self, i: int, j: int) -> None:
        '''Remove a living cell at the position (i, j).'''

        if (i < 0 or self.__height <= i or
            j < 0 or self.__width <= j):
            return

        if self.__current[i][j]:
            self.__living.remove((i, j))
            self.__current[i][j] = False

    def is_alive(self, i: int, j: int) -> bool:
        """Check if a cell at the position (i, j) is alive."""

        if (i < 0 or self.__height <= i or
            j < 0 or self.__width <= j):
            return False

        return self.__current[i][j]

    def next_gen(self) -> None:
        """Compute the next generation and set it as current."""

        def solve_living_and_find_neighbors(living: list, survivors: list, neighbors: set) -> None:
            """Decide the next state of living cells and find their neighbors."""

            def count_neighbors_and_find_empty(x: int, y: int) -> int:
                """Count neighbors of a cell (x, y) and add empty neighbors to the set."""
                
                def add_if_empty(i: int, j: int) -> None:
                    """Increments the counter or adds an empty cell to neighbors."""

                    nonlocal counter
                    if self.__current[i][j]:
                        counter += 1
                    else:
                        neighbors.add((i, j))

                counter = 0
                if x > 0:
                    add_if_empty(x-1, y)
                    if y > 0:
                        add_if_empty(x-1, y-1)
                    if y < self.__width - 1:
                        add_if_empty(x-1, y+1)

                if x < self.__height - 1:
                    add_if_empty(x+1, y)
                    if y > 0:
                        add_if_empty(x+1, y-1)
                    if y < self.__width - 1:
                        add_if_empty(x+1, y+1)
    
                if y > 0:
                    add_if_empty(x, y-1)
                if y < self.__width - 1:
                    add_if_empty(x, y+1)

                return counter

            nonlocal next
            current = self.__current

            for i, j in living:
                neighbor_count = count_neighbors_and_find_empty(i, j)
                if neighbor_count in self.__remain_rule:
                    next[i][j] = True
                    survivors.append((i, j))

        def solve_neighbors(neighbors: set, survivors: list) -> None:
            """Decide the next state of neighbors of living cells."""
            
            def count_neighbors(x: int, y: int) -> int:
                """Count neighbors of a cell (x, y)."""

                grid = self.__current

                counter = 0   
                if x > 0:
                    if grid[x-1][y]: counter += 1
                    if y > 0:
                        if grid[x-1][y-1]: counter += 1
                    if y < self.__width - 1:
                        if grid[x-1][y+1]: counter += 1

                if x < self.__height - 1:
                    if grid[x+1][y]: counter += 1
                    if y > 0:
                        if grid[x+1][y-1]: counter += 1
                    if y < self.__width - 1:
                        if grid[x+1][y+1]: counter += 1
    
                if y > 0:
                    if grid[x][y-1]: counter += 1
                if y < self.__width - 1:
                    if grid[x][y+1]: counter += 1

                return counter

            nonlocal next
            current = self.__current

            for i, j in neighbors:
                neighbor_count = count_neighbors(i, j)
                if neighbor_count in self.__birth_rule:
                    next[i][j] = True
                    survivors.append((i, j))

        if self.__height <= 0 or self.__width <= 0:
            return

        survivors = []          # Cells that will survive to the next generation
        neighbors = set()       # Neighbors of living cells
        next = self.__next

        solve_living_and_find_neighbors(self.__living, survivors, neighbors)
        solve_neighbors(neighbors, survivors)
        self.__remove_living()

        self.__living = survivors
        self.__next = self.__current
        self.__current = next
        self.__generation += 1

    def save_to_string(self) -> str:
        """Save the board to a string."""

        grid_string = ""
        for cell in self.__living:
            i, j = cell
            grid_string += str(i) + " " + str(j) + " "

        return grid_string

    def read_from_string(self, grid_string: str) -> bool:
        """Read the board from a string.
        Assumes an empty board has been created before."""

        self.__remove_living()
        self.__generation = 0

        cells = grid_string.split()     # Coordinates of living cells

        # Divide the coordinates into pairs
        for i in range(0, len(cells) - 1, 2):
            x, y = cells[i], cells[i + 1]

            if x.isdigit() and y.isdigit():
                i, j = int(x), int(y)
                if (0 <= i and i < self.__height and 
                    0 <= j and j < self.__width):
                    self.__living.append((i, j))
                    self.__current[i][j] = True
                else:
                    self.__remove_living()
                    return False
            else:
                self.__remove_living()
                return False

        return True


class Rule:
    """Validates and stores a game rule."""

    def __init__(self, birth_name: str, remain_name: str, sep: str) -> None:
        """Initialize instance variables."""

        self.__birth_name = birth_name
        self.__remain_name = remain_name
        self.__sep = sep

        self.__birth_rule = set()
        self.__remain_rule = set()

    @property
    def birth_rule(self) -> set:
        return self.__birth_rule.copy()

    @property
    def remain_rule(self) -> set:
        return self.__remain_rule.copy()

    def try_set_rule(self, value: str) -> bool:
        """Try to set the value as a new rule.
        Return True if successful, False otherwise."""

        def try_add_numbers(rule_string: str, rule_name: str, rule_numbers: set) -> bool:
            """Try to add rule numbers to a set.
            Return True if successful, False otherwise."""

            if not rule_string.find(rule_name) == 0:
                return False

            numbers = list(rule_string)[len(rule_name):]   
            for num in numbers:
                if not num.isdigit():
                    return False
                x = int(num)
                if (x == 0) or (x == 9) or (x in rule_numbers):
                    return False
                rule_numbers.add(x)
            return True

        birth_rule = set()
        remain_rule = set()

        split_rules = value.split(sep = self.__sep)
        if len(split_rules) != 2:
            return False
        birth_string, remain_string = split_rules

        if (not try_add_numbers(birth_string, self.__birth_name, birth_rule) or
            not try_add_numbers(remain_string, self.__remain_name, remain_rule)):
            return False

        self.__birth_rule = birth_rule
        self.__remain_rule = remain_rule
        return True


class Painter:
    """Paints a board on a canvas."""

    def __init__(self) -> None:
        """Initialize instance variables"""

        self.__max_width = 0        # Maximum size of the canvas image, actual size of grids
        self.__max_height = 0
        self.__width = 0            # Actual size of the canvas image and cropped grids
        self.__height = 0

        self.__m_cell = (0,0)       # Index of a cell displayed in the middle of the 
                                    # canvas image = position of the view
        self.__board = None
        self.__canvas = None
        self.__canvas_image = None
        self.__board_image = None       # Result image drawn on the canvas_image
        self.__stroke = (50,50,50)      # Stroke color of the cells
        self.__fill = (255,255,255)     # Fill color of the cells

        self.__cell_sizes = []
        self.__grids = []           # Images of grids for different cell sizes
        self.__current = 0          # Index of currently used cell size and grid

        self.__is_drawing = False
        self.__is_adjusting = False

    # PROPERTIES
    # region
    @property
    def canvas(self) -> Canvas:
        return self.__canvas

    @canvas.setter
    def canvas(self, value: Canvas) -> None:
        self.__canvas = value
        self.__canvas_image = self.__canvas.create_image(0, 0, anchor='nw')

    @property
    def board(self) -> Board:
        return self.__board

    @board.setter
    def board(self, value: Board) -> None:
        self.__board = value
        self.__m_cell = (value.height // 2, value.width // 2)

    @property
    def fill(self) -> Tuple[int,int,int]:
        return self.__fill

    @fill.setter
    def fill(self, value: Tuple[int,int,int]) -> None:
        self.__fill = value

    @property
    def zoom(self) -> int:
        return self.__current

    @zoom.setter
    def zoom(self, value: int) -> None:
        if 0 <= value and value < len(self.__cell_sizes):
            self.__current = value
    # endregion

    def reset(self, max_width: int, max_height: int, cell_sizes: list,
              bg: Tuple[int,int,int], stroke: Tuple[int,int,int]) -> None:
        """Initialize the painter, create a background image (grid) for each cell size."""

        def append_grid(w: int, h: int, cell_size: int):
            """Append a new grid image for the cell size."""

            # Do not draw grid lines for cell_size < 5
            if cell_size < 5:
                if len(self.__grids) == 0:
                    self.__grids.append(Img.new('RGB', (w,h), color = bg)) 
                else:                                       
                    self.__grids.append(self.__grids[0])    # Do not create more empty images
                return

            self.__grids.append(Img.new('RGB', (w,h), color = bg))
            draw = ImageDraw.Draw(self.__grids[-1])
            for i in range(w // cell_size):
                draw.line((0, i*cell_size, h, i*cell_size), fill=stroke, width=1)
            for i in range(h // cell_size):
                draw.line((i*cell_size, 0, i*cell_size, w), fill=stroke, width=1)

        cell_sizes.sort()
        self.__grids = []
        for cell_size in cell_sizes:
            append_grid(max_width, max_height, cell_size)

        self.__max_width = max_width
        self.__max_height = max_height
        self.__cell_sizes = cell_sizes
        self.__current = 0
        self.__stroke = stroke

    def adjust_to_canvas(self) -> None:
        """Adjust drawing to the canvas size.
        Call this when the canvas is resized."""

        if self.__is_adjusting:
            return
        self.__is_adjusting = True

        canvas_width = self.__canvas.winfo_width()
        canvas_height = self.__canvas.winfo_height()
        self.__width = min(self.__max_width, canvas_width)
        self.__height = min(self.__max_height, canvas_height)

        self.__is_adjusting = False

    def draw_board(self) -> None:
        """Draw the board on the canvas."""

        def find_cells_in_view(m_position) -> Tuple:
            """Find indices of cells in the top left corner and the bottom right corner
            of the cropped image."""

            w = self.__width
            h = self.__height
            m_cell = self.__m_cell
            size = self.__cell_sizes[self.__current]

            # Number of cells relatively to the middle cell
            cells_left = int(math.ceil(m_position[0] / size))
            cells_above = int(math.ceil(m_position[1] / size))
            cells_right = int(math.ceil((w - m_position[0]) / size)) - 1
            cells_below = int(math.ceil((h - m_position[1]) / size)) - 1

            top_left = (m_cell[0] - cells_above,
                        m_cell[1] - cells_left)
            bottom_right = (m_cell[0] + cells_below,
                            m_cell[1] + cells_right)

            return top_left, bottom_right

        def crop_grid(grid: Img.Image) -> Img.Image:
            """Crop the grid to fit the canvas image."""

            max_w = self.__max_width
            max_h = self.__max_height
            w = self.__width
            h = self.__height

            crop_from = (max_w // 2 - w // 2, max_h // 2 - h // 2)
            crop_to = (crop_from[0] + w - 1, crop_from[1] + h - 1)

            return grid.crop(crop_from + crop_to)

        def draw_cells(image: Img.Image, m_position: Tuple[int,int],
                       top_left: Tuple[int,int], bottom_right: Tuple[int,int]):
            """Draw all living cells."""

            draw = ImageDraw.Draw(image)
            m_cell = self.__m_cell
            size = self.__cell_sizes[self.__current]

            for i, j in self.__board.living:
                if (i < top_left[0] or bottom_right[0] < i or
                    j < top_left[1] or bottom_right[1] < j):
                    continue
                left = m_position[0] + (j - m_cell[1]) * size      # Left position of the cell
                top = m_position[1] + (i - m_cell[0]) * size       # Top position of the cell
                rect = (left, top, left + size, top + size)
                draw.rectangle(rect, fill=self.__fill, outline=self.__stroke, width=1)

        if (self.__canvas == None or self.__board == None or 
            self.__is_drawing or self.__is_adjusting):
            return
        self.__is_drawing = True

        m_position = self.__m_cell_position_in_image()
        top_left, bottom_right = find_cells_in_view(m_position)

        cropped = crop_grid(self.__grids[self.__current])
        draw_cells(cropped, m_position, top_left, bottom_right)
        self.__board_image = ImageTk.PhotoImage(cropped)    # Convert image to be used by tkinter
        self.__canvas.itemconfig(self.__canvas_image, image=self.__board_image)

        self.__is_drawing = False

    def __m_cell_position_in_image(self) -> Tuple[int, int]:
        """Find the position of the middle cell in the cropped image."""

        max_w = self.__max_width
        max_h = self.__max_height
        w = self.__width
        h = self.__height
        size = self.__cell_sizes[self.__current]

        middle = (max_w // 2, max_h // 2)
        m_position = (w // 2 - middle[0] % size,
                      h // 2 - middle[1] % size)

        return m_position

    def cell_index_from_coord(self, x: int, y: int) -> Tuple[int,int]:
        """Return the index of a cell (row, column) at the coordinates (x, y) on the canvas."""

        if x >= self.__width or y >= self.__height:
            return -1, -1

        size = self.__cell_sizes[self.__current]
        m_position = self.__m_cell_position_in_image()
        m_middle = (m_position[0] + size / 2,
                    m_position[1] + size / 2)
        i = self.__m_cell[0] + round( (y - m_middle[1]) / size ) 
        j = self.__m_cell[1] + round( (x - m_middle[0]) / size )

        return i, j

    def move_view(self, right: int, bottom: int) -> None:
        """Move the view of the board.
        Use negative numbers for the opposite direction."""

        if self.board == None:
            return
        
        size = self.__cell_sizes[self.__current]
        displayed_cells = min(self.__width // size,
                              self.__height // size)
        move_length = max(1, displayed_cells // 5)

        new_i = self.__m_cell[0] + bottom * move_length
        new_j = self.__m_cell[1] + right * move_length
        self.__m_cell = (new_i, new_j)


class Animator:
    """Animates board generations using a painter."""

    def __init__(self, master) -> None:
        """Initialize instance variables."""

        self.__master = master
        self.__board = None
        self.__painter = None

        self.__is_running = False
        self.__time_per_gen = 1

        self.__on_new_gen = None

    # PROPERTIES
    # region
    @property
    def board(self) -> Board:
        return self.__board

    @board.setter
    def board(self, value: Board) -> None:
        self.__board = value

    @property
    def painter(self) -> Painter:
        return self.__painter

    @painter.setter
    def painter(self, value: Painter) -> None:
        self.__painter = value
        
    @property
    def is_running(self) -> bool:
        return self.__is_running

    @property
    def time_per_gen(self) -> int:
        return self.__time_per_gen

    @time_per_gen.setter
    def time_per_gen(self, value: int) -> None:
        self.__time_per_gen = value

    @property
    def on_new_gen(self) -> 'function':
        return self.__on_new_gen
    
    @on_new_gen.setter
    def on_new_gen(self, value: 'function') -> None:    
        self.__on_new_gen = value
    # endregion

    def play(self) -> None:
        """Start the animation."""

        def next_frame() -> None:
            """Draw the next frame of the animation."""

            if not self.__is_running:
                return

            start = time.time()

            self.__board.next_gen()
            self.__painter.draw_board()
            if self.__on_new_gen != None:
                self.__on_new_gen()

            end = time.time()

            elapsed = int((end - start) * 1000)
            time_to_wait = self.__time_per_gen - elapsed

            if time_to_wait <= 50:   # Make enough time for events
                time_to_wait = 50
            self.__master.after(time_to_wait, next_frame)

        if (self.__board == None or
            self.__painter == None or
            self.__is_running):
            return

        self.__is_running = True
        self.__master.after(max(self.__time_per_gen, 50), next_frame)

    def stop(self) -> None:
        """Pause the animation."""

        self.__is_running = False


