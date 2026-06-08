"""
Quoridor game state representation.

Coordinate system:
- (0,0) is the bottom-left square.
- White starts at (4,0).
- Black starts at (4,8).

Wall representation:
- Wall anchors use an 8x8 wall grid.
- Horizontal walls are stored as anchor coordinates.
- Vertical walls are stored as anchor coordinates.
- A wall extends in the positive direction from its anchor.
"""

BOARD_SIZE = 9
STARTING_WALLS = 10

white_position = (4, 0)
black_position = (4, 8)

white_walls = STARTING_WALLS
black_walls = STARTING_WALLS

horizontal_walls = set()
vertical_walls = set()

current_player = "white"


def is_position_on_board(position):
    x, y = position
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def is_valid_wall_position(x, y):
    return 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1

def is_adjacent_move(start, end):
    start_x, start_y = start
    end_x, end_y = end

    dx = end_x - start_x
    dy = end_y - start_y

    return abs(dx) + abs(dy) == 1


def place_horizontal_wall(x, y):
    if not is_valid_wall_position(x, y):
        print("Invalid horizontal wall position")
        return False

    horizontal_walls.add((x, y))
    return True


def place_vertical_wall(x, y):
    if not is_valid_wall_position(x, y):
        print("Invalid vertical wall position")
        return False

    vertical_walls.add((x, y))
    return True


def is_move_on_board(start, end):
    return is_position_on_board(start) and is_position_on_board(end)


print(is_position_on_board((4, 0)))
print(is_position_on_board((9, 0)))

print(place_horizontal_wall(3, 2))
print(place_horizontal_wall(8, 2))

print(horizontal_walls)






