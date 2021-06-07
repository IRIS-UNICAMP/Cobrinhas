from src.agent import MonteCarloAgent
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors, ActionTakerPolicy
from time import time
import math
import json


def dump_results_to_file(result):
    timestamp = math.floor(time())
    path = f"result_{timestamp}_score_{result['header']['statistics']['best_score']}.json"
    print(f"Dumping results to file {path}")
    with open(path, "w") as fp:
        json.dump(result, fp, sort_keys=True, indent=4)


def run():
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
        number_of_episodes=40000,
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
        speed=0,
        initial_length=1
    )

    _agent = MonteCarloAgent(
        every_visit=True,
        gamma=0.2,
        epsilon_step_increment=1
    )

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config,
        agent=_agent
    )

    start = time()
    # Run the game
    result = _game.loop()
    if isinstance(result, dict):
        dump_results_to_file(result)
    end = time()
    print(f"\nElapsed time: {math.floor(end - start)} seconds")


if __name__ == '__main__':
    run()
