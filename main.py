import matplotlib.pyplot as plt
from pathlib import Path
from src.agents.monte_carlo import MonteCarloAgent
from src.agents.q_learning import QLearning
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors, ActionTakerPolicy
from time import time
import math
import json
from os import system, name


def dump_results_to_file(result, x, y):
    timestamp = math.floor(time())
    folder = f"results/result_{timestamp}_score_{result['header']['statistics']['best_score']}"
    Path(folder).mkdir(parents=True, exist_ok=True)

    print(f"Dumping results to directory {folder}")
    with open(f"{folder}/info.json", "w") as fp:
        json.dump(result, fp, sort_keys=True, indent=4)

    plt.scatter(x, y)
    plt.xlabel('episode')
    plt.ylabel('score')
    plt.savefig(f"{folder}/graph.png")


def plot_results(x, y):
    plt.scatter(x, y)
    plt.xlabel('episode')
    plt.ylabel('score')
    plt.show()


def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


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
        action_taker_policy=ActionTakerPolicy.AI_AGENT,
        default_reward=0,
        food_reward=10,
        punishment=-10,
        show_game=False,
        speed_delta=10,
        run_for_n_minutes=20,
        change_agent_episode=200
    )

    _snake_config = SnakeConfig(
        speed=0,
        random_initial_pos=True,
        initial_length=1
    )

    monte_carlo_agent = MonteCarloAgent(
        every_visit=True,
        gamma=0.5,
        epsilon_step_increment=0.1,
        initial_epsilon=1,
        use_individual_policies=True,
        learning_incentive=False,
        reverse_history=True
    )

    q_learning_agent = QLearning(
        gamma=0.5,
        epsilon_step_increment=0.1,
        initial_epsilon=1,
        learning_incentive=False,
        use_individual_policies=False,
        alpha=0.01
    )

    clear()
    option = int(input("""
    Escolha sua opção de agente:
     1) Monte Carlo
     2) Q-Learning
    """))

    if option == 1:
        agent = monte_carlo_agent
    else:
        agent = q_learning_agent

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config,
        agent=agent
    )

    start = time()
    # Run the game
    result, x, y = _game.loop()
    end = time()

    _time = math.floor(end-start)
    if isinstance(result, dict):
        result["header"]["statistics"]["seconds"] = _time
        dump_results_to_file(result, x, y)
        plot_results(x, y)
    print(f"\nElapsed time: {_time} seconds")


if __name__ == '__main__':
    run()
