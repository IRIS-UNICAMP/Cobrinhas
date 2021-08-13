from abc import ABC, abstractmethod
import random
from typing import List, Dict

from src.shared import Action, StateActionInfo, Policy, HistoryRecord


class AbstractAgent(ABC):
    _actions = [e for e in Action]
    _state_action_value: Dict = {}
    _use_individual_policies: bool
    _policy: Policy
    _history: List[HistoryRecord] = list()
    _chosen_policy: Policy
    _last_action_info: StateActionInfo
    _last_state: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self):
        return self._name

    def best_action(self, state: str) -> StateActionInfo:
        best_action: StateActionInfo = StateActionInfo(Action.UP)
        best_action.value = float('-inf')
        last_value = self._state_action_value[state][self._actions[0].value].value
        all_equal = True
        for action in self._actions:
            current_value = self._state_action_value[state][action.value].value
            all_equal = (all_equal and last_value == current_value)
            last_value = current_value
            if current_value > best_action.value:
                best_action = self._state_action_value[state][action.value]

        # There was no better action
        if all_equal:
            return random.choice(self.state_actions(state))

        # up = self._state_action_value[state][Action.UP.value].value
        # down = self._state_action_value[state][Action.DOWN.value].value
        # left = self._state_action_value[state][Action.LEFT.value].value
        # right = self._state_action_value[state][Action.RIGHT.value].value
        # actions_str = f"Actions were UP: {up}, DOWN: {down}, LEFT: {left}, RIGHT: {right}.\nChose: " \
        #               f"{best_action.action.value}."
        return best_action

    def choose_action(self, state) -> StateActionInfo:
        self.init_state_if_needed(state)

        # Increment state counter (useless for the algorithm itself)
        self._state_action_value[state]["counter"] += 1
        policy: Policy
        if self._use_individual_policies:
            policy = self._state_action_value[state]["policy"]
            self._chosen_policy = policy
        else:
            policy = self._policy

        random_value = random.random()
        if random_value <= policy.epsilon:
            best_action = random.choice(self.state_actions(state))
        else:
            best_action = self.best_action(state)

        # Increment Counter (N(s,a))
        self._state_action_value[state][best_action.action.value].counter += 1

        self.set_last_action_info(state, best_action)
        return best_action

    def set_last_action_info(self, state: str, action_info: StateActionInfo):
        self._last_state = state
        self._last_action_info = action_info

    def get_action_info(self, state: str, action: Action) -> StateActionInfo:
        return self._state_action_value[state][action.value]

    def save_to_history(self, state: str, action: Action, reward: float):
        # Save to history
        self._history.append(
            HistoryRecord(
                state=state,
                reward=reward,
                action=action
            )
        )

    def state_actions(self, state: str) -> List[StateActionInfo]:
        return [self._state_action_value[state][x.value] for x in self._actions]

    @abstractmethod
    def plottable_configs(self) -> List[str]:
        pass

    @property
    def policy(self) -> Policy:
        if self._use_individual_policies:
            return self._chosen_policy
        else:
            return self._policy

    @property
    def state_amount(self) -> int:
        return len(self._state_action_value.keys())

    @property
    def state_action_values(self):
        return self._state_action_value

    @abstractmethod
    def init_state_if_needed(self, state: str) -> bool:
        pass

    @abstractmethod
    def episode_reinforcement(self):
        pass

    @abstractmethod
    def step_reinforcement(self, reward: int, current_state: str):
        pass

    @abstractmethod
    def dict(self) -> Dict:
        pass
