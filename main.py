from src.agents.monte_carlo import MonteCarloAgent
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
        number_of_episodes=100000,
        block_interactions=False,
        missed_food_max_steps=1000,
        action_taker_policy=ActionTakerPolicy.MIXED_FOOD_AI,
        default_reward=0.01,
        food_reward=10,
        punishment=-20,
        show_game=False,
        speed_delta=10,
        run_for_n_minutes=40,
        change_agent_episode=500,
        body_hit_punishment=-20
    )

    _snake_config = SnakeConfig(
        speed=0,
        random_initial_pos=True,
        initial_length=1
    )

    _agent = MonteCarloAgent(
        every_visit=False,
        gamma=1.01,
        epsilon_step_increment=0.01,
        initial_epsilon=1,
        use_individual_policies=True,
        learning_incentive=False,
        reverse_history=False
    )

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config,
        agent=_agent
    )

    start = time()
    # Run the game
    result = _game.loop()
    end = time()

    _time = math.floor(end-start)
    if isinstance(result, dict):
        result["header"]["statistics"]["seconds"] = _time
        dump_results_to_file(result)
    print(f"\nElapsed time: {_time} seconds")


if __name__ == '__main__':
    run()