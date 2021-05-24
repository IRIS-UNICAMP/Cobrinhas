from dataclasses import dataclass, field
from enum import Enum
import random

import pygame
from pygame import Surface
from pygame.time import Clock

from typing import Set, List, Tuple


class HitWall(Exception):
    pass


Color = Tuple[int, int, int]


class Colors(Enum):
    BLUE = (67, 59, 103)
    RED = (200, 112, 126)
    SWALLOW_GREEN = (0, 71, 48)


@dataclass(frozen=True)
class Velocity:
    x: int
    y: int


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
    swallow_color: Color
    block_size: int
    number_of_episodes: int


@dataclass(frozen=True)
class SnakeConfig:
    initial_position: Coord
    speed: int
    initial_length: int = field(default=1)


class Snake:
    _velocity: Velocity = field(default=None)
    _body: List[Coord] = field(default_factory=set)

    def __init__(self, game_config: GameConfig, screen: Surface, config: SnakeConfig):
        self.game_config = game_config
        self.screen = screen
        self.config = config

        self._initialize_body()

    @property
    def mouth(self) -> Coord:
        return self._body[0]

    @property
    def body(self):
        return self._body

    def change_velocity(self, velocity: Velocity):
        self._velocity = velocity

    def can_slither(self) -> bool:
        new_head = self._body[0].translate(self._velocity)
        return not (new_head.x < 0 or new_head.x >= self.game_config.screen_width
                    or new_head.y < 0 or new_head.y >= self.game_config.screen_height)

    def slither(self, has_eaten: bool):
        head = self._body[0].translate(self._velocity)
        # print(f"Slithering head to ({head.x},{head.y})")
        if not self.can_slither():
            raise HitWall(f"The snake hit the wall at the coordinates {{x: {head.x}, y: {head.y}}}")
        self._body.insert(0, head)
        if not has_eaten:
            tail = self._body.pop()
            self._erase_block(tail)

        self._paint_block(head)

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
        # Creating a linearized version of the screen of the size of the snake
        linearized_vector = self._snaky_linearized_screen(max_length=self.config.initial_length)
        linearized_vector.reverse()
        self._body = linearized_vector
        self._set_default_velocity()
        self._paint()

    def _paint_block(self, coord: Coord):
        pygame.draw.rect(self.screen, self.game_config.snake_color,
                         [coord.x, coord.y, self.game_config.block_size, self.game_config.block_size])

    def _erase_block(self, coord: Coord):
        pygame.draw.rect(self.screen, self.game_config.background_color,
                         [coord.x, coord.y, self.game_config.block_size, self.game_config.block_size])

    def _paint(self):
        for x in self._body:
            self._paint_block(x)


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


def human_player_agent(event, block_size) -> Velocity:
    directions = Direction(block_size)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            return directions.left
        elif event.key == pygame.K_RIGHT:
            return directions.right
        elif event.key == pygame.K_UP:
            return directions.up
        elif event.key == pygame.K_DOWN:
            return directions.down


class SnakeGame:
    score: int = 0
    current_episode: int = 1
    game_over: bool = False

    # font_position: Coord = None
    _screen_coords: Set[Coord] = set()

    clock: Clock = Clock()
    snake: Snake
    snake_config: SnakeConfig
    game_config: GameConfig
    screen: Surface
    food: Food

    @staticmethod
    def _validate_attributes(snake: SnakeConfig, game: GameConfig):
        # todo should raise errors if data is invalid
        return True

    @property
    def screen_coords(self):
        if len(self._screen_coords) > 0:
            return self._screen_coords
        else:
            for x in range(0, self.game_config.screen_width, self.game_config.block_size):
                for y in range(0, self.game_config.screen_height, self.game_config.block_size):
                    self._screen_coords.add(Coord(x, y))
            return self._screen_coords

    @property
    def available_positions(self):
        return self.screen_coords - set(self.snake.body)

    def __init__(self,
                 snake_config: SnakeConfig,
                 game_config: GameConfig
                 ):
        SnakeGame._validate_attributes(snake_config, game_config)
        self.snake_config = snake_config
        self.game_config = game_config

        self.screen = pygame.display.set_mode((game_config.screen_height, game_config.screen_height))
        # self.font_style = pygame.font.SysFont([], game_config.font_size)

        self.snake = Snake(game_config, self.screen, snake_config)

    def loop(self):
        self.screen.fill(self.game_config.background_color)
        self.food = Food(self.game_config, self.screen, self.available_positions)
        pygame.display.update()
        while self.current_episode < self.game_config.number_of_episodes:
            self.current_episode += 1
            self.game_over = False
            has_eaten = False
            try:
                while not self.game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        new_velocity = human_player_agent(event, self.game_config.block_size)
                        if new_velocity is not None:
                            self.snake.change_velocity(new_velocity)

                    self.snake.slither(has_eaten)

                    has_eaten = False
                    if self.food.can_be_eaten(self.snake.mouth):
                        self.food.eat(self.available_positions)
                        has_eaten = True

                    pygame.display.update()
                    self.clock.tick(self.snake_config.speed)
            except HitWall as e:
                print(e)



if __name__ == '__main__':
    _game_config = GameConfig(
        screen_height=600,
        screen_width=600,
        snake_color=Colors.RED.value,
        background_color=Colors.BLUE.value,
        food_color=Colors.RED.value,
        font_size=50,
        font_color=Colors.RED.value,
        swallow_color=Colors.SWALLOW_GREEN.value,
        block_size=20,
        number_of_episodes=5
    )

    _snake_config = SnakeConfig(
        initial_position=Coord(0, 0),
        speed=15,
        initial_length=2
    )

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config
    )

    # Run the game
    _game.loop()
