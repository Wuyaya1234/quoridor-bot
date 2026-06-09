"""
Quoridor game state representation.

Coordinate system:
- (0, 0) is the bottom-left square.
- White starts at (4, 0).
- Black starts at (4, 8).

Wall representation:
- Wall anchors use an 8x8 wall grid.
- Horizontal walls are stored as anchor coordinates.
- Vertical walls are stored as anchor coordinates.
- A wall extends in the positive direction from its anchor.

Action representation:
- ("pawn", (x, y))
- ("horizontal_wall", (x, y))
- ("vertical_wall", (x, y))
"""

BOARD_SIZE = 9
STARTING_WALLS = 10

ALL_WALL_ANCHORS = {
    (x, y)
    for x in range(BOARD_SIZE - 1)
    for y in range(BOARD_SIZE - 1)
}


class GameState:
    def __init__(
        self,
        white_position=(4, 0),
        black_position=(4, 8),
        white_walls=STARTING_WALLS,
        black_walls=STARTING_WALLS,
        horizontal_walls=None,
        vertical_walls=None,
        current_player="white",
    ):
        self.white_position = white_position
        self.black_position = black_position

        self.white_walls = white_walls
        self.black_walls = black_walls

        if horizontal_walls is None:
            self.horizontal_walls = set()
        else:
            self.horizontal_walls = set(horizontal_walls)

        if vertical_walls is None:
            self.vertical_walls = set()
        else:
            self.vertical_walls = set(vertical_walls)

        self.current_player = current_player

    # -------------------------
    # State copying
    # -------------------------

    def copy(self):
        return GameState(
            white_position=self.white_position,
            black_position=self.black_position,
            white_walls=self.white_walls,
            black_walls=self.black_walls,
            horizontal_walls=self.horizontal_walls.copy(),
            vertical_walls=self.vertical_walls.copy(),
            current_player=self.current_player,
        )

    # -------------------------
    # Player helpers
    # -------------------------

    def get_player_position(self, player):
        if player == "white":
            return self.white_position

        if player == "black":
            return self.black_position

        return None

    def get_opponent_position(self, player):
        if player == "white":
            return self.black_position

        if player == "black":
            return self.white_position

        return None

    def get_player_wall_count(self, player):
        if player == "white":
            return self.white_walls

        if player == "black":
            return self.black_walls

        return None

    def is_square_occupied(self, position):
        return position == self.white_position or position == self.black_position

    def switch_player(self):
        if self.current_player == "white":
            self.current_player = "black"
        else:
            self.current_player = "white"

    def get_winner(self):
        # Returns "white", "black", or None.
        if self.white_position[1] == BOARD_SIZE - 1:
            return "white"

        if self.black_position[1] == 0:
            return "black"

        return None

    def is_terminal(self):
        return self.get_winner() is not None

    # -------------------------
    # Board helpers
    # -------------------------

    def is_position_on_board(self, position):
        x, y = position
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE

    def are_adjacent(self, start, end):
        start_x, start_y = start
        end_x, end_y = end

        dx = end_x - start_x
        dy = end_y - start_y

        return abs(dx) + abs(dy) == 1

    # -------------------------
    # Wall helpers
    # -------------------------

    def is_valid_wall_position(self, x, y):
        return 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1

    def is_blocked_by_wall(self, start, end):
        start_x, start_y = start
        end_x, end_y = end

        dx = end_x - start_x
        dy = end_y - start_y

        # Moving right: vertical wall may block between start and end.
        if dx == 1:
            return (
                (start_x, start_y) in self.vertical_walls
                or (start_x, start_y - 1) in self.vertical_walls
            )

        # Moving left.
        if dx == -1:
            return (
                (start_x - 1, start_y) in self.vertical_walls
                or (start_x - 1, start_y - 1) in self.vertical_walls
            )

        # Moving up: horizontal wall may block between start and end.
        if dy == 1:
            return (
                (start_x, start_y) in self.horizontal_walls
                or (start_x - 1, start_y) in self.horizontal_walls
            )

        # Moving down.
        if dy == -1:
            return (
                (start_x, start_y - 1) in self.horizontal_walls
                or (start_x - 1, start_y - 1) in self.horizontal_walls
            )

        return False

    def get_unblocked_adjacent_positions(self, position):
        x, y = position

        possible_positions = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        accessible_positions = []

        for end_position in possible_positions:
            if not self.is_position_on_board(end_position):
                continue

            if self.is_blocked_by_wall(position, end_position):
                continue

            accessible_positions.append(end_position)

        return accessible_positions

    def has_path_to_goal(self, player):
        start = self.get_player_position(player)

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

            for neighbour in self.get_unblocked_adjacent_positions(current_position):
                if neighbour not in visited:
                    stack.append(neighbour)

        return False

    def is_legal_horizontal_wall(self, player, x, y):
        if player != "white" and player != "black":
            return False

        if player == "white" and self.white_walls <= 0:
            return False

        if player == "black" and self.black_walls <= 0:
            return False

        if not self.is_valid_wall_position(x, y):
            return False

        # Cannot overlap another horizontal wall.
        if (x, y) in self.horizontal_walls:
            return False

        # Cannot directly continue another horizontal wall.
        if (x - 1, y) in self.horizontal_walls:
            return False

        if (x + 1, y) in self.horizontal_walls:
            return False

        # Cannot cross a vertical wall at the same anchor.
        if (x, y) in self.vertical_walls:
            return False

        # Temporarily place the wall.
        self.horizontal_walls.add((x, y))

        white_has_path = self.has_path_to_goal("white")
        black_has_path = self.has_path_to_goal("black")

        # Remove the temporary wall.
        self.horizontal_walls.remove((x, y))

        if not white_has_path:
            return False

        if not black_has_path:
            return False

        return True

    def is_legal_vertical_wall(self, player, x, y):
        if player != "white" and player != "black":
            return False

        if player == "white" and self.white_walls <= 0:
            return False

        if player == "black" and self.black_walls <= 0:
            return False

        if not self.is_valid_wall_position(x, y):
            return False

        # Cannot overlap another vertical wall.
        if (x, y) in self.vertical_walls:
            return False

        # Cannot directly continue another vertical wall.
        if (x, y + 1) in self.vertical_walls:
            return False

        if (x, y - 1) in self.vertical_walls:
            return False

        # Cannot cross a horizontal wall at the same anchor.
        if (x, y) in self.horizontal_walls:
            return False

        # Temporarily place the wall.
        self.vertical_walls.add((x, y))

        white_has_path = self.has_path_to_goal("white")
        black_has_path = self.has_path_to_goal("black")

        # Remove the temporary wall.
        self.vertical_walls.remove((x, y))

        if not white_has_path:
            return False

        if not black_has_path:
            return False

        return True

    def generate_legal_wall_moves(self, player):
        legal_wall_moves = []

        if player == "white" and self.white_walls <= 0:
            return legal_wall_moves

        if player == "black" and self.black_walls <= 0:
            return legal_wall_moves

        if player != "white" and player != "black":
            return legal_wall_moves

        # -------------------------
        # Horizontal wall candidates
        # -------------------------

        horizontal_candidates = ALL_WALL_ANCHORS.copy()

        # Horizontal walls cannot overlap existing horizontal walls.
        horizontal_candidates = horizontal_candidates - self.horizontal_walls

        # Horizontal walls cannot cross vertical walls at the same anchor.
        horizontal_candidates = horizontal_candidates - self.vertical_walls

        # Horizontal walls cannot directly continue other horizontal walls.
        for x, y in self.horizontal_walls:
            horizontal_candidates.discard((x - 1, y))
            horizontal_candidates.discard((x + 1, y))

        for x, y in horizontal_candidates:
            if self.is_legal_horizontal_wall(player, x, y):
                legal_wall_moves.append(("horizontal_wall", (x, y)))

        # -------------------------
        # Vertical wall candidates
        # -------------------------

        vertical_candidates = ALL_WALL_ANCHORS.copy()

        # Vertical walls cannot overlap existing vertical walls.
        vertical_candidates = vertical_candidates - self.vertical_walls

        # Vertical walls cannot cross horizontal walls at the same anchor.
        vertical_candidates = vertical_candidates - self.horizontal_walls

        # Vertical walls cannot directly continue other vertical walls.
        for x, y in self.vertical_walls:
            vertical_candidates.discard((x, y - 1))
            vertical_candidates.discard((x, y + 1))

        for x, y in vertical_candidates:
            if self.is_legal_vertical_wall(player, x, y):
                legal_wall_moves.append(("vertical_wall", (x, y)))

        return legal_wall_moves

    def place_horizontal_wall(self, player, x, y):
        if not self.is_legal_horizontal_wall(player, x, y):
            return False

        self.horizontal_walls.add((x, y))

        if player == "white":
            self.white_walls -= 1
        elif player == "black":
            self.black_walls -= 1

        self.switch_player()

        return True

    def place_vertical_wall(self, player, x, y):
        if not self.is_legal_vertical_wall(player, x, y):
            return False

        self.vertical_walls.add((x, y))

        if player == "white":
            self.white_walls -= 1
        elif player == "black":
            self.black_walls -= 1

        self.switch_player()

        return True

    def place_wall(self, player, wall_type, position):
        x, y = position

        if wall_type == "horizontal_wall":
            return self.place_horizontal_wall(player, x, y)

        if wall_type == "vertical_wall":
            return self.place_vertical_wall(player, x, y)

        return False

    # -------------------------
    # Pawn movement helpers
    # -------------------------

    def is_legal_adjacent_move(self, start, end):
        if not self.is_position_on_board(start):
            return False

        if not self.is_position_on_board(end):
            return False

        if not self.are_adjacent(start, end):
            return False

        if self.is_blocked_by_wall(start, end):
            return False

        if self.is_square_occupied(end):
            return False

        return True

    def is_valid_straight_jump(self, player, start, end):
        if not self.is_position_on_board(start):
            return False

        if not self.is_position_on_board(end):
            return False

        opponent_position = self.get_opponent_position(player)

        if opponent_position is None:
            return False

        if self.is_blocked_by_wall(start, opponent_position):
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
        if self.is_blocked_by_wall(middle, end):
            return False

        if self.is_square_occupied(end):
            return False

        return True

    def is_valid_diagonal_jump(self, player, start, end):
        if not self.is_position_on_board(start):
            return False

        if not self.is_position_on_board(end):
            return False

        opponent_position = self.get_opponent_position(player)

        if opponent_position is None:
            return False

        # Diagonal jump only happens if opponent is next to you.
        if not self.are_adjacent(start, opponent_position):
            return False

        if self.is_blocked_by_wall(start, opponent_position):
            return False

        start_x, start_y = start
        opponent_x, opponent_y = opponent_position

        # Direction from you to opponent.
        opponent_dx = opponent_x - start_x
        opponent_dy = opponent_y - start_y

        # The square behind the opponent, where a normal jump would land.
        straight_jump_end_position = (
            opponent_x + opponent_dx,
            opponent_y + opponent_dy,
        )

        straight_jump_is_possible = (
            self.is_position_on_board(straight_jump_end_position)
            and not self.is_blocked_by_wall(opponent_position, straight_jump_end_position)
        )

        # If you can jump straight, diagonal jump is not allowed.
        if straight_jump_is_possible:
            return False

        # Diagonal landing square must be beside the opponent.
        if not self.are_adjacent(opponent_position, end):
            return False

        # But it must also be diagonal from the original start square.
        end_x, end_y = end
        dx = end_x - start_x
        dy = end_y - start_y

        if not (abs(dx) == 1 and abs(dy) == 1):
            return False

        # Wall between opponent and diagonal landing square blocks this move.
        if self.is_blocked_by_wall(opponent_position, end):
            return False

        if self.is_square_occupied(end):
            return False

        return True

    def is_legal_pawn_move(self, player, end):
        start = self.get_player_position(player)

        if start is None:
            return False

        if self.is_legal_adjacent_move(start, end):
            return True

        if self.is_valid_straight_jump(player, start, end):
            return True

        if self.is_valid_diagonal_jump(player, start, end):
            return True

        return False

    def generate_legal_pawn_moves(self, player):
        player_position = self.get_player_position(player)

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
            if self.is_legal_pawn_move(player, end_position):
                legal_moves.append(end_position)

        return legal_moves

    def move_pawn(self, player, end):
        if not self.is_legal_pawn_move(player, end):
            return False

        if player == "white":
            self.white_position = end
        elif player == "black":
            self.black_position = end
        else:
            return False

        if self.get_winner() is None:
            self.switch_player()

        return True

    # -------------------------
    # Legal action generation
    # -------------------------

    def generate_legal_actions(self, player=None):
        if player is None:
            player = self.current_player

        legal_actions = []

        for pawn_move in self.generate_legal_pawn_moves(player):
            legal_actions.append(("pawn", pawn_move))

        legal_actions.extend(self.generate_legal_wall_moves(player))

        return legal_actions

    def apply_action(self, action):
        action_type, position = action
        player = self.current_player

        if action_type == "pawn":
            return self.move_pawn(player, position)

        if action_type == "horizontal_wall":
            x, y = position
            return self.place_horizontal_wall(player, x, y)

        if action_type == "vertical_wall":
            x, y = position
            return self.place_vertical_wall(player, x, y)

        return False

    def next_state(self, action):
        copied_state = self.copy()
        action_was_applied = copied_state.apply_action(action)

        if not action_was_applied:
            return None

        return copied_state

    # -------------------------
    # Display
    # -------------------------

    def print_board(self):
        for y in range(BOARD_SIZE - 1, -1, -1):
            row = str(y) + "   "

            for x in range(BOARD_SIZE):
                position = (x, y)

                if position == self.white_position:
                    row += "W"
                elif position == self.black_position:
                    row += "B"
                else:
                    row += "."

                if x < BOARD_SIZE - 1:
                    if (x, y) in self.vertical_walls or (x, y + 1) in self.vertical_walls:
                        row += " ║ "
                    else:
                        row += "   "

            print(row)

            if y > 0:
                wall_row = "    "

                for x in range(BOARD_SIZE):
                    if (x, y - 1) in self.horizontal_walls or (x - 1, y - 1) in self.horizontal_walls:
                        wall_row += "==  "
                    else:
                        wall_row += "    "

                print(wall_row)

        print()
        print("    0   1   2   3   4   5   6   7   8")


# -------------------------
# Quick tests
# -------------------------

def run_tests():
    state = GameState()

    assert state.white_position == (4, 0)
    assert state.black_position == (4, 8)
    assert state.white_walls == 10
    assert state.black_walls == 10
    assert state.current_player == "white"

    assert state.get_player_position("white") == (4, 0)
    assert state.get_player_position("black") == (4, 8)
    assert state.get_opponent_position("white") == (4, 8)
    assert state.get_opponent_position("black") == (4, 0)

    assert state.is_position_on_board((0, 0)) is True
    assert state.is_position_on_board((8, 8)) is True
    assert state.is_position_on_board((-1, 0)) is False
    assert state.is_position_on_board((9, 0)) is False

    assert state.are_adjacent((4, 4), (4, 5)) is True
    assert state.are_adjacent((4, 4), (5, 4)) is True
    assert state.are_adjacent((4, 4), (5, 5)) is False
    assert state.are_adjacent((4, 4), (4, 6)) is False

    assert state.is_valid_wall_position(0, 0) is True
    assert state.is_valid_wall_position(7, 7) is True
    assert state.is_valid_wall_position(8, 7) is False
    assert state.is_valid_wall_position(7, 8) is False

    assert state.has_path_to_goal("white") is True
    assert state.has_path_to_goal("black") is True

    white_moves = state.generate_legal_pawn_moves("white")
    assert (4, 1) in white_moves
    assert (3, 0) in white_moves
    assert (5, 0) in white_moves

    legal_actions = state.generate_legal_actions()
    assert ("pawn", (4, 1)) in legal_actions
    assert ("horizontal_wall", (0, 0)) in legal_actions
    assert ("vertical_wall", (0, 0)) in legal_actions

    copied_state = state.copy()
    copied_state.white_position = (4, 1)
    copied_state.horizontal_walls.add((3, 3))

    assert state.white_position == (4, 0)
    assert copied_state.white_position == (4, 1)
    assert (3, 3) not in state.horizontal_walls
    assert (3, 3) in copied_state.horizontal_walls

    next_state = state.next_state(("pawn", (4, 1)))
    assert next_state is not None
    assert next_state.white_position == (4, 1)
    assert next_state.current_player == "black"
    assert state.white_position == (4, 0)
    assert state.current_player == "white"

    print("All tests passed")


if __name__ == "__main__":
    run_tests()
