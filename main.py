from src.agent import MonteCarloAgent
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors, ActionTakerPolicy
from time import time
import math

if __name__ == '__main__':
    _game_config = GameConfig(
        screen_height=440,
        screen_width=440,
        snake_color=Colors.RED.value,
        background_color=Colors.BLUE.value,
        food_color=Colors.RED.value,
        font_size=50,
        font_color=Colors.RED.value,
        swallow_color=Colors.SWALLOW_GREEN.value,
        head_color=Colors.HEAD.value,
        block_size=20,
        number_of_episodes=50000,
        block_interactions=False,
        missed_food_max_steps=1000,
        action_taker_policy=ActionTakerPolicy.AI_AGENT,
        default_reward=1,
        food_reward=10,
        punishment=-10,
        show_game=True,
        speed_delta=10
    )

    _snake_config = SnakeConfig(
        speed=20,
        initial_length=1
    )

    _agent = MonteCarloAgent(
        every_visit=True,
        gamma=0.5,
        epsilon_step_increment=0.9
    )

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config,
        agent=_agent
    )

    start = time()
    # Run the game
    _game.loop()
    end = time()
    print(f"\nElapsed time: {math.floor(end-start)} seconds")
