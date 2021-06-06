from dataclasses import dataclass, field

from src.shared import Color


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class SnakeConfig:
    speed: int
    initial_length: int = field(default=1)
