import random
from typing import Set

import pygame
from pygame import Surface

from src.configs import GameConfig
from src.shared import Coord


class Food:
    position: Coord

    def __init__(self, game_config: GameConfig, screen: Surface, available_positions: Set[Coord]):
        self.game = game_config
        self.screen = screen

        # Initializing food position
        self.position = random.choice(list(available_positions))
        self._paint()

    def can_be_eaten(self, mouth_coord: Coord) -> bool:
        return self.position == mouth_coord

    def eat(self, available_positions: Set[Coord]):
        new_position = random.choice(list(available_positions))
        self._replace(new_position)

    def _replace(self, new_position):
        self._erase()
        self.position = new_position
        self._paint()

    def _erase(self):
        pygame.draw.rect(self.screen, self.game.swallow_color,
                         [self.position.x, self.position.y, self.game.block_size, self.game.block_size])

    def _paint(self):
        pygame.draw.rect(self.screen, self.game.food_color,
                         [self.position.x, self.position.y, self.game.block_size, self.game.block_size])