from src.agent import MonteCarloAgent
from src.configs import GameConfig, SnakeConfig
from src.game import SnakeGame
from src.shared import Colors

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
        number_of_episodes=10000,
        block_interactions=False,
        missed_food_max_steps=150
    )

    _snake_config = SnakeConfig(
        speed=20,
        initial_length=1
    )

    _agent = MonteCarloAgent()

    _game = SnakeGame(
        snake_config=_snake_config,
        game_config=_game_config,
        agent=_agent
    )

    # Run the game
    _game.loop()
