from dataclasses import field
from typing import List
import random

import pygame
from pygame import Surface

from src.configs import GameConfig, SnakeConfig
from src.exceptions import WallHit, BodyHit
from src.shared import Velocity, Coord, Direction


class Snake:
    _velocity: Velocity = field(default=None)
    _body: List[Coord] = field(default_factory=set)

    def __init__(self, game_config: GameConfig, screen: Surface, config: SnakeConfig, available_positions: List[Coord]):
        self.game_config = game_config
        self.screen = screen
        self.config = config
        self.available_positions = available_positions

        self._initialize_body()

    @property
    def head(self) -> Coord:
        return self._body[0]

    @property
    def body(self):
        return self._body

    @property
    def velocity(self):
        return self._velocity

    def change_velocity(self, velocity: Velocity):
        self._velocity = velocity

    def can_slither(self) -> Exception:
        new_head = self._body[0].translate(self._velocity)
        wall_danger = new_head.x < 0 or new_head.x >= self.game_config.screen_width \
                      or new_head.y < 0 or new_head.y >= self.game_config.screen_height
        body_danger = new_head in self._body

        if wall_danger:
            return WallHit(new_head)
        if body_danger:
            return BodyHit(new_head)

    def slither(self, has_eaten: bool):
        head = self._body[0].translate(self._velocity)
        # print(f"Slithering head to ({head.x},{head.y})")
        evaluation = self.can_slither()
        if evaluation is not None:
            raise evaluation

        self._body.insert(0, head)
        if not has_eaten:
            tail = self._body.pop()
            self._erase_block(tail)
            if len(self._body) > 1:
                self._paint_block(self._body[1])
        self._paint_head(head)

    def _snaky_linearized_screen(self, max_length=-1) -> List[Coord]:
        """
            This function takes the screen coordinates and block size and returns a linearized
            array of the screen in a "snaky" manner. That is, a linearized 2d-array that follows
            the "zig-zag" of the snake through the screen.
        """
        linearized_vector: List[Coord] = []

        for y in range(0, self.game_config.screen_height, self.game_config.block_size):
            for x in range(0, self.game_config.screen_width, self.game_config.block_size):
                if (y // self.game_config.block_size) % 2 == 0:
                    linearized_vector.append(Coord(x, y))
                else:
                    if x != 0:
                        linearized_vector.append(Coord(self.game_config.screen_width - x, y))
                    if self.game_config.screen_width - x == self.game_config.block_size:
                        # It's the last iteration, we have to insert one more, otherwise y will be increased
                        # before we can repeat the x coordinate
                        linearized_vector.append(Coord(0, y))

                if len(linearized_vector) == max_length:
                    return linearized_vector

        return linearized_vector

    def _set_default_velocity(self):
        # todo improve
        self._velocity = Direction(self.game_config.block_size).right

    def _initialize_body(self):
        if self.config.random_initial_pos:
            self._body = [random.choice(self.available_positions)]
        else:
            # Creating a linearized version of the screen of the size of the snake
            linearized_vector = self._snaky_linearized_screen(max_length=self.config.initial_length)
            linearized_vector.reverse()
            self._body = linearized_vector
        self._set_default_velocity()
        self.paint()

    def _paint_block(self, coord: Coord):
        if self.game_config.show_game:
            pygame.draw.rect(self.screen, self.game_config.snake_color,
                             [coord.x, coord.y, self.game_config.block_size, self.game_config.block_size])

    def _erase_block(self, coord: Coord):
        if self.game_config.show_game:
            pygame.draw.rect(self.screen, self.game_config.background_color,
                             [coord.x, coord.y, self.game_config.block_size, self.game_config.block_size])

    def _paint_head(self, coord: Coord):
        if self.game_config.show_game:
            pygame.draw.rect(self.screen, self.game_config.head_color,
                             [coord.x, coord.y, self.game_config.block_size, self.game_config.block_size])

    def paint(self):
        for x in self._body:
            self._paint_block(x)
