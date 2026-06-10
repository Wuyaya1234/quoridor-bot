# encoder.py

import numpy as np

from game_state import GameState, BOARD_SIZE


PAWN_ACTIONS = BOARD_SIZE * BOARD_SIZE
WALL_GRID_SIZE = BOARD_SIZE - 1
WALL_ACTIONS = WALL_GRID_SIZE * WALL_GRID_SIZE
TOTAL_ACTIONS = PAWN_ACTIONS + WALL_ACTIONS + WALL_ACTIONS


def encode_state(state):
    encoded = np.zeros((5, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)

    # Channel 0: white pawn position
    white_x, white_y = state.white_position
    encoded[0][white_y][white_x] = 1

    # Channel 1: black pawn position
    black_x, black_y = state.black_position
    encoded[1][black_y][black_x] = 1

    # Channel 2: horizontal wall roots
    for x, y in state.horizontal_walls:
        encoded[2][y][x] = 1

    # Channel 3: vertical wall roots
    for x, y in state.vertical_walls:
        encoded[3][y][x] = 1

    # Channel 4: current player
    # All 1s means white to move.
    # All 0s means black to move.
    if state.current_player == "white":
        encoded[4][:, :] = 1

    return encoded


def encode_action(action):
    action_type, position = action
    x, y = position

    if action_type == "pawn":
        return y * BOARD_SIZE + x

    if action_type == "horizontal_wall":
        return PAWN_ACTIONS + y * WALL_GRID_SIZE + x

    if action_type == "vertical_wall":
        return PAWN_ACTIONS + WALL_ACTIONS + y * WALL_GRID_SIZE + x

    return None


def decode_action(action_id):
    if action_id < 0 or action_id >= TOTAL_ACTIONS:
        return None

    if action_id < PAWN_ACTIONS:
        x = action_id % BOARD_SIZE
        y = action_id // BOARD_SIZE
        return ("pawn", (x, y))

    if action_id < PAWN_ACTIONS + WALL_ACTIONS:
        wall_id = action_id - PAWN_ACTIONS
        x = wall_id % WALL_GRID_SIZE
        y = wall_id // WALL_GRID_SIZE
        return ("horizontal_wall", (x, y))

    wall_id = action_id - PAWN_ACTIONS - WALL_ACTIONS
    x = wall_id % WALL_GRID_SIZE
    y = wall_id // WALL_GRID_SIZE
    return ("vertical_wall", (x, y))




# -------------------------
# Encoder tests
# -------------------------

def test_encode_starting_state():
    state = GameState()

    encoded = encode_state(state)

    assert encoded.shape == (5, BOARD_SIZE, BOARD_SIZE)

    # White starts at (4, 0), so array index is [y][x] = [0][4].
    assert encoded[0][0][4] == 1
    assert encoded[0].sum() == 1

    # Black starts at (4, 8), so array index is [y][x] = [8][4].
    assert encoded[1][8][4] == 1
    assert encoded[1].sum() == 1

    # No walls at the start.
    assert encoded[2].sum() == 0
    assert encoded[3].sum() == 0

    # White moves first, so current-player channel should be all 1s.
    assert encoded[4].sum() == BOARD_SIZE * BOARD_SIZE

    print("test_encode_starting_state passed")


def test_encode_walls():
    state = GameState()

    state.horizontal_walls.add((3, 4))
    state.vertical_walls.add((5, 6))

    encoded = encode_state(state)

    assert encoded[2][4][3] == 1
    assert encoded[2].sum() == 1

    assert encoded[3][6][5] == 1
    assert encoded[3].sum() == 1

    print("test_encode_walls passed")


def test_encode_black_to_move():
    state = GameState(current_player="black")

    encoded = encode_state(state)

    # Black to move means current-player channel is all 0s.
    assert encoded[4].sum() == 0

    print("test_encode_black_to_move passed")


def test_encode_and_decode_actions():
    actions = [
        ("pawn", (4, 1)),
        ("horizontal_wall", (3, 5)),
        ("vertical_wall", (6, 2)),
    ]

    for action in actions:
        action_id = encode_action(action)
        decoded_action = decode_action(action_id)

        assert decoded_action == action

    assert encode_action(("pawn", (4, 1))) == 13
    assert encode_action(("horizontal_wall", (3, 5))) == 124
    assert encode_action(("vertical_wall", (6, 2))) == 167

    assert decode_action(13) == ("pawn", (4, 1))
    assert decode_action(124) == ("horizontal_wall", (3, 5))
    assert decode_action(167) == ("vertical_wall", (6, 2))

    assert decode_action(-1) is None
    assert decode_action(TOTAL_ACTIONS) is None

    print("test_encode_and_decode_actions passed")

def run_tests():
    test_encode_starting_state()
    test_encode_walls()
    test_encode_black_to_move()
    test_encode_and_decode_actions()

    print()
    print("All encoder tests passed")


if __name__ == "__main__":
    run_tests()