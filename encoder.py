# encoder.py

import numpy as np

from game_state import GameState, BOARD_SIZE


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


def run_tests():
    test_encode_starting_state()
    test_encode_walls()
    test_encode_black_to_move()

    print()
    print("All encoder tests passed")


if __name__ == "__main__":
    run_tests()