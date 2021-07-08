from abc import ABC, abstractmethod
from plistlib import Dict

from src.shared import Action


class AbstractAgent(ABC):

    @property
    @abstractmethod
    def state_action_values(self) -> Dict:
        pass

    @abstractmethod
    def save_to_history(self, state: str, action: Action, reward: float):
        pass

    @abstractmethod
    def init_state_if_needed(self, state: str) -> bool:
        pass

    @abstractmethod
    def choose_action(self, state) -> Action:
        pass

    @abstractmethod
    def state_amount(self) -> int:
        pass

    @abstractmethod
    def episode_reinforcement(self):
        pass

    @abstractmethod
    def step_reinforcement(self):
        pass

    @abstractmethod
    def dict(self) -> Dict:
        pass
