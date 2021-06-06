from dataclasses import dataclass
from enum import Enum
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


Color = Tuple[int, int, int]

