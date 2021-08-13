import random

import pygame
from pygame import Surface
from pygame.time import Clock

from typing import Set
from statistics import mean, pvariance

from src.agents.abstract_agent import AbstractAgent
from src.configs import GameConfig, SnakeConfig
from src.exceptions import QuitGame
from src.food import Food
from src.shared import Velocity, Coord, Direction, Colors, Action, map_action_to_keypress, ActionTakerPolicy, Problem
from src.snake import Snake
from src.state import State

pygame.init()


def velocity_interpreter(event, block_size: int, current_velocity: Velocity, snake_size_is_one: bool) -> Velocity:
    directions = Direction(block_size)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            if current_velocity != directions.right or snake_size_is_one:
                return directions.left
        elif event.key == pygame.K_RIGHT:
            if current_velocity != directions.left or snake_size_is_one:
                return directions.right
        elif event.key == pygame.K_UP:
            if current_velocity != directions.down or snake_size_is_one:
                return directions.up
        elif event.key == pygame.K_DOWN:
            if current_velocity != directions.up or snake_size_is_one:
                return directions.down
    return current_velocity


def food_based_action(food: Food, snake: Snake, state: State) -> Action:
    def food_choice() -> Set[Action]:
        choices = set()
        if state.food_right.value:
            choices.add(Action.RIGHT)
        if state.food_left.value:
            choices.add(Action.LEFT)
        if state.food_below.value:
            choices.add(Action.DOWN)
        if state.food_above.value:
            choices.add(Action.UP)
        return choices

    def danger_choice() -> Set[Action]:
        choices = set()
        if not state.danger_up.value:
            choices.add(Action.UP)
        if not state.danger_down.value:
            choices.add(Action.DOWN)
        if not state.danger_left.value:
            choices.add(Action.LEFT)
        if not state.danger_right.value:
            choices.add(Action.RIGHT)
        return choices

    def not_opposite_speed_choice() -> Set[Action]:
        choices = set()
        if not state.going_left.value or len(snake.body) == 1:
            choices.add(Action.RIGHT)
        if not state.going_right.value or len(snake.body) == 1:
            choices.add(Action.LEFT)
        if not state.going_up.value or len(snake.body) == 1:
            choices.add(Action.DOWN)
        if not state.going_down.value or len(snake.body) == 1:
            choices.add(Action.UP)
        return choices

    not_opposite_speed_choices = not_opposite_speed_choice()
    food_actions = food_choice()
    no_danger_actions = danger_choice()
    common = [*food_actions.intersection(no_danger_actions).intersection(not_opposite_speed_choices)]
    # printable_common = [e.value for e in common]
    # printable_not_op = [e.value for e in not_opposite_speed_choices]
    # printable_food = [e.value for e in food_actions]
    # printable_danger = [e.value for e in no_danger_actions]
    #
    # print(f"common: {printable_common}")
    # print(f"not op: {printable_not_op}")
    # print(f"food: {printable_food}")
    # print(f"no danger: {printable_danger}\n\n\n")

    if len(common) > 0:
        return random.choice(common)
    elif len(no_danger_actions) > 0:
        return random.choice([*no_danger_actions.intersection(not_opposite_speed_choices)])
    else:
        return random.choice([*not_opposite_speed_choices])


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
    best_score_episode: int = 0
    current_episode: int = 1
    paused: bool = False

    _scores = []
    _mean = []
    _variance = []
    _scores_episode = []

    # font_position: Coord = None
    _screen_coords: Set[Coord] = None

    clock: Clock = Clock()
    snake: Snake
    snake_config: SnakeConfig
    game_config: GameConfig
    screen: Surface
    food: Food
    state: State = State()
    agent: AbstractAgent

    too_dumb_counter = 0
    died_wall_hit_counter = 0
    died_body_hit_counter = 0

    dist = 0
    last_dist = 0

    human_turn: bool = False
    food_ai_turn: bool = False

    def __init__(self,
                 snake_config: SnakeConfig,
                 game_config: GameConfig,
                 agent: AbstractAgent
                 ):
        SnakeGame._validate_attributes(snake_config, game_config)
        self.snake_config = snake_config
        self.game_config = game_config
        self.agent = agent

        self.screen = pygame.display.set_mode((game_config.screen_height, game_config.screen_height))
        self.font_style = pygame.font.SysFont([], game_config.font_size)
        self.pause_font_style = pygame.font.SysFont([], game_config.font_size, True, True)

        if game_config.action_taker_policy == ActionTakerPolicy.MIXED_FOOD_AI:
            self.food_ai_turn = True

    def update_display(self):
        if self.game_config.show_game:
            pygame.display.update()

    @staticmethod
    def _validate_attributes(snake: SnakeConfig, game: GameConfig):
        # todo should raise errors if data is invalid
        return True

    def _show_text(self, text, color, coord: Coord, font=None):
        if font is None:
            font = self.font_style
        text_object = font.render(text, True, color)
        self.screen.blit(text_object, coord.to_array())
        self.update_display()
        self.food.paint()

    def _erase_text(self, text, coord: Coord, font=None):
        if font is None:
            font = self.font_style
        text_width, text_height = font.size(text)
        self.screen.fill(self.game_config.background_color, [coord.x, coord.y, text_width, text_height])
        self.food.paint()

    def show_score(self):
        text = f"Score: {self.food.score}"
        erase_text = f"Score: {int(self.food.score) - 1}"
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

            unpause_keys = [pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    # toggle action taker between ia agent and mixed
                    is_mixed = self.game_config.action_taker_policy == ActionTakerPolicy.MIXED
                    if is_mixed:
                        self.game_config.action_taker_policy = ActionTakerPolicy.AI_AGENT
                    else:
                        self.game_config.action_taker_policy = ActionTakerPolicy.MIXED

                elif event.key == pygame.K_KP_PLUS:
                    self.snake.config.speed += self.game_config.speed_delta
                    print(f"Current speed is {self.snake.config.speed}")

                elif event.key == pygame.K_KP_MINUS:
                    if self.snake.config.speed > 0:
                        if self.snake.config.speed < self.game_config.speed_delta:
                            self.snake.config.speed = 0
                        else:
                            self.snake.config.speed -= self.game_config.speed_delta
                    print(f"Current speed is {self.snake.config.speed}")

                elif event.key == pygame.K_s:
                    self.game_config.show_game = not self.game_config.show_game

                elif event.key == pygame.K_p:
                    # toggle pause
                    self.paused = not self.paused
                    self.toggle_pause_text()
                elif self.paused and event.key in unpause_keys and hasattr(event, "scancode"):
                    self.paused = False
                    self.toggle_pause_text()

                ###############################################################
                #    From this comment down, user commands will be ignored    #
                #                                                             #
                #    This means manual user input                             #
                elif hasattr(event, "scancode") and self.game_config.block_interactions:
                    print("Blocking human interaction")
                    continue
                ###############################################################

            if self.paused:
                # skip everything below this line. If the game is paused we don't want to change the snake's velocity
                break

            old_velocity = self.snake.velocity
            new_velocity = velocity_interpreter(event, self.game_config.block_size, self.snake.velocity,
                                                len(self.snake.body) == 1)
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

    def build_dump_object_info(self):
        agent_results = self.agent.state_action_values
        return {
            "header": {
                "game_config": self.game_config.__dict__,
                "snake_config": self.snake_config.__dict__,
                "state_meaning": self.state.dict(),
                "statistics": {
                    "best_score": self.best_score,
                    "best_score_episode": self.best_score_episode,
                    "dumb_snake": self.too_dumb_counter,
                    "died_wall": self.died_wall_hit_counter,
                    "died_body": self.died_body_hit_counter,
                    "agent": self.agent.dict()
                }
            },
            "agent_rehearsal": agent_results
        }

    def loop(self):
        while self.current_episode < self.game_config.number_of_episodes:
            # Repaint the whole screen
            self.screen.fill(self.game_config.background_color)
            self.snake = Snake(self.game_config, self.screen, self.snake_config, list(self.screen_coords_list))
            self.food = Food(self.game_config, self.screen, self.available_positions)
            self.update_display()

            # Initialize variables
            self.current_episode += 1
            has_eaten = False
            try:
                # Running an episode
                missed_food_times = 0
                self.state.populate(self.snake, self.food.position, self.game_config).set_state()
                while True:
                    if self.paused:
                        # process events one more time so we can listen for 'p' key
                        self.process_events()
                        self.clock.tick(self.snake_config.speed)
                        continue

                    if self.food_ai_turn:
                        action = food_based_action(self.food, self.snake, self.state)
                        self.agent.init_state_if_needed(self.state.value)
                        agent_action_info = self.agent.get_action_info(self.state.value, action)
                        self.agent.set_last_action_info(self.state.value, agent_action_info)
                    else:
                        # choose action from agent
                        action = self.agent.choose_action(self.state.value).action

                    # Put event in the queue
                    put_keypress_event(pygame.event, action)

                    # process events (there might be others besides snake velocity changes)
                    self.process_events()

                    # make the snake slither and catch the problems encountered
                    problem: Problem = self.snake.slither(has_eaten)

                    # helper flag to decide whether to pop or not pop the tail
                    has_eaten = False

                    # calculate reward
                    if problem == Problem.BODY_HIT:
                        reward = self.game_config.punishment
                    elif problem == Problem.WALL_HIT:
                        reward = self.game_config.punishment
                    elif missed_food_times > self.game_config.missed_food_max_steps:
                        problem = Problem.TOO_DUMB
                        reward = self.game_config.punishment
                    elif self.food.can_be_eaten(self.snake.head):
                        self.food.eat(self.available_positions)
                        has_eaten = True
                        self.show_score()
                        missed_food_times = 0
                        reward = self.game_config.food_reward
                    else:
                        missed_food_times += 1
                        self.dist = self.snake.distance_to_food(self.food)
                        reward = (self.last_dist - self.dist) * 0.0000001
                        # print(f"last {self.last_dist}; current {self.dist}; reward {reward}")
                        # print(reward)
                        self.last_dist = self.dist
                        # reward = self.game_config.default_reward

                    # save the reward history. some agents might use this info
                    self.agent.save_to_history(self.state.value, action, reward)

                    # populate new state
                    self.state.populate(self.snake, self.food.position, self.game_config).set_state()

                    # The agent might need to make a step reinforcement
                    self.agent.step_reinforcement(reward, self.state.value)

                    self.update_display()

                    # now, check for problems
                    if problem is not None:
                        msg = ""
                        if problem == Problem.WALL_HIT:
                            self.died_wall_hit_counter += 1
                            msg = f"The snake died from wall hit at coords ({self.snake.head.x},{self.snake.head.y})"
                        elif problem == Problem.BODY_HIT:
                            self.died_body_hit_counter += 1
                            msg = f"The snake died from body hit at coords ({self.snake.head.x},{self.snake.head.y})"
                        elif problem == Problem.TOO_DUMB:
                            self.too_dumb_counter += 1
                            msg = "The snake didn't know what to do.."
                        elif problem == Problem.QUIT:
                            print('Exiting..')
                            return self.build_dump_object_info(), self._scores_episode, self._scores, self._mean, self._variance

                        print(msg)
                        # if there's a problem, we should end this episode
                        break

                    self.clock.tick(self.snake_config.speed)

            except QuitGame:
                print('Exiting..')
                return self.build_dump_object_info(), self._scores_episode, self._scores, self._mean, self._variance

            if self.game_config.action_taker_policy == ActionTakerPolicy.MIXED_FOOD_AI:
                if self.current_episode > self.game_config.change_agent_episode:
                    self.food_ai_turn = False

            # End of episode!!
            print(f"Episode {self.current_episode}/{self.game_config.number_of_episodes}. "
                  f"Score was {self.food.score}. Best score is {self.best_score} made in episode "
                  f"{self.best_score_episode}.\n"
                  f"There are {self.agent.state_amount} states registered.\n"
                  f"The snake was lost {self.too_dumb_counter} times.\n"
                  f"The snake died from wall hit {self.died_wall_hit_counter} times.\n"
                  f"The snake died from body hit {self.died_body_hit_counter} times.\n", )

            self.agent.episode_reinforcement()

            has_best_score = int(self.food.score) > self.best_score
            if has_best_score:
                self.best_score = int(self.food.score)
                self.best_score_episode = self.current_episode

            # if self.current_episode % 10 == 0 or has_best_score:
            self._scores.append(int(self.food.score))
            _current_mean = mean(self._scores)
            self._mean.append(_current_mean)
            self._variance.append(pvariance(self._scores, _current_mean))
            self._scores_episode.append(self.current_episode)

        # End of experiment!!
        print(f"End of experiment.\n"
              f"Best score was {self.best_score}\n")

        return self.build_dump_object_info(), self._scores_episode, self._scores, self._mean, self._variance
