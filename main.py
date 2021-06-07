from src.agent import MonteCarloAgent
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors, ActionTakerPolicy
from time import time
import math

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
        head_color=Colors.HEAD.value,
        block_size=20,
        number_of_episodes=1000,
        block_interactions=False,
        missed_food_max_steps=1500,
        action_taker_policy=ActionTakerPolicy.AI_AGENT,
        default_reward=0.5,
        food_reward=100,
        punishment=-100
    )

    _snake_config = SnakeConfig(
        speed=40,
        initial_length=1
    )

    _agent = MonteCarloAgent(
        every_visit=False,
        gamma=0.2,
        epsilon_step_increment=0.2
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
