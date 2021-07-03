from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Tuple, List

import pygame


@dataclass(frozen=True)
class Velocity:
    x: int
    y: int


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def translate(self, velocity: Velocity):
        return Coord(self.x + velocity.x, self.y + velocity.y)

    def to_array(self) -> List:
        return [self.x, self.y]


class Action(Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


def map_action_to_keypress(action: Action):
    if action == Action.UP:
        return pygame.K_UP
    elif action == Action.DOWN:
        return pygame.K_DOWN
    elif action == Action.LEFT:
        return pygame.K_LEFT
    elif action == Action.RIGHT:
        return pygame.K_RIGHT
    else:
        raise ValueError(f"Unknown action {str(action)}")


class Colors(Enum):
    BLUE = (67, 59, 103)
    RED = (200, 112, 126)
    SWALLOW_GREEN = (0, 71, 48)
    HEAD = (0, 255, 150)
    GOLD = pygame.color.Color('gold3')
    LAVENDER_BLUSH = pygame.color.Color('lavenderblush3')


class Direction:
    def __init__(self, block_size):
        self.up = Velocity(0, -block_size)
        self.down = Velocity(0, block_size)
        self.left = Velocity(-block_size, 0)
        self.right = Velocity(block_size, 0)

    def all(self) -> List[Velocity]:
        return [self.up, self.down, self.left, self.right]


class ActionTakerPolicy(IntEnum):
    HUMAN = 0
    AI_AGENT = 1
    MIXED = 2
    MIXED_FOOD_AI = 3


Color = Tuple[int, int, int]


@dataclass()
class HistoryRecord:
    state: str
    reward: float
    action: Action


class Policy:
    epsilon: float = 1
    epsilon_step: float = 0.1

    # desc_action_index: int = 0  # gets the n-th best action
    # alternative_action_pick_slice: float = 1/3  # uses the above 1/3 of the time

    def to_json(self):
        return {
            "epsilon": self.epsilon,
            "epsilon_step": self.epsilon_step,
        }


class StateActionInfo:
    counter: int = 0  # N
    value: float = 0  # Q(s,a)
    action: Action
    policy: Policy = Policy()

    def __init__(self, action: Action):
        self.action = action

    def to_json(self):
        return {
            "counter": self.counter,
            "value": self.value,
        }