from dataclasses import dataclass, field
from enum import Enum
import random

import pygame
from pygame import Surface
from pygame.time import Clock

from typing import Set, List


class HitWall(Exception):
    pass


@dataclass(frozen=True)
class Velocity:
    x: int
    y: int


class Color(Enum):
    BLUE = (67, 59, 103)
    RED = (200, 112, 126)


class Direction:
    def __init__(self, block_size):
        self.up = Velocity(0, -block_size)
        self.down = Velocity(0, block_size)
        self.left = Velocity(-block_size, 0)
        self.right = Velocity(block_size, 0)


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def translate(self, velocity: Velocity):
        return Coord(self.x + velocity.x, self.y + velocity.y)


@dataclass(frozen=True)
class GameConfig:
    screen_height: int
    screen_width: int
    snake_color: Color
    background_color: Color
    food_color: Color
    font_size: int
    font_color: Color
    block_size: int
    number_of_episodes: int


@dataclass(frozen=True)
class SnakeConfig:
    initial_position: Coord
    speed: int
    initial_length: int = field(default=1)


class Snake:
    velocity: Velocity = field(default=None)
    body: List[Coord] = field(default_factory=set)

    def __init__(self, game: GameConfig, screen: Surface, config: SnakeConfig):
        self.game = game
        self.screen = screen
        self.config = config

        self.initialize_body()

    def snaky_linearized_screen(self, max_length=-1) -> List[Coord]:
        """
            This function takes the screen coordinates and block size and returns a linearized
            array of the screen in a "snaky" manner. That is, a linearized 2d-array that follows
            the "zig-zag" of the snake through the screen.
        """
        linearized_vector: List[Coord] = []

        for y in range(0, self.game.screen_height, self.game.block_size):
            for x in range(0, self.game.screen_width, self.game.block_size):
                if (y // self.game.block_size) % 2 == 0:
                    linearized_vector.append(Coord(x, y))
                else:
                    if x != 0:
                        linearized_vector.append(Coord(self.game.screen_width - x, y))
                    if self.game.screen_width - x == self.game.block_size:
                        # It's the last iteration, we have to insert one more, otherwise y will be increased
                        # before we can repeat the x coordinate
                        linearized_vector.append(Coord(0, y))

                if len(linearized_vector) == max_length:
                    return linearized_vector

        return linearized_vector

    def initialize_body(self):
        # Creating a linearized version of the screen of the size of the snake
        linearized_vector = self.snaky_linearized_screen(max_length=self.config.initial_length)
        linearized_vector.reverse()
        self.body = linearized_vector

    def can_slither(self) -> bool:
        new_head = self.body[0].translate(self.velocity)
        return new_head.x < 0 or new_head.x >= self.game.screen_width \
               or new_head.y < 0 or new_head.y >= self.game.screen_height

    def slither(self):
        new_head = self.body[0].translate(self.velocity)
        if not self.can_slither():
            raise HitWall(f"The snake hit the wall at the coordinates {{x: {new_head.x}, y: {new_head.y}}}")
        self.body.insert(0, new_head)
        self.body.pop()

    def _paint_block(self, coord: Coord):
        pygame.draw.rect(self.screen, self.game.snake_color,
                         [coord.x, coord.y, self.game.block_size, self.game.block_size])

    def _erase_block(self, coord: Coord):
        pygame.draw.rect(self.screen, self.game.background_color,
                         [coord.x, coord.y, self.game.block_size, self.game.block_size])


class Food:
    position: Coord

    def __init__(self, game: GameConfig, screen: Surface, available_positions: Set[Coord]):
        self.game = game
        self.screen = screen

        # Initializing food position
        self.position = random.choice(list(available_positions))

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
        pygame.draw.rect(self.screen, self.game.background_color,
                         [self.position.x, self.position.y, self.game.block_size, self.game.block_size])

    def _paint(self):
        pygame.draw.rect(self.screen, self.game.food_color,
                         [self.position.x, self.position.y, self.game.block_size, self.game.block_size])


class SnakeGame:
    score: int = 0
    current_episode: int = 1
    game_over: bool = False

    font_position: Coord
    screen_coords: Set[Coord]

    clock: Clock = Clock()
    snake: Snake
    snake_config: SnakeConfig
    game: GameConfig
    screen: Surface
    food: Food

    @staticmethod
    def _validate_attributes(snake: SnakeConfig, game: GameConfig):
        # todo should raise errors if data is invalid
        return True

    def initialize_screen_coords(self):
        for x in range(0, self.game.screen_width, self.game.block_size):
            for y in range(0, self.game.screen_height, self.game.block_size):
                self.screen_coords.add(Coord(x, y))

    @property
    def available_positions(self):
        return self.screen_coords - self.snake.body

    def __init__(self,
                 snake_config: SnakeConfig,
                 game: GameConfig
                 ):
        SnakeGame._validate_attributes(snake_config, game)
        self.snake_config = snake_config
        self.game = game

        self.screen = pygame.display.set_mode((game.screen_height, game.screen_height))
        self.font_style = pygame.font.SysFont([], game.font_size)

        self.initialize_screen_coords()

        self.food = Food(game, self.screen, self.available_positions)

        # Run the game
        self.loop()

    def loop(self):
        while self.current_episode < self.game.number_of_episodes:
            self.game.number_of_episodes += 1


if __name__ == '__main__':
    game_config = GameConfig(
        screen_height=100,
        screen_width=100,
        snake_color=Color.RED,
        background_color=Color.BLUE,
        food_color=Color.RED,
        font_size=50,
        font_color=Color.RED,
        block_size=20,
        number_of_episodes=5
    )

    snake_config = SnakeConfig(Coord(0, 0), 15, 20)

    snake = Snake(game_config, pygame.display.set_mode(), snake_config)

    print(snake.snaky_linearized_screen())
