from dataclasses import dataclass
from typing import List

from src.configs import GameConfig
from src.shared import Coord
from src.snake import Snake


@dataclass()
class StateInfo:
    value: bool
    name: str

    def __str__(self):
        return str(int(self.value))


@dataclass
class SnakeSize(StateInfo):
    def __str__(self):
        return f"_{self.value}"


def build_state_str(values: List[StateInfo]):
    state = ''
    for v in values:
        state += str(v)
    return state


class State:
    _state: str
    _state_values: List[StateInfo]

    food_right: StateInfo = StateInfo(False, "food_right")
    food_left: StateInfo = StateInfo(False, "food_left")
    food_below: StateInfo = StateInfo(False, "food_below")
    food_above: StateInfo = StateInfo(False, "food_above")
    going_left: StateInfo = StateInfo(False, "going_left")
    going_right: StateInfo = StateInfo(False, "going_right")
    going_down: StateInfo = StateInfo(False, "going_down")
    going_up: StateInfo = StateInfo(False, "going_up")
    wall_left: StateInfo = StateInfo(False, "wall_left")
    wall_right: StateInfo = StateInfo(False, "wall_right")
    wall_above: StateInfo = StateInfo(False, "wall_above")
    wall_below: StateInfo = StateInfo(False, "wall_below")
    body_left: StateInfo = StateInfo(False, "body_left")
    body_right: StateInfo = StateInfo(False, "body_right")
    body_below: StateInfo = StateInfo(False, "body_below")
    body_above: StateInfo = StateInfo(False, "body_above")
    danger_left: StateInfo = StateInfo(False, "danger_left")
    danger_right: StateInfo = StateInfo(False, "danger_right")
    danger_down: StateInfo = StateInfo(False, "danger_down")
    danger_up: StateInfo = StateInfo(False, "danger_up")
    going_left_danger_ahead: StateInfo = StateInfo(False, "going_left_danger_ahead")
    going_right_danger_ahead: StateInfo = StateInfo(False, "going_right_danger_ahead")
    going_down_danger_ahead: StateInfo = StateInfo(False, "going_down_danger_ahead")
    going_up_danger_ahead: StateInfo = StateInfo(False, "going_up_danger_ahead")
    snake_size: SnakeSize = SnakeSize(False, "snake_size")

    def dict(self):
        return {index: state_info.name for index, state_info in enumerate(self._state_values)}

    @property
    def value(self):
        return self._state

    def set_state(self):
        self.snake_size.__str__()
        # O estado é uma string de uma sequência de digitos que será recebido por uma
        # função ação valor para decidir o movimento da cobrinha.
        self._state_values = [
            self.food_right,
            self.food_left,
            self.food_below,
            self.food_above,
            #
            # self._wall_left,
            # self._wall_right,
            # self._wall_above,
            # self._wall_below,
            #
            # self._body_left,
            # self._body_right,
            # self._body_above,
            # self._body_below,
            # going_to_food,
            # danger_ahead,
            # self.going_left,
            # self.going_right,
            # self.going_down,
            # self.going_up,

            self.danger_left,
            self.danger_right,
            self.danger_down,
            self.danger_up,
            # self.snake_size,
        ]
        state = build_state_str(self._state_values)
        # state += str(int(self._going_left))
        # state += str(int(self._going_right))
        # state += str(int(self._going_up))
        # state += str(int(self._going_down))

        # state += str(int(going_to_food_right))
        # state += str(int(going_to_food_left))
        # state += str(int(going_to_food_above))
        # state += str(int(going_to_food_below))

        # 1010100011001

        self._state = state
    
    def populate(self, snake: Snake, food_pos: Coord, game_config: GameConfig):
        block = game_config.block_size
        self.snake_size.value = len(snake.body)

        # Posicao da comida relativa a cobrinha
        self.food_right.value = snake.head.x - food_pos.x < 0
        self.food_left.value = snake.head.x - food_pos.x > 0
        self.food_above.value = snake.head.y - food_pos.y > 0
        self.food_below.value = snake.head.y - food_pos.y < 0

        # Direção que a cobrinha está se movendo
        self.going_left.value = snake.velocity.x < 0
        self.going_right.value = snake.velocity.x > 0
        self.going_down.value = snake.velocity.y > 0
        self.going_up.value = snake.velocity.y < 0

        # Se há parede do lado
        self.wall_left.value = snake.head.x - block < 0
        self.wall_right.value = snake.head.x + block >= game_config.screen_width
        self.wall_above.value = snake.head.y - block < 0
        self.wall_below.value = snake.head.y + block >= game_config.screen_height

        # Posição do corpo da cobrinha em relação a cabeça
        self.body_left.value = Coord(snake.head.x - block, snake.head.y) in snake.body
        self.body_right.value = Coord(snake.head.x + block, snake.head.y) in snake.body
        self.body_below.value = Coord(snake.head.x, snake.head.y + block) in snake.body
        self.body_above.value = Coord(snake.head.x, snake.head.y - block) in snake.body

        self.danger_left.value = self.wall_left.value or self.body_left.value
        self.danger_right.value = self.wall_right.value or self.body_right.value
        self.danger_down.value = self.wall_below.value or self.body_below.value
        self.danger_up.value = self.wall_above.value or self.body_above.value
        
        # Se há parede e está indo em direção a ela --Perigo--
        going_left_wall_ahead = self.going_left.value and self.wall_left.value
        going_right_wall_ahead = self.going_right.value and self.wall_right.value
        going_down_wall_ahead = self.going_down.value and self.wall_below.value
        going_up_wall_ahead = self.going_up.value and self.wall_above.value

        wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

        # Se a cobrinha está indo em direção a uma parte do corpo
        going_left_body_ahead = self.going_left.value and self.body_left.value
        going_right_body_ahead = self.going_right.value and self.body_right.value
        going_down_body_ahead = self.going_down.value and self.body_below.value
        going_up_body_ahead = self.going_up.value and self.body_above.value

        # Perigo de uma parte do corpo como obstáculo
        body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

        # Perigo em alguma direção
        danger_ahead = wall_ahead or body_ahead

        going_to_food_right = self.food_right.value and self.going_right.value
        going_to_food_left = self.food_left.value and self.going_left.value
        going_to_food_above = self.food_above.value and self.going_up.value
        going_to_food_below = self.food_below.value and self.going_down.value

        going_to_food = going_to_food_below or going_to_food_above or going_to_food_left or going_to_food_right
        
        self.going_left_danger_ahead = going_left_wall_ahead or going_left_body_ahead
        self.going_right_danger_ahead = going_right_wall_ahead or going_right_body_ahead
        self.going_down_danger_ahead = going_down_wall_ahead or going_down_body_ahead
        self.going_up_danger_ahead = going_up_wall_ahead or going_up_body_ahead

        return self

    def __str__(self):
        return self.value
