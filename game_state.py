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

ALL_WALL_ANCHORS = {
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
    (3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
    (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7),
    (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
    (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
    (7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7),
}

white_position = (4, 0)
black_position = (4, 8)

white_walls = STARTING_WALLS
black_walls = STARTING_WALLS

horizontal_walls = set()
vertical_walls = set()

current_player = "white"


# -------------------------
# Player helpers
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

def switch_player():
    global current_player
    if current_player == "white":
        current_player = "black"
    else:
        current_player = "white"
    
def get_winner():
    # returns white, black or None
    if white_position[1] == BOARD_SIZE - 1:
        return "white"
    elif black_position[1] == 0:
        return "black"
    else:
        return None

# -------------------------
# Board helpers
# -------------------------

def is_position_on_board(position):
    x, y = position
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


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


def get_unblocked_adjacent_positions(position):
    x, y = position

    possible_positions = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    accessible_positions = []

    for end_position in possible_positions:
        if not is_position_on_board(end_position):
            continue

        if is_blocked_by_wall(position, end_position):
            continue

        accessible_positions.append(end_position)

    return accessible_positions


def has_path_to_goal(player):
    start = get_player_position(player)

    if start is None:
        return False

    if player == "white":
        goal_y = BOARD_SIZE - 1
    elif player == "black":
        goal_y = 0
    else:
        return False

    visited = set()
    stack = [start]

    while stack:
        current_position = stack.pop()

        if current_position in visited:
            continue

        visited.add(current_position)

        current_x, current_y = current_position

        if current_y == goal_y:
            return True

        for neighbour in get_unblocked_adjacent_positions(current_position):
            if neighbour not in visited:
                stack.append(neighbour)

    return False


def is_legal_horizontal_wall(player, x, y):
    if player != "white" and player != "black":
        return False

    if player == "white" and white_walls <= 0:
        return False

    if player == "black" and black_walls <= 0:
        return False

    if not is_valid_wall_position(x, y):
        return False

    # Cannot overlap another horizontal wall.
    if (x, y) in horizontal_walls:
        return False

    # Cannot directly continue another horizontal wall.
    if (x - 1, y) in horizontal_walls:
        return False

    if (x + 1, y) in horizontal_walls:
        return False

    # Cannot cross a vertical wall at the same anchor.
    if (x, y) in vertical_walls:
        return False

    # Temporarily place the wall.
    horizontal_walls.add((x, y))

    white_has_path = has_path_to_goal("white")
    black_has_path = has_path_to_goal("black")

    # Remove the temporary wall.
    horizontal_walls.remove((x, y))

    if not white_has_path:
        return False

    if not black_has_path:
        return False

    return True


def place_horizontal_wall(player, x, y):
    global white_walls, black_walls

    if not is_legal_horizontal_wall(player, x, y):
        return False

    horizontal_walls.add((x, y))

    if player == "white":
        white_walls -= 1
    elif player == "black":
        black_walls -= 1

    return True


def is_legal_vertical_wall(player, x, y):
    if player != "white" and player != "black":
        return False

    if player == "white" and white_walls <= 0:
        return False

    if player == "black" and black_walls <= 0:
        return False

    if not is_valid_wall_position(x, y):
        return False

    # Cannot overlap another vertical wall.
    if (x, y) in vertical_walls:
        return False

    # Cannot directly continue another vertical wall.
    if (x, y + 1) in vertical_walls:
        return False

    if (x, y - 1) in vertical_walls:
        return False

    # Cannot cross a horizontal wall at the same anchor.
    if (x, y) in horizontal_walls:
        return False

    # Temporarily place the wall.
    vertical_walls.add((x, y))

    white_has_path = has_path_to_goal("white")
    black_has_path = has_path_to_goal("black")

    # Remove the temporary wall.
    vertical_walls.remove((x, y))

    if not white_has_path:
        return False

    if not black_has_path:
        return False

    return True


def generate_legal_wall_moves(player):
    legal_wall_moves = []

    horizontal_candidates = ALL_WALL_ANCHORS.copy()
    horizontal_candidates = horizontal_candidates - horizontal_walls
    horizontal_candidates = horizontal_candidates - vertical_walls

    for x, y in horizontal_walls:
        horizontal_candidates.discard((x - 1, y))
        horizontal_candidates.discard((x + 1, y))

    for x, y in horizontal_candidates:
        if is_legal_horizontal_wall(player, x, y):
            legal_wall_moves.append(("horizontal_wall", x, y))

    vertical_candidates = ALL_WALL_ANCHORS.copy()
    vertical_candidates = vertical_candidates - vertical_walls
    vertical_candidates = vertical_candidates - horizontal_walls

    for x, y in vertical_walls:
        vertical_candidates.discard((x, y - 1))
        vertical_candidates.discard((x, y + 1))

    for x, y in vertical_candidates:
        if is_legal_vertical_wall(player, x, y):
            legal_wall_moves.append(("vertical_wall", x, y))

    return legal_wall_moves


def place_vertical_wall(player, x, y):
    global white_walls, black_walls

    if not is_legal_vertical_wall(player, x, y):
        return False

    vertical_walls.add((x, y))

    if player == "white":
        white_walls -= 1
    elif player == "black":
        black_walls -= 1

    switch_player()
    
    return True


# -------------------------
# Pawn movement helpers
# -------------------------

def is_legal_adjacent_move(start, end):
    if not is_position_on_board(start):
        return False

    if not is_position_on_board(end):
        return False

    if not are_adjacent(start, end):
        return False

    if is_blocked_by_wall(start, end):
        return False

    if is_square_occupied(end):
        return False

    return True


def is_valid_straight_jump(player, start, end):
    if not is_position_on_board(start):
        return False

    if not is_position_on_board(end):
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
    if not is_position_on_board(start):
        return False

    if not is_position_on_board(end):
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
    straight_jump_end_position = (
        opponent_x + opponent_dx,
        opponent_y + opponent_dy
    )

    straight_jump_is_possible = (
        is_position_on_board(straight_jump_end_position)
        and not is_blocked_by_wall(opponent_position, straight_jump_end_position)
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


def generate_legal_pawn_moves(player):
    player_position = get_player_position(player)

    if player_position is None:
        return []

    x, y = player_position

    candidate_moves = [
        # Adjacent moves
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),

        # Straight jumps
        (x + 2, y),
        (x - 2, y),
        (x, y + 2),
        (x, y - 2),

        # Diagonal jumps
        (x + 1, y + 1),
        (x + 1, y - 1),
        (x - 1, y + 1),
        (x - 1, y - 1),
    ]

    legal_moves = []

    for end_position in candidate_moves:
        if is_legal_pawn_move(player, end_position):
            legal_moves.append(end_position)

    return legal_moves


def move_pawn(player, end):
    global white_position, black_position
    if not is_legal_pawn_move(player, end):
        return False
    
    if player == "white":
        white_position = end
    elif player == "black":
        black_position = end

    winner = get_winner()

    if winner == "white":
        print("white wins")
        return True
    elif winner == "black":
        print("black wins")
        return True

    switch_player()


    return True


def generate_legal_actions(player):

    generate_legal_pawn_moves()
    generate_legal_wall_moves()




# -------------------------
# Test code
# -------------------------

print("White walls before:", white_walls)
print("Place vertical wall:", place_vertical_wall("white", 4, 4))
print("White walls after:", white_walls)

print("White has path:", has_path_to_goal("white"))
print("Black has path:", has_path_to_goal("black"))

