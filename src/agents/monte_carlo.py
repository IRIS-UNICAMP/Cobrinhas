import random
from dataclasses import dataclass
from typing import List, Dict

from src.shared import Action, HistoryRecord, Policy, StateActionInfo

from json import JSONEncoder


# Tip taken from:
# https://stackoverflow.com/a/38764817/12603421
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class MonteCarloAgent:
    _history: List[HistoryRecord] = list()
    _state_action_value: Dict = {}
    _episode_counter = 1
    _policy = Policy()
    _chosen_policy: Policy
    _last_reinforcement_factor = float('-inf')
    _use_individual_policies: bool
    _learning_incentive: bool
    _epsilon_step_increment: float
    _initial_epsilon: float
    _reverse_history: bool

    def __init__(self,
                 every_visit: bool = False,
                 gamma=1.01,
                 epsilon_step_increment=0.1,
                 initial_epsilon=1,
                 use_individual_policies=False,
                 learning_incentive=True,
                 reverse_history=True):
        self._gamma = gamma
        self._every_visit = every_visit
        if not use_individual_policies:
            self._policy = Policy()
            self._policy.epsilon_step = epsilon_step_increment
        self._use_individual_policies = use_individual_policies
        self._learning_incentive = learning_incentive
        self._initial_epsilon = initial_epsilon
        self._epsilon_step_increment = epsilon_step_increment
        self._reverse_history = reverse_history

    def dict(self):
        data = {
            "gamma": self._gamma,
            "every_visit": self._every_visit,
            "use_individual_policies": self._use_individual_policies,
            "learning_incentive": self._learning_incentive,
            "reverse_history": self._reverse_history
        }
        if not self._use_individual_policies:
            return {
                **data,
                "epsilon": self.policy.epsilon,
                "epsilon_step_increment": self.policy.epsilon_step
            }
        else:
            return data

    @property
    def state_amount(self) -> int:
        return len(self._state_action_value.keys())

    @property
    def policy(self) -> Policy:
        if self._use_individual_policies:
            return self._chosen_policy
        else:
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

    def init_state_if_needed(self, state: str) -> bool:
        # Initializing specific state dict
        if state not in self._state_action_value.keys():
            self._state_action_value[state] = {
                "counter": 0,
                Action.UP.value: StateActionInfo(Action.UP),
                Action.DOWN.value: StateActionInfo(Action.DOWN),
                Action.LEFT.value: StateActionInfo(Action.LEFT),
                Action.RIGHT.value: StateActionInfo(Action.RIGHT),
            }
            if self._use_individual_policies:
                policy = Policy()
                policy.epsilon = self._initial_epsilon
                policy.epsilon_step = self._epsilon_step_increment
                self._state_action_value[state] = {
                    **self._state_action_value[state],
                    "policy": policy,
                }

            if not self._every_visit:
                self._state_action_value[state] = {
                    **self._state_action_value[state],
                    "has_been_visited": False,
                }
            return False
        return True

    def _reinforce_state_action(self, record: HistoryRecord, factor: float):
        # Increment Counter (N(s,a))
        self._state_action_value[record.state][record.action.value].counter += 1

        # Reinforce (Q(s,a))
        state_action_value = self._state_action_value[record.state][record.action.value].value
        state_action_count = self._state_action_value[record.state][record.action.value].counter
        new_sate_action_value = state_action_value + ((1 / state_action_count) * (factor - state_action_value))
        self._state_action_value[record.state][record.action.value].value = new_sate_action_value

    def _reset_visited_flag(self):
        if self._every_visit:
            raise Exception("Should not need to reset visit flags when the algorithm is every-visit")
        for state in self._state_action_value.keys():
            self._state_action_value[state]["has_been_visited"] = False

    def choose_action(self, state) -> Action:
        self.init_state_if_needed(state)
        self._state_action_value[state]["counter"] += 1
        policy: Policy
        if self._use_individual_policies:
            policy = self._state_action_value[state]["policy"]
            self._chosen_policy = policy
        else:
            policy = self._policy

        random_value = random.random()
        actions = [e for e in Action]
        if random_value <= policy.epsilon:
            return random.choice(actions)
        else:
            best_action: StateActionInfo = StateActionInfo(Action.UP)
            best_action.value = float('-inf')
            last_value = self._state_action_value[state][actions[0].value].value
            all_equal = True
            for action in actions:
                current_value = self._state_action_value[state][action.value].value
                all_equal = (all_equal and last_value == current_value)
                last_value = current_value
                if current_value > best_action.value:
                    best_action = self._state_action_value[state][action.value]

            # There was no better action
            if all_equal:
                return random.choice(actions)

            # up = self._state_action_value[state][Action.UP.value].value
            # down = self._state_action_value[state][Action.DOWN.value].value
            # left = self._state_action_value[state][Action.LEFT.value].value
            # right = self._state_action_value[state][Action.RIGHT.value].value
            # actions_str = f"Actions were UP: {up}, DOWN: {down}, LEFT: {left}, RIGHT: {right}.\nChose: " \
            #               f"{best_action.action.value}."
            # print(actions_str)
            return best_action.action

    def episode_reinforcement(self):
        factor = self._calculate_reinforcement_factor()

        for step, record in enumerate(self._history):
            state_exists = self.init_state_if_needed(record.state)
            if not state_exists:
                self._state_action_value[record.state]["counter"] = 1
                self._chosen_policy = self._state_action_value[record.state]["policy"]
            if not self._every_visit and self._state_action_value[record.state]["has_been_visited"]:
                continue

            if not self._every_visit:
                self._state_action_value[record.state]["has_been_visited"] = True

            if self._use_individual_policies:
                if self._learning_incentive:
                    if self._last_reinforcement_factor < factor:
                        update_epsilon = True
                    else:
                        update_epsilon = False
                else:
                    update_epsilon = True

                if update_epsilon:
                    state_count = self._state_action_value[record.state]["counter"]
                    epsilon_value = self._state_action_value[record.state]["policy"].epsilon
                    epsilon_step = self._state_action_value[record.state]["policy"].epsilon_step
                    self._last_reinforcement_factor = factor
                    self._state_action_value[record.state]["policy"].epsilon = 1 / ((1 / epsilon_value) + epsilon_step)
                    # self._state_action_value[record.state]["policy"].epsilon = 1 / (state_count + epsilon_step)

            self._reinforce_state_action(record, factor)

        if not self._use_individual_policies:
            if self._learning_incentive:
                if self._last_reinforcement_factor < factor:
                    update_epsilon = True
                else:
                    update_epsilon = False
            else:
                update_epsilon = True
            if update_epsilon:
                self._last_reinforcement_factor = factor
                self._policy.epsilon = 1 / ((1 / self._policy.epsilon) + self._policy.epsilon_step)

        print(
            f"Factor: {factor}; Last Best Factor: {self._last_reinforcement_factor};  Epsilon: {self.policy.epsilon}")
        if not self._every_visit:
            self._reset_visited_flag()
        self._history = []
        self._episode_counter += 1

    def _calculate_reinforcement_factor(self):
        factor = 0
        if self._reverse_history:
            history = self._history[::-1]
        else:
            history = self._history
        for step, record in enumerate(history):
            factor += record.reward * pow(self._gamma, step)
        return factor

    @property
    def state_action_values(self):
        return self._state_action_value
