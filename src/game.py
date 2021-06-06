import pygame
from pygame import Surface
from pygame.time import Clock

from typing import Set

from src.configs import GameConfig, SnakeConfig
from src.exceptions import SnakeGameException
from src.food import Food
from src.shared import Velocity, Coord, Direction
from src.snake import Snake


def human_player_agent(event, block_size: int, current_velocity: Velocity) -> Velocity:
    directions = Direction(block_size)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            if current_velocity != directions.right:
                return directions.left
        elif event.key == pygame.K_RIGHT:
            if current_velocity != directions.left:
                return directions.right
        elif event.key == pygame.K_UP:
            if current_velocity != directions.down:
                return directions.up
        elif event.key == pygame.K_DOWN:
            if current_velocity != directions.up:
                return directions.down
    return current_velocity


class SnakeGame:
    score: int = 0
    current_episode: int = 1
    game_over: bool = False
    paused: bool = False

    # font_position: Coord = None
    _screen_coords: Set[Coord] = None

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
        if self._screen_coords is not None:
            return self._screen_coords
        else:
            self._screen_coords = set()
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

    def loop(self):
        while self.current_episode < self.game_config.number_of_episodes:
            # Repaint the whole screen
            self.screen.fill(self.game_config.background_color)
            self.snake = Snake(self.game_config, self.screen, self.snake_config)
            self.food = Food(self.game_config, self.screen, self.available_positions)
            pygame.display.update()

            # Initialize variables
            self.current_episode += 1
            self.game_over = False
            has_eaten = False
            try:
                while not self.game_over:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
                        if event.type == pygame.KEYDOWN:
                            if event.key == 112:  # letter p
                                self.paused = not self.paused

                        if self.paused:
                            break

                        old_velocity = self.snake.velocity
                        new_velocity = human_player_agent(event, self.game_config.block_size, self.snake.velocity)
                        self.snake.change_velocity(new_velocity)
                        if old_velocity != new_velocity:
                            # This is important because the pygame.event attribute is queue.
                            # If we "insert" more than one velocity change event in the queue per clock tick
                            # then all events will be processed and, even though the velocities reached a consistent
                            # state, there hasn't been enough time to go through the rest of the code and update the
                            # screen and snake body.
                            # You can try the error by removing this check, setting the speed to 1 and hitting down+left
                            # when the snake is going right. If you do both commands in a frame interval you are going
                            # to hit your own body and lose, even though we check for consistency in the agent.
                            break

                    if self.paused:
                        continue

                    self.snake.slither(has_eaten)

                    has_eaten = False
                    if self.food.can_be_eaten(self.snake.mouth):
                        self.food.eat(self.available_positions)
                        has_eaten = True
                    pygame.display.update()
                    self.clock.tick(self.snake_config.speed)
            except SnakeGameException as e:
                print(e)
