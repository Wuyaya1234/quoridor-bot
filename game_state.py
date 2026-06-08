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


# -------------------------
# Player position helpers
# -------------------------

def get_player_position(player):
    if player == "white":
        return white_position

    if player == "black":
        return black_position

    return None


def get_opponent_position(player):
    if player == "white":
        return black_position

    if player == "black":
        return white_position

    return None


def is_square_occupied(position):
    return position == white_position or position == black_position


# -------------------------
# Board helpers
# -------------------------

def is_position_on_board(position):
    x, y = position
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def is_move_on_board(start, end):
    return is_position_on_board(start) and is_position_on_board(end)


def are_adjacent(start, end):
    start_x, start_y = start
    end_x, end_y = end

    dx = end_x - start_x
    dy = end_y - start_y

    return abs(dx) + abs(dy) == 1


# -------------------------
# Wall helpers
# -------------------------

def is_valid_wall_position(x, y):
    return 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1


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


def is_blocked_by_wall(start, end):
    start_x, start_y = start
    end_x, end_y = end

    dx = end_x - start_x
    dy = end_y - start_y

    # Moving right: vertical wall may block between start and end.
    if dx == 1:
        return (
            (start_x, start_y) in vertical_walls
            or (start_x, start_y - 1) in vertical_walls
        )

    # Moving left.
    if dx == -1:
        return (
            (start_x - 1, start_y) in vertical_walls
            or (start_x - 1, start_y - 1) in vertical_walls
        )

    # Moving up: horizontal wall may block between start and end.
    if dy == 1:
        return (
            (start_x, start_y) in horizontal_walls
            or (start_x - 1, start_y) in horizontal_walls
        )

    # Moving down.
    if dy == -1:
        return (
            (start_x, start_y - 1) in horizontal_walls
            or (start_x - 1, start_y - 1) in horizontal_walls
        )

    return False


# -------------------------
# Pawn movement helpers
# -------------------------

def is_legal_adjacent_move(start, end):
    if not is_move_on_board(start, end):
        return False

    if not are_adjacent(start, end):
        return False

    if is_blocked_by_wall(start, end):
        return False

    if is_square_occupied(end):
        return False

    return True


def is_valid_straight_jump(player, start, end):
    if not is_move_on_board(start, end):
        return False

    opponent_position = get_opponent_position(player)

    if opponent_position is None:
        return False
    
    if is_blocked_by_wall(start, opponent_position):
        return False

    start_x, start_y = start
    end_x, end_y = end

    dx = end_x - start_x
    dy = end_y - start_y

    # Must move exactly 2 squares horizontally or vertically.
    if not ((abs(dx) == 2 and dy == 0) or (abs(dy) == 2 and dx == 0)):
        return False

    middle = (start_x + dx // 2, start_y + dy // 2)

    # Must be jumping over the opponent.
    if middle != opponent_position:
        return False

    # Wall between opponent and landing square blocks jump.
    if is_blocked_by_wall(middle, end):
        return False

    if is_square_occupied(end):
        return False

    return True


def is_valid_diagonal_jump(player, start, end):
    if not is_move_on_board(start, end):
        return False

    opponent_position = get_opponent_position(player)

    if opponent_position is None:
        return False

    # Diagonal jump only happens if opponent is next to you.
    if not are_adjacent(start, opponent_position):
        return False

    if is_blocked_by_wall(start, opponent_position):
        return False

    start_x, start_y = start
    opponent_x, opponent_y = opponent_position

    # Direction from you to opponent.
    opponent_dx = opponent_x - start_x
    opponent_dy = opponent_y - start_y

    # The square behind the opponent, where a normal jump would land.
    straight_jump_end_pos = (
        opponent_x + opponent_dx,
        opponent_y + opponent_dy
    )

    straight_jump_is_possible = (
        is_position_on_board(straight_jump_end_pos)
        and not is_blocked_by_wall(opponent_position, straight_jump_end_pos)
    )

    # If you can jump straight, diagonal jump is not allowed.
    if straight_jump_is_possible:
        return False

    # Diagonal landing square must be beside the opponent.
    if not are_adjacent(opponent_position, end):
        return False

    # But it must also be diagonal from the original start square.
    end_x, end_y = end
    dx = end_x - start_x
    dy = end_y - start_y

    if not (abs(dx) == 1 and abs(dy) == 1):
        return False

    # Wall between opponent and diagonal landing square blocks this move.
    if is_blocked_by_wall(opponent_position, end):
        return False

    if is_square_occupied(end):
        return False

    return True


def is_legal_pawn_move(player, end):
    start = get_player_position(player)

    if start is None:
        return False

    if is_legal_adjacent_move(start, end):
        return True

    if is_valid_straight_jump(player, start, end):
        return True

    if is_valid_diagonal_jump(player, start, end):
        return True

    return False


# -------------------------
# Test code

# Basic move
print(is_legal_pawn_move("white", (4, 1)))  # True

# Blocked by wall
horizontal_walls.add((4, 0))
print(is_legal_pawn_move("white", (4, 1)))  # False

# Reset wall
horizontal_walls.clear()

# Straight jump test
white_position = (4, 4)
black_position = (4, 5)
print(is_legal_pawn_move("white", (4, 6)))  # True

# Diagonal jump test
horizontal_walls.add((4, 5))
print(is_legal_pawn_move("white", (3, 5)))  # True
print(is_legal_pawn_move("white", (5, 5)))  # True
# -------------------------

print(is_legal_pawn_move("white", (4, 1)))  # True at starting position
print(is_legal_pawn_move("white", (4, 2)))  # False, too far



