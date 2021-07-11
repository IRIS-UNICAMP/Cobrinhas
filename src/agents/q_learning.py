from src.agents.abstract_agent import AbstractAgent
from src.shared import Action, Policy, StateActionInfo

from json import JSONEncoder


# Tip taken from:
# https://stackoverflow.com/a/38764817/12603421
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class QLearning(AbstractAgent):

    # unneeded methods
    def episode_reinforcement(self):
        pass

    _episode_counter = 1
    _last_reinforcement_factor = float('-inf')
    _epsilon_step_increment: float
    _initial_epsilon: float
    _learning_incentive: bool
    _alpha: float

    def __init__(self,
                 gamma=1.01,
                 epsilon_step_increment=0.1,
                 initial_epsilon=1,
                 learning_incentive=False,
                 use_individual_policies=False,
                 alpha=0.2):
        self._gamma = gamma
        if not use_individual_policies:
            self._policy = Policy()
            self._policy.epsilon_step = epsilon_step_increment
        self._use_individual_policies = use_individual_policies
        self._initial_epsilon = initial_epsilon
        self._epsilon_step_increment = epsilon_step_increment
        self._learning_incentive = learning_incentive
        self._alpha = alpha

    def dict(self):
        data = {
            "gamma": self._gamma,
            "use_individual_policies": self._use_individual_policies,
        }
        if not self._use_individual_policies:
            return {
                **data,
                "epsilon": self.policy.epsilon,
                "epsilon_step_increment": self.policy.epsilon_step
            }
        else:
            return data

    def init_state_if_needed(self, state: str) -> bool:
        # Initializing specific state dict
        if state not in self._state_action_value.keys():
            self._state_action_value[state] = {
                "counter": 1,
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
            return False
        return True

    def step_reinforcement(self, reward: int, current_state: str):
        max_action_value = max(x.value for x in self.state_actions(current_state))
        deviation = reward + self._gamma * max_action_value - self._last_action_info.value
        new_action_value = self._last_action_info.value + self._alpha * deviation
        self._state_action_value[self._last_state][self._last_action_info.action.value].value = new_action_value

        if self._use_individual_policies:
            # state_count = self._state_action_value[last_state]["counter"]
            epsilon_value = self._state_action_value[self._last_state]["policy"].epsilon
            epsilon_step = self._state_action_value[self._last_state]["policy"].epsilon_step
            self._state_action_value[self._last_state]["policy"].epsilon = 1 / ((1 / epsilon_value) + epsilon_step)
            # self._state_action_value[record.state]["policy"].epsilon = 1 / (state_count + epsilon_step)
        else:
            self._policy.epsilon = 1 / ((1 / self._policy.epsilon) + self._policy.epsilon_step)
