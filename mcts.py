# mcts.py

from game_state import GameState

import random

class Node:

    def __init__(self, state, parent=None, action_taken=None, prior=0):
        # your code here
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

    def expand(self):
        if self.is_expanded():
            return 

        legal_actions = self.state.generate_legal_actions()

        if not legal_actions:
            return

        prior = 1 / len(legal_actions)

        for action in legal_actions:
            new_state = self.state.next_state(action)

            child_node = Node(
                state=new_state,
                parent=self,
                action_taken=action,
                prior=prior
            )

            self.children[action] = child_node 

    def select_child(self, c=1.0):
        best_child = None
        best_score = float("-inf")

        for child in self.children.values():
            score = child.Q + c * child.P * (self.N ** 0.5) / (1 + child.N)

            if score > best_score:
                best_score = score
                best_child = child

        return best_child
    
    def backpropagate(self, value):
        self.N += 1
        self.W += value
        self.Q = self.W / self.N

        if self.parent is not None:
            self.parent.backpropagate(value)



class MCTS:
    def __init__(self, simulations=100):
        self.simulations = simulations

    def search(self, state):
        root = Node(state)

        for _ in range(self.simulations):
            self.run_simulation(root)

        return self.select_action(root)

    def run_simulation(self, root):
        node = root

        while node.is_expanded():
            node = node.select_child()

        value = self.random_playout(node.state)

        if not node.state.is_terminal():
            node.expand()

        node.backpropagate(value)

    def random_playout(self, state, max_moves=200):
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

        if winner == "white":
            return 1

        if winner == "black":
            return -1

        return 0

    def select_action(self, root):
        best_action = None
        best_visit_count = -1

        for action, child in root.children.items():
            if child.N > best_visit_count:
                best_visit_count = child.N
                best_action = action

        return best_action






mcts = MCTS(simulations=100)
print(mcts.search(GameState()))