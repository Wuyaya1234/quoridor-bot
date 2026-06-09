# mcts.py

from game_state import GameState

import random

def random_playout(state, max_moves=200):
    copied_state = state.copy()

    for _ in range(max_moves):
        if copied_state.is_terminal():
            break

        legal_actions = copied_state.generate_legal_actions()
        action = random.choice(legal_actions)
        copied_state.apply_action(action)

    winner = copied_state.get_winner()

    if winner == "white":
        return 1

    if winner == "black":
        return -1

    return 0

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

        for action in legal_actions:
            new_state = self.state.next_state(action)

            child_node = Node(
                state=new_state,
                parent=self,
                action_taken=action,
                prior=0
            )

            self.children[action] = child_node 

    def backpropagate(self, value):
        self.N += 1
        self.W += value
        self.Q = self.W / self.N

        if self.parent is not None:
            self.parent.backpropagate(value)
    
    def select_child(self, c=1.0):
        best_child = None
        best_score = float("-inf")

        for child in self.children.values():
            score = child.Q + c * child.P * (self.N ** 0.5) / (1 + child.N)

            if score > best_score:
                best_score = score
                best_child = child

        return best_child
    
    def run_simulation(self):

        node = self

        while node.is_expanded():
            node = node.select_child()

        value = random_playout(node.state)

        node.expand()
        node.backpropagate(value)
    

    def select_action(self):
        best_action = None
        best_visit_count = -1

        for action, child in self.children.items():
            if child.N > best_visit_count:
                best_visit_count = child.N
                best_action = action

        return best_action




state = GameState()

root = Node(state)

for _ in range(100):
    root.run_simulation()
    best_action = root.select_action()
    print(best_action)


for child in root.children.values():
    print(child.N, child.Q)