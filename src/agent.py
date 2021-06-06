import random
from dataclasses import dataclass
from typing import List, Dict

from src.shared import Action


class StateActionInfo:
    counter: int = 0  # N
    value: float = 0  # Q(s,a)
    action: Action

    def __init__(self, action: Action):
        self.action = action

    def __str__(self):
        return "{}"


@dataclass()
class Policy:
    epsilon: float = 1
    epsilon_step: float = 0.1
    # desc_action_index: int = 0  # gets the n-th best action
    # alternative_action_pick_slice: float = 1/3  # uses the above 1/3 of the time


@dataclass()
class HistoryRecord:
    state: str
    reward: float
    action: Action


class MonteCarloAgent:
    _history: List[HistoryRecord] = list()
    _state_action_value: Dict = {}
    _episode_counter = 1
    _policy = Policy()
    _last_reinforcement_factor = float('-inf')

    def __init__(self, every_visit: bool = False, gamma=0.99999):
        self._gamma = gamma
        self._every_visit = every_visit

    @property
    def policy(self) -> Policy:
        return self._policy

    def save_to_history(self, state: str, action: Action, reward: float):
        # Save to history
        self._history.append(
            HistoryRecord(
                state=state,
                reward=reward,
                action=action
            )
        )

    def _init_state_if_needed(self, state: str):
        # Initializing specific state dict
        if state not in self._state_action_value.keys():
            self._state_action_value[state] = {
                "has_been_visited": False,
                Action.UP.value: StateActionInfo(Action.UP),
                Action.DOWN.value: StateActionInfo(Action.DOWN),
                Action.LEFT.value: StateActionInfo(Action.LEFT),
                Action.RIGHT.value: StateActionInfo(Action.RIGHT),
            }

    def _reinforce_state_action(self, record: HistoryRecord, factor: float):
        # Increment Counter (N)
        self._state_action_value[record.state][record.action.value].counter += 1

        # Reinforce (Q(s,a))
        state_action_value = self._state_action_value[record.state][record.action.value].value
        state_action_count = self._state_action_value[record.state][record.action.value].counter
        new_sate_action_value = state_action_value + 1/(state_action_count * (factor - state_action_value))
        self._state_action_value[record.state][record.action.value].value = new_sate_action_value

    def _reset_visited_flag(self):
        if self._every_visit:
            raise Exception("Should not need to reset visit flags when the algorithm is every-visit")
        for state in self._state_action_value.keys():
            self._state_action_value[state]["has_been_visited"] = False

    def choose_action(self, state) -> Action:
        self._init_state_if_needed(state)

        random_value = random.random()
        actions = [e for e in Action]
        if random_value <= self._policy.epsilon:
            return random.choice(actions)
        else:
            best_action: StateActionInfo = StateActionInfo(Action.UP)
            for action in actions:
                if self._state_action_value[state][action.value].value > best_action.value:
                    best_action = self._state_action_value[state][action.value]

            # There was no better action
            if best_action.value == 0:
                return random.choice(actions)

            return best_action.action

    def episode_reinforcement(self):
        factor = self._calculate_reinforcement_factor()

        for step, record in enumerate(self._history):
            if not self._every_visit and self._state_action_value[record.state]["has_been_visited"]:
                continue

            self._state_action_value[record.state]["has_been_visited"] = True
            self._reinforce_state_action(record, factor)

        self._episode_counter += 1

        # Only change the epsilon if results were satisfactory
        if self._last_reinforcement_factor < factor:
            self._last_reinforcement_factor = factor
            self._policy.epsilon = 1 / ((1/self._policy.epsilon) + self._policy.epsilon_step)

        print(f"Factor: {factor}; Last Best Factor: {self._last_reinforcement_factor};  Epsilon: {self._policy.epsilon}")

        self._history = []

    def _calculate_reinforcement_factor(self):
        factor = 0
        for step, record in enumerate(self._history):
            factor += record.reward * pow(self._gamma, step)
        return factor
