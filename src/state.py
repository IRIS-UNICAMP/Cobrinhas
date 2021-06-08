from dataclasses import dataclass
from typing import List

from src.configs import GameConfig
from src.shared import Coord
from src.snake import Snake


@dataclass()
class StateInfo:
    value: bool
    name: str


def build_state_str(values: List[StateInfo]):
    state = ''
    for v in values:
        state += str(int(v.value))
    return state


class State:
    _state: str
    _state_values: List[StateInfo]

    _food_right: StateInfo = StateInfo(False, "food_right")
    _food_left: StateInfo = StateInfo(False, "food_left")
    _food_below: StateInfo = StateInfo(False, "food_below")
    _food_above: StateInfo = StateInfo(False, "food_above")
    _going_left: StateInfo = StateInfo(False, "going_left")
    _going_right: StateInfo = StateInfo(False, "going_right")
    _going_down: StateInfo = StateInfo(False, "going_down")
    _going_up: StateInfo = StateInfo(False, "going_up")
    _wall_left: StateInfo = StateInfo(False, "wall_left")
    _wall_right: StateInfo = StateInfo(False, "wall_right")
    _wall_above: StateInfo = StateInfo(False, "wall_above")
    _wall_below: StateInfo = StateInfo(False, "wall_below")
    _body_left: StateInfo = StateInfo(False, "body_left")
    _body_right: StateInfo = StateInfo(False, "body_right")
    _body_below: StateInfo = StateInfo(False, "body_below")
    _body_above: StateInfo = StateInfo(False, "body_above")
    _danger_left: StateInfo = StateInfo(False, "danger_left")
    _danger_right: StateInfo = StateInfo(False, "danger_right")
    _danger_down: StateInfo = StateInfo(False, "danger_down")
    _danger_up: StateInfo = StateInfo(False, "danger_up")

    def dict(self):
        return {index: state_info.name for index, state_info in enumerate(self._state_values)}

    @property
    def value(self):
        return self._state

    def set_state(self):
        # Se há parede e está indo em direção a ela --Perigo--
        going_left_wall_ahead = self._going_left.value and self._wall_left.value
        going_right_wall_ahead = self._going_right.value and self._wall_right.value
        going_down_wall_ahead = self._going_down.value and self._wall_below.value
        going_up_wall_ahead = self._going_up.value and self._wall_above.value

        wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

        # Se a cobrinha está indo em direção a uma parte do corpo
        going_left_body_ahead = self._going_left.value and self._body_left.value
        going_right_body_ahead = self._going_right.value and self._body_right.value
        going_down_body_ahead = self._going_down.value and self._body_below.value
        going_up_body_ahead = self._going_up.value and self._body_above.value

        # Perigo de uma parte do corpo como obstáculo
        body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

        # Perigo em alguma direção
        danger_ahead = wall_ahead or body_ahead
        self._danger_left.value = self._wall_left.value or self._body_left.value
        self._danger_right.value = self._wall_right.value or self._body_right.value
        self._danger_down.value = self._wall_below.value or self._body_below.value
        self._danger_up.value = self._wall_above.value or self._body_above.value

        going_to_food_right = self._food_right.value and self._going_right.value
        going_to_food_left = self._food_left.value and self._going_left.value
        going_to_food_above = self._food_above.value and self._going_up.value
        going_to_food_below = self._food_below.value and self._going_down.value

        going_to_food = going_to_food_below or going_to_food_above or going_to_food_left or going_to_food_right

        # O estado é uma string de uma sequência de digitos que será recebido por uma
        # função ação valor para decidir o movimento da cobrinha.
        self._state_values = [
            self._food_right,
            self._food_left,
            self._food_below,
            self._food_above,
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
            self._going_left,
            self._going_right,
            self._going_down,
            self._going_up,

            self._danger_left,
            self._danger_right,
            self._danger_down,
            self._danger_up,
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
        # Posicao da comida relativa a cobrinha
        self._food_right.value = snake.head.x - food_pos.x < 0
        self._food_left.value = snake.head.x - food_pos.x > 0
        self._food_above.value = snake.head.y - food_pos.y > 0
        self._food_below.value = snake.head.y - food_pos.y < 0

        # Direção que a cobrinha está se movendo
        self._going_left.value = snake.velocity.x < 0
        self._going_right.value = snake.velocity.x > 0
        self._going_down.value = snake.velocity.y > 0
        self._going_up.value = snake.velocity.y < 0

        # Se há parede do lado
        self._wall_left.value = snake.head.x - block <= 0
        self._wall_right.value = snake.head.x + block >= game_config.screen_width
        self._wall_above.value = snake.head.y - block <= 0
        self._wall_below.value = snake.head.y + block >= game_config.screen_height

        # Posição do corpo da cobrinha em relação a cabeça
        self._body_left.value = Coord(snake.head.x - block, snake.head.y) in snake.body
        self._body_right.value = Coord(snake.head.x + block, snake.head.y) in snake.body
        self._body_below.value = Coord(snake.head.x, snake.head.y - block) in snake.body
        self._body_above.value = Coord(snake.head.x, snake.head.y + block) in snake.body

        return self

    def __str__(self):
        return self.value
