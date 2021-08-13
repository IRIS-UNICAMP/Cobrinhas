import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from pathlib import Path

from src.agents.abstract_agent import AbstractAgent
from src.agents.monte_carlo import MonteCarloAgent
from src.agents.q_learning import QLearning
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors, ActionTakerPolicy
from time import time
import math
import json
from os import system, name


def dump_results_to_file(result, episodes, scores, mean, variance, option, agent: AbstractAgent,
                         game_config: GameConfig):
    timestamp = math.floor(time())
    folder = f"results/result_{timestamp}_score_{result['header']['statistics']['best_score']}"
    Path(folder).mkdir(parents=True, exist_ok=True)

    print(f"Dumping results to directory {folder}")
    with open(f"{folder}/info.json", "w") as fp:
        json.dump(result, fp, sort_keys=True, indent=4)

    with open(f"{folder}/mean_variance.json", "w") as fp:
        data = {
            "mean": mean,
            "variance": variance
        }
        json.dump(data, fp, sort_keys=True, indent=4)

    action_policy_is_mixed_food_ai = game_config.action_taker_policy == ActionTakerPolicy.MIXED_FOOD_AI
    labels = agent.plottable_configs()
    labels.extend(
        [
            f"food_reward={game_config.food_reward}",
            f"punishment={game_config.punishment}",
            f"action_taker_policy={game_config.action_taker_policy.name}",
            f"change_agent_episode={game_config.change_agent_episode if action_policy_is_mixed_food_ai else 'NA'}",
        ]
    )

    # create a list with two empty handles (or more if needed)
    handles = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white",
                                     lw=0, alpha=0)] * len(labels)

    title = "Monte Carlo" if option == 1 else "Q Learning"

    plt.suptitle(title)
    plt.subplot(1, 2, 1)
    plt.scatter(episodes, scores)
    plt.xlabel('episode')
    plt.ylabel('score')
    plt.legend(handles, labels, loc='best', fontsize='small',
               fancybox=True, framealpha=0.7,
               handlelength=0, handletextpad=0)

    plt.subplot(1, 2, 2)
    plt.scatter(episodes, mean, color="b", label="Mean")
    plt.scatter(episodes, variance, color="r", label="Variance")
    plt.legend()

    plt.savefig(f"{folder}/scores.png")
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
        number_of_episodes=27000,
        block_interactions=False,
        missed_food_max_steps=1000,
        action_taker_policy=ActionTakerPolicy.AI_AGENT,
        default_reward=0,
        food_reward=10,
        punishment=-10,
        show_game=False,
        speed_delta=10,
        change_agent_episode=200,
        paint_sideways=False,
        pause_when_dead=False,
        pause_when_danger=False
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
Digite o número: """))

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
    result, episodes, scores, mean, variance = _game.loop()
    end = time()

    _time = math.floor(end - start)
    if isinstance(result, dict):
        result["header"]["statistics"]["seconds"] = _time
        dump_results_to_file(result, episodes, scores, mean, variance, option, agent, _game_config)
    print(f"\nElapsed time: {_time} seconds")


if __name__ == '__main__':
    run()
