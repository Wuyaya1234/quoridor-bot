# network.py

import torch
import torch.nn as nn

from encoder import TOTAL_ACTIONS, encode_state
from game_state import GameState, BOARD_SIZE


class QuoridorNet(nn.Module):
    def __init__(self):
        super().__init__()

        # Shared board-processing layers.
        # Input shape:  (batch_size, 5, 9, 9)
        # Output shape: (batch_size, 32, 9, 9)
        self.shared_layers = nn.Sequential(
            nn.Conv2d(in_channels=5, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=3, padding=1),
            nn.ReLU(),
        )

        # Policy head:
        # Turns the board features into 209 action scores.
        self.policy_head = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=2, kernel_size=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * BOARD_SIZE * BOARD_SIZE, TOTAL_ACTIONS),
        )

        # Value head:
        # Turns the board features into one number between -1 and +1.
        self.value_head = nn.Sequential(
            nn.Conv2d(in_channels=32, out_channels=1, kernel_size=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(BOARD_SIZE * BOARD_SIZE, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh(),
        )

    def forward(self, x):
        features = self.shared_layers(x)

        policy_logits = self.policy_head(features)

        value = self.value_head(features)

        # value currently has shape (batch_size, 1).
        # We want shape (batch_size,).
        value = value.squeeze(1)

        return policy_logits, value


# -------------------------
# Network tests
# -------------------------

def test_network_output_shapes_for_one_state():
    network = QuoridorNet()

    dummy_input = torch.zeros((1, 5, BOARD_SIZE, BOARD_SIZE), dtype=torch.float32)

    policy_logits, value = network(dummy_input)

    assert policy_logits.shape == (1, TOTAL_ACTIONS)
    assert value.shape == (1,)

    print("test_network_output_shapes_for_one_state passed")


def test_network_output_shapes_for_batch():
    network = QuoridorNet()

    batch_size = 4
    dummy_input = torch.zeros((batch_size, 5, BOARD_SIZE, BOARD_SIZE), dtype=torch.float32)

    policy_logits, value = network(dummy_input)

    assert policy_logits.shape == (batch_size, TOTAL_ACTIONS)
    assert value.shape == (batch_size,)

    print("test_network_output_shapes_for_batch passed")


def test_network_accepts_encoded_state():
    network = QuoridorNet()

    state = GameState()
    encoded_state = encode_state(state)

    # encoded_state has shape (5, 9, 9).
    # PyTorch needs shape (1, 5, 9, 9), so we add a batch dimension.
    input_tensor = torch.tensor(encoded_state, dtype=torch.float32).unsqueeze(0)

    policy_logits, value = network(input_tensor)

    assert policy_logits.shape == (1, TOTAL_ACTIONS)
    assert value.shape == (1,)

    print("test_network_accepts_encoded_state passed")


def test_value_is_between_minus_one_and_one():
    network = QuoridorNet()

    dummy_input = torch.zeros((1, 5, BOARD_SIZE, BOARD_SIZE), dtype=torch.float32)

    policy_logits, value = network(dummy_input)

    assert value.item() >= -1
    assert value.item() <= 1

    print("test_value_is_between_minus_one_and_one passed")


def test_network_can_backpropagate():
    network = QuoridorNet()

    dummy_input = torch.zeros((2, 5, BOARD_SIZE, BOARD_SIZE), dtype=torch.float32)

    policy_logits, value = network(dummy_input)

    # Fake loss just to check gradients can flow.
    loss = policy_logits.sum() + value.sum()

    loss.backward()

    found_gradient = False

    for parameter in network.parameters():
        if parameter.grad is not None:
            found_gradient = True
            break

    assert found_gradient is True

    print("test_network_can_backpropagate passed")


def run_tests():
    test_network_output_shapes_for_one_state()
    test_network_output_shapes_for_batch()
    test_network_accepts_encoded_state()
    test_value_is_between_minus_one_and_one()
    test_network_can_backpropagate()

    print()
    print("All network tests passed")


if __name__ == "__main__":
    run_tests()