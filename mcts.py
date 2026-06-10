# mcts.py

from game_state import GameState

import random

class SimpleEvaluator:
    def __init__(self):
        pass
    
    def evaluate(self, state):
        legal_actions = state.generate_legal_actions()

        if not legal_actions:
            return {}, 0
        
        equal_prior = 1/ len(legal_actions)

        policy = {}
        for action in legal_actions:
            policy[action] = equal_prior
        
        value = 0

        return policy, value


class Node:
    def __init__(self, state, parent=None, action_taken=None, prior=0):
        self.state = state
        self.parent = parent
        self.action_taken = action_taken

        self.P = prior      # Prior probability
        self.N = 0          # Visit count
        self.W = 0          # Total value
        self.Q = 0          # Average value

        self.children = {}

    def is_expanded(self):
        return bool(self.children)

    def expand(self, policy=None):
        if self.is_expanded():
            return

        legal_actions = self.state.generate_legal_actions()

        if not legal_actions:
            return

        # If no policy is provided, treat every legal move equally.
        if policy is None:
            equal_prior = 1 / len(legal_actions)
            policy = {}

            for action in legal_actions:
                policy[action] = equal_prior

        for action in legal_actions:
            new_state = self.state.next_state(action)

            # This should not happen if generate_legal_actions() is correct,
            # but it protects MCTS from crashing if there is a bug elsewhere.
            if new_state is None:
                continue

            child_node = Node(
                state=new_state,
                parent=self,
                action_taken=action,
                prior=policy.get(action, 0)
            )

            self.children[action] = child_node

    def select_child(self, c=1.0):
        best_child = None
        best_score = float("-inf")

        for child in self.children.values():
            # child.Q is from the child player's perspective.
            # The current player wants the child position to be bad for the opponent.
            exploitation_score = -child.Q

            exploration_score = c * child.P * (self.N ** 0.5) / (1 + child.N)

            score = exploitation_score + exploration_score

            if score > best_score:
                best_score = score
                best_child = child

        return best_child

    def backpropagate(self, value):
        self.N += 1
        self.W += value
        self.Q = self.W / self.N

        # Flip the value when moving to the parent,
        # because the parent is the opponent's perspective.
        if self.parent is not None:
            self.parent.backpropagate(-value)


class MCTS:
    def __init__(self, simulations=100, evaluator=None):
        self.simulations = simulations

        if evaluator is None:
            self.evaluator = SimpleEvaluator()
        else:
            self.evaluator = evaluator

    def search(self, state, debug=False):
        root = Node(state)

        for _ in range(self.simulations):
            self.run_simulation(root)

        if debug:
            self.print_root_stats(root)

        best_action = self.select_action(root)
        visit_policy = self.get_visit_policy(root)

        return best_action, visit_policy

    def run_simulation(self, root):
        node = root

        # Selection phase:
        # Move down the tree while the current node has children.
        while node.is_expanded():
            node = node.select_child()

        # Evaluation phase:
        policy, value = self.evaluator.evaluate(node.state)

        # Expansion phase:
        # Expand the leaf after evaluating it.
        if not node.state.is_terminal():
            node.expand(policy)

        # Backpropagation phase:
        # Send the value back up the tree.
        node.backpropagate(value)

    def random_playout(self, state, player_to_value_for, max_moves=200):
        copied_state = state.copy()

        for _ in range(max_moves):
            if copied_state.is_terminal():
                break

            legal_actions = copied_state.generate_legal_actions()

            if not legal_actions:
                break

            action = random.choice(legal_actions)
            copied_state.apply_action(action)

        winner = copied_state.get_winner()

        if winner == player_to_value_for:
            return 1

        if winner is None:
            return 0

        return -1

    def select_action(self, root):
        best_action = None
        best_visit_count = -1

        for action, child in root.children.items():
            if child.N > best_visit_count:
                best_visit_count = child.N
                best_action = action

        return best_action

    def print_root_stats(self, root, top_n=10):
        sorted_children = sorted(
            root.children.items(),
            key=lambda item: item[1].N,
            reverse=True
        )

        print()
        print(f"Top {top_n} root moves:")
        print("--------------------")

        for action, child in sorted_children[:top_n]:
            # child.Q is from the opponent's perspective after root plays action.
            # So -child.Q is the root player's view of that move.
            root_view_q = -child.Q

            print(
                f"Action: {action}, "
                f"N: {child.N}, "
                f"Q from child view: {child.Q:.3f}, "
                f"Q from root view: {root_view_q:.3f}, "
                f"P: {child.P:.3f}"
            )

    def get_visit_policy(self, root): 
        children = root.children
        visit_policy = {}

        if not children:
            return {}

        total_visits = 0

        for child in children.values():
            total_visits += child.N

        if total_visits == 0:
            equal_probability = 1 / len(children)

            for action in children:
                visit_policy[action] = equal_probability

            return visit_policy

        for action, child in children.items():
            visit_policy[action] = child.N / total_visits
        
        return visit_policy

    def sample_action_from_policy(self, visit_policy):
        if not visit_policy:
            return None

        actions = list(visit_policy.keys())
        probabilities = list(visit_policy.values())

        action = random.choices(actions, weights=probabilities, k=1)[0]

        return action

    def self_play_game(self, max_moves=100):
        state = GameState()
        training_examples = []

        for _ in range(max_moves):
            if state.is_terminal():
                break

            current_player = state.current_player

            best_action, visit_policy = self.search(state)

            action = self.sample_action_from_policy(visit_policy)

            training_examples.append(
                (state.copy(), visit_policy, current_player)
            )

            state.apply_action(action)

        winner = state.get_winner()

        final_examples = []

        for old_state, visit_policy, player in training_examples:
            if winner is None:
                value = 0
            elif winner == player:
                value = 1
            else:
                value = -1

            final_examples.append(
                (old_state, visit_policy, value)
            )

        return final_examples, winner

# -------------------------
# Basic MCTS tests
# -------------------------

def test_node_expansion():
    state = GameState()
    root = Node(state)

    assert root.is_expanded() is False

    root.expand()

    legal_actions = state.generate_legal_actions()

    assert root.is_expanded() is True
    assert len(root.children) == len(legal_actions)

    for action, child in root.children.items():
        assert action in legal_actions
        assert child.parent is root
        assert child.action_taken == action
        assert child.state is not state
        assert child.P > 0

    print("test_node_expansion passed")


def test_backpropagation_flips_value():
    state = GameState()
    root = Node(state)

    action = ("pawn", (4, 1))
    child_state = state.next_state(action)

    child = Node(
        state=child_state,
        parent=root,
        action_taken=action,
        prior=1
    )

    root.children[action] = child

    # +1 means good for the child node's current player.
    child.backpropagate(1)

    assert child.N == 1
    assert child.W == 1
    assert child.Q == 1

    # Root gets the opposite value because root is the opponent's perspective.
    assert root.N == 1
    assert root.W == -1
    assert root.Q == -1

    print("test_backpropagation_flips_value passed")


def test_mcts_returns_legal_action():
    state = GameState()
    mcts = MCTS(simulations=20)

    best_action, visit_policy = mcts.search(state)

    legal_actions = state.generate_legal_actions()

    assert best_action in legal_actions
    assert isinstance(visit_policy, dict)
    assert best_action in visit_policy
    total_probability = sum(visit_policy.values())

    assert abs(total_probability - 1) < 0.000001

    print("test_mcts_returns_legal_action passed")


def test_sample_action_from_policy_returns_valid_action():
    mcts = MCTS()

    visit_policy = {
        ("pawn", (4, 1)): 0.75,
        ("pawn", (3, 0)): 0.25,
    }

    action = mcts.sample_action_from_policy(visit_policy)

    assert action in visit_policy

    print("test_sample_action_from_policy_returns_valid_action passed")

def test_self_play_game_returns_valid_examples():
    random.seed(1)

    mcts = MCTS(simulations=5)

    examples, winner = mcts.self_play_game(max_moves=20)

    # self_play_game should return a list of training examples.
    assert isinstance(examples, list)

    # winner should either be one of the two players, or None if max_moves was reached.
    assert winner == "white" or winner == "black" or winner is None

    for example in examples:
        # Each example should have exactly:
        # state, visit_policy, value
        assert len(example) == 3

        state, visit_policy, value = example

        # State should be a copied GameState object.
        assert isinstance(state, GameState)

        # visit_policy should map action -> probability.
        assert isinstance(visit_policy, dict)

        # value should be from the stored player's perspective:
        # +1 = that player won
        # -1 = that player lost
        # 0 = draw / no winner
        assert value in [-1, 0, 1]

        # If the visit policy is non-empty, probabilities should add up to 1.
        if visit_policy:
            total_probability = sum(visit_policy.values())
            assert abs(total_probability - 1) < 0.000001

            for action, probability in visit_policy.items():
                # Action should look like:
                # ("pawn", (x, y))
                # ("horizontal_wall", (x, y))
                # ("vertical_wall", (x, y))
                assert isinstance(action, tuple)
                assert len(action) == 2

                action_type, position = action

                assert action_type in [
                    "pawn",
                    "horizontal_wall",
                    "vertical_wall",
                ]

                assert isinstance(position, tuple)
                assert len(position) == 2

                # Probability should be valid.
                assert probability >= 0
                assert probability <= 1

    print("test_self_play_game_returns_valid_examples passed")


def run_tests():
    test_node_expansion()
    test_backpropagation_flips_value()
    test_mcts_returns_legal_action()
    test_sample_action_from_policy_returns_valid_action()
    test_self_play_game_returns_valid_examples()

    print()
    print("All MCTS tests passed")


# -------------------------
# Manual run
# -------------------------

if __name__ == "__main__":
    random.seed(1)

    run_tests()

    print()
    print("Running MCTS search...")

    state = GameState()

    mcts = MCTS(simulations=10)
    best_action, visit_policy = mcts.search(state, debug=False)

    print()
    print("Best action:", best_action)

    examples, winner = mcts.self_play_game(max_moves=50)

    print("Winner:", winner)
    print("Number of examples:", len(examples))