from dataclasses import field
from typing import List
import random

import pygame
from pygame import Surface

from src.configs import GameConfig, SnakeConfig
from src.food import Food
from src.shared import Velocity, Coord, Direction, Problem, Action, Color, Colors


class Snake:
    _velocity: Velocity = field(default=None)
    _body: List[Coord] = field(default_factory=set)
    rightmost_positions = set()
    leftmost_positions = set()

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

    def can_slither(self) -> Problem:
        new_head = self._body[0].translate(self._velocity)
        wall_danger = new_head.x < 0 or new_head.x >= self.game_config.screen_width \
                      or new_head.y < 0 or new_head.y >= self.game_config.screen_height
        body_danger = new_head in self._body

        if wall_danger:
            return Problem.WALL_HIT
        if body_danger:
            return Problem.BODY_HIT

    def slither(self, has_eaten: bool):
        head = self._body[0].translate(self._velocity)
        # print(f"Slithering head to ({head.x},{head.y})")
        evaluation = self.can_slither()
        if evaluation is not None:
            return evaluation

        self._body.insert(0, head)
        if not has_eaten:
            tail = self._body.pop()
            self._erase_block(tail)
            if len(self._body) > 1:
                self._paint_block(self._body[1])
        self._paint_head(head)

    def paint_sideways(self):
        if self.game_config.paint_sideways:
            for coord in self.rightmost_positions:
                self._paint_block(coord, Colors.RIGHT.value)

            for coord in self.leftmost_positions:
                self._paint_block(coord, Colors.LEFT.value)

    def erase_sideways(self):
        if self.game_config.paint_sideways:
            for coord in self.rightmost_positions:
                self._erase_block(coord)

            for coord in self.leftmost_positions:
                self._erase_block(coord)

    def sideways_xray(self, available_positions: List[Coord]):
        self.rightmost_positions = set()
        self.leftmost_positions = set()
        for coord in self.rightmost_available_positions(available_positions):
            self.rightmost_positions.add(coord)

        for coord in self.leftmost_available_positions(available_positions):
            self.leftmost_positions.add(coord)

    def velocity_to_right(self, velocity: Velocity) -> Velocity:
        direction = Direction(self.game_config.block_size)
        if velocity == direction.up:
            return direction.right
        elif velocity == direction.right:
            return direction.down
        elif velocity == direction.down:
            return direction.left
        else:
            return direction.up

    def velocity_to_left(self, velocity) -> Velocity:
        direction = Direction(self.game_config.block_size)
        if velocity == direction.up:
            return direction.left
        elif velocity == direction.right:
            return direction.up
        elif velocity == direction.down:
            return direction.right
        else:
            return direction.down

    def body_part_velocity(self, index: int, body_part: Coord):
        if index == 0:
            return self.velocity
        else:
            direction = Direction(self.game_config.block_size)
            next_part = self.body[index-1]
            if body_part.x == next_part.x:
                if body_part.y < next_part.y:
                    return direction.down
                else:
                    return direction.up
            else:
                if body_part.x < next_part.x:
                    return direction.right
                else:
                    return direction.left

    def rightmost_available_positions(self, available_positions: List[Coord]) -> List[Coord]:
        _pos = []
        for index, body_part in reversed(list(enumerate(self.body))):
            velocity = self.body_part_velocity(index, body_part)
            fixed_velocity = self.velocity_to_right(velocity)
            _pos.extend(self.available_positions_to_dir(body_part, fixed_velocity, available_positions))
        return _pos

    def leftmost_available_positions(self, available_positions: List[Coord]) -> List[Coord]:
        _pos = []
        for index, body_part in reversed(list(enumerate(self.body))):
            velocity = self.body_part_velocity(index, body_part)
            fixed_velocity = self.velocity_to_left(velocity)
            _pos.extend(self.available_positions_to_dir(body_part, fixed_velocity, available_positions))
        return _pos

    @staticmethod
    def available_positions_to_dir(start: Coord, velocity: Velocity, available_positions: List[Coord]) -> List[Coord]:
        positions = []
        current = start.translate(velocity)
        while current in available_positions:
            positions.append(current)
            current = current.translate(velocity)
        return positions

    def distance_to_food(self, food: Food):
        return pow(self.head.x - food.position.x, 2) + pow(self.head.y - food.position.y, 2)

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

    def _paint_block(self, coord: Coord, color: Color = None):
        if color is None:
            color = self.game_config.snake_color
        if self.game_config.show_game:
            pygame.draw.rect(self.screen, color,
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
