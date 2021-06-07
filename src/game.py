import random

import pygame
from pygame import Surface
from pygame.time import Clock

from typing import Set

from src.agent import MonteCarloAgent
from src.configs import GameConfig, SnakeConfig
from src.exceptions import SnakeGameException, QuitGame, TooDumb
from src.food import Food
from src.shared import Velocity, Coord, Direction, Colors, Action, map_action_to_keypress, ActionTakerPolicy
from src.snake import Snake
from src.state import State

pygame.init()


def velocity_interpreter(event, block_size: int, current_velocity: Velocity) -> Velocity:
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


def put_random_dir(queue):
    rand_key = random.choice([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN])
    new_event = pygame.event.Event(pygame.KEYDOWN, unicode='', key=rand_key, mod=pygame.KMOD_NONE)

    # For some reason we have to repost every event in the queue when we pause the game
    events = queue.get()
    for e in events:
        queue.post(e)
    queue.post(new_event)


def put_keypress_event(queue, action: Action):
    key = map_action_to_keypress(action)
    new_event = pygame.event.Event(pygame.KEYDOWN, unicode='', key=key, mod=pygame.KMOD_NONE)
    # For some reason we have to repost every event in the queue when we pause the game
    events = queue.get()
    for e in events:
        queue.post(e)
    queue.post(new_event)


class SnakeGame:
    best_score: int = 0
    current_episode: int = 1
    paused: bool = False

    # font_position: Coord = None
    _screen_coords: Set[Coord] = None

    clock: Clock = Clock()
    snake: Snake
    snake_config: SnakeConfig
    game_config: GameConfig
    screen: Surface
    food: Food
    state: State = State()
    agent: MonteCarloAgent
    default_reward: int = 1
    food_reward: int = 5
    punishment: int = -10

    too_dumb_counter = 0
    died_counter = 0

    human_turn: bool = False

    def __init__(self,
                 snake_config: SnakeConfig,
                 game_config: GameConfig,
                 agent: MonteCarloAgent
                 ):
        SnakeGame._validate_attributes(snake_config, game_config)
        self.snake_config = snake_config
        self.game_config = game_config
        self.agent = agent

        self.screen = pygame.display.set_mode((game_config.screen_height, game_config.screen_height))
        self.font_style = pygame.font.SysFont([], game_config.font_size)
        self.pause_font_style = pygame.font.SysFont([], game_config.font_size, True, True)

    @staticmethod
    def _validate_attributes(snake: SnakeConfig, game: GameConfig):
        # todo should raise errors if data is invalid
        return True

    def _show_text(self, text, color, coord: Coord, font=None):
        if font is None:
            font = self.font_style
        text_object = font.render(text, True, color)
        self.screen.blit(text_object, coord.to_array())
        pygame.display.update()
        self.food.paint()

    def _erase_text(self, text, coord: Coord, font=None):
        if font is None:
            font = self.font_style
        text_width, text_height = font.size(text)
        self.screen.fill(self.game_config.background_color, [coord.x, coord.y, text_width, text_height])
        self.food.paint()

    def show_score(self):
        text = f"Score: {self.food.score}"
        erase_text = f"Score: {int(self.food.score)-1}"
        self._erase_text(erase_text, self.start_coords)
        self._show_text(text, Colors.LAVENDER_BLUSH.value, self.start_coords)

    def toggle_pause_text(self):
        text = "Paused"
        text_width, _ = self.pause_font_style.size(text)
        text_coords = Coord(self.top_right.x - text_width, self.top_right.y)
        if self.paused:
            self._show_text(text, Colors.GOLD.value, text_coords, self.pause_font_style)
        else:
            self._erase_text(text, text_coords, self.pause_font_style)

    @property
    def screen_coords_list(self):
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
        return self.screen_coords_list - set(self.snake.body)

    @property
    def center_coords(self) -> Coord:
        return Coord(self.game_config.screen_width // 2 - 50, self.game_config.screen_height // 2 - 100)

    @property
    def start_coords(self) -> Coord:
        return Coord(0, 0)

    @property
    def top_right(self):
        return Coord(self.game_config.screen_width, 0)

    def process_events(self):
        # Here we process the generated events by the agent and analyze the results
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise QuitGame()

            # This means manual user input
            if hasattr(event, "scancode") and self.game_config.block_interactions:
                print("Blocking human interaction")
                continue

            unpause_keys = [pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    # toggle action taker between ia agent and mixed
                    is_mixed = self.game_config.action_taker_policy == ActionTakerPolicy.MIXED
                    if is_mixed:
                        self.game_config.action_taker_policy = ActionTakerPolicy.AI_AGENT
                    else:
                        self.game_config.action_taker_policy = ActionTakerPolicy.MIXED

                if event.key == pygame.K_p:
                    # toggle pause
                    self.paused = not self.paused
                if self.paused and event.key in unpause_keys:
                    self.paused = False

                self.toggle_pause_text()

            if self.paused:
                break

            old_velocity = self.snake.velocity
            new_velocity = velocity_interpreter(event, self.game_config.block_size, self.snake.velocity)
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

    def loop(self):
        while self.current_episode < self.game_config.number_of_episodes:
            # Repaint the whole screen
            self.screen.fill(self.game_config.background_color)
            self.snake = Snake(self.game_config, self.screen, self.snake_config)
            self.food = Food(self.game_config, self.screen, self.available_positions)
            pygame.display.update()

            # Initialize variables
            self.current_episode += 1
            has_eaten = False
            action: Action = Action.UP  # Random action for initialization
            try:
                # Running an episode
                missed_food_times = 0
                while True:
                    # Here we define the state and take the best action
                    self.state.populate(self.snake, self.food.position, self.game_config).set_state()
                    # print(self.state)
                    # put_random_dir(pygame.event)

                    # Choosing the best action given the current state
                    # and putting the keypress event in the queue
                    if not self.human_turn:
                        action = self.agent.choose_action(self.state.value)
                        put_keypress_event(pygame.event, action)
                    else:
                        self.agent.init_state_if_needed(self.state.value)

                    # Process the current events in the queue
                    self.process_events()

                    if self.paused:
                        self.clock.tick(self.snake_config.speed)
                        continue

                    self.snake.slither(has_eaten)

                    # This will tell the snake printer function to not
                    # erase it's tail if a food has been eaten. this way you will gain size
                    has_eaten = False
                    if self.food.can_be_eaten(self.snake.head):
                        self.food.eat(self.available_positions)
                        has_eaten = True
                        self.show_score()
                        self.agent.save_to_history(self.state.value, action, self.food_reward)
                        missed_food_times = 0
                    else:
                        self.agent.save_to_history(self.state.value, action, self.default_reward)
                        missed_food_times += 1

                    if missed_food_times > self.game_config.missed_food_max_steps:
                        raise TooDumb()

                    pygame.display.update()
                    self.clock.tick(self.snake_config.speed)
            except SnakeGameException as e:
                print('\n\n')
                print(e)
                self.died_counter += 1
                self.agent.save_to_history(self.state.value, action, self.punishment)
            except TooDumb as e:
                print('\n\n')
                print(e)
                self.too_dumb_counter += 1
                self.agent.save_to_history(self.state.value, action, self.punishment)
            except QuitGame:
                print('Exiting..')
                return

            if self.game_config.action_taker_policy == ActionTakerPolicy.AI_AGENT:
                self.human_turn = False
            elif self.game_config.action_taker_policy == ActionTakerPolicy.HUMAN:
                self.human_turn = True
            else:
                self.human_turn = not self.human_turn
                self.paused = True
                self.toggle_pause_text()

            # End of episode!!
            print(f"Reinforcing episode {self.current_episode}/{self.game_config.number_of_episodes}. "
                  f"Score was {self.food.score}. Best score is {self.best_score}.\n"
                  f"There are {self.agent.state_amount} states registered out of {2**9} possible ones.\n"
                  f"The snake didn't know what to do {self.too_dumb_counter} times and died {self.died_counter} times.")
            self.agent.episode_reinforcement()
            if int(self.food.score) > self.best_score:
                self.best_score = int(self.food.score)

        # End of experiment!!
        print(f"End of experiment.\n"
              f"Best score was {self.best_score}\n"
              f"Epsilon was {self.agent.policy.epsilon}")
        self.agent.dump_results_to_file()
