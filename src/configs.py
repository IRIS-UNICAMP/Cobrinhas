from dataclasses import dataclass, field

from src.shared import Color, ActionTakerPolicy


@dataclass()
class GameConfig:
    screen_height: int
    screen_width: int
    snake_color: Color
    background_color: Color
    food_color: Color
    font_size: int
    font_color: Color
    swallow_color: Color
    head_color: Color
    block_size: int
    number_of_episodes: int
    block_interactions: bool
    missed_food_max_steps: int
    action_taker_policy: ActionTakerPolicy
    default_reward: float
    food_reward: int
    punishment: int
    show_game: bool
    speed_delta: int
    run_for_n_minutes: int


@dataclass()
class SnakeConfig:
    speed: int
    initial_length: int = field(default=1)
