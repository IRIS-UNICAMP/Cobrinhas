from typing import List

from src.configs import GameConfig
from src.shared import Coord
from src.snake import Snake


def build_state_str(values: List[bool]):
    state = ''
    for v in values:
        state += str(int(v))
    return state


class State:
    _state: str

    _food_right: bool = False
    _food_left: bool = False
    _food_below: bool = False
    _food_above: bool = False

    _going_left: bool = False
    _going_right: bool = False
    _going_down: bool = False
    _going_up: bool = False

    _wall_left: bool = False
    _wall_right: bool = False
    _wall_above: bool = False
    _wall_below: bool = False
    
    _body_left: bool = False
    _body_right: bool = False
    _body_below: bool = False
    _body_above: bool = False

    @property
    def value(self):
        return self._state

    def set_state(self):
        # Se há parede e está indo em direção a ela --Perigo--
        going_left_wall_ahead = self._going_left and self._wall_left
        going_right_wall_ahead = self._going_right and self._wall_right
        going_down_wall_ahead = self._going_down and self._wall_below
        going_up_wall_ahead = self._going_up and self._wall_above

        wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

        # Se a cobrinha está indo em direção a uma parte do corpo
        going_left_body_ahead = self._going_left and self._body_left
        going_right_body_ahead = self._going_right and self._body_right
        going_down_body_ahead = self._going_down and self._body_below
        going_up_body_ahead = self._going_up and self._body_above

        # Perigo de uma parte do corpo como obstáculo
        body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

        # Perigo em alguma direção
        danger_ahead = wall_ahead or body_ahead
        danger_left = self._wall_left or self._body_left
        danger_right = self._wall_right or self._body_right
        danger_down = self._wall_below or self._body_below
        danger_up = self._wall_above or self._body_above

        going_to_food_right = self._food_right and self._going_right
        going_to_food_left = self._food_left and self._going_left
        going_to_food_above = self._food_above and self._going_up
        going_to_food_below = self._food_below and self._going_down

        going_to_food = going_to_food_below or going_to_food_above or going_to_food_left or going_to_food_right

        # O estado é uma string de uma sequência de digitos que será recebido por uma
        # função ação valor para decidir o movimento da cobrinha.
        state_values = [
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
            danger_left,
            danger_right,
            danger_down,
            danger_up,
        ]
        state = build_state_str(state_values)
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
        self._food_right = snake.head.x - food_pos.x < 0
        self._food_left = snake.head.x - food_pos.x > 0
        self._food_above = snake.head.y - food_pos.y > 0
        self._food_below = snake.head.y - food_pos.y < 0

        # Direção que a cobrinha está se movendo
        self._going_left = snake.velocity.x < 0
        self._going_right = snake.velocity.x > 0
        self._going_down = snake.velocity.y > 0
        self._going_up = snake.velocity.y < 0

        # Se há parede do lado
        self._wall_left = snake.head.x - block <= 0
        self._wall_right = snake.head.x + block >= game_config.screen_width
        self._wall_above = snake.head.y - block <= 0
        self._wall_below = snake.head.y + block >= game_config.screen_height

        # Posição do corpo da cobrinha em relação a cabeça
        self._body_left = Coord(snake.head.x - block, snake.head.y) in snake.body
        self._body_right = Coord(snake.head.x + block, snake.head.y) in snake.body
        self._body_below = Coord(snake.head.x, snake.head.y - block) in snake.body
        self._body_above = Coord(snake.head.x, snake.head.y + block) in snake.body

        return self

    def __str__(self):
        return self.value
