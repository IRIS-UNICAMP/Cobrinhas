from src.configs import GameConfig
from src.shared import Coord
from src.snake import Snake


class State:
    food_right: bool = False
    food_left: bool = False
    food_below: bool = False
    food_above: bool = False

    going_left: bool = False
    going_right: bool = False
    going_down: bool = False
    going_up: bool = False

    wall_left: bool = False
    wall_right: bool = False
    wall_above: bool = False
    wall_below: bool = False
    
    body_left: bool = False
    body_right: bool = False
    body_below: bool = False
    body_above: bool = False

    def state(self):
        # Se há parede e está indo em direção a ela --Perigo--
        going_left_wall_ahead = self.going_left and self.wall_left
        going_right_wall_ahead = self.going_right and self.wall_right
        going_down_wall_ahead = self.going_down and self.wall_below
        going_up_wall_ahead = self.going_up and self.wall_above

        wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

        # Se a cobrinha está indo em direção a uma parte do corpo
        going_left_body_ahead = self.going_left and self.body_left
        going_right_body_ahead = self.going_right and self.body_right
        going_down_body_ahead = self.going_down and self.body_below
        going_up_body_ahead = self.going_up and self.body_above

        # Perigo de uma parte do corpo como obstáculo
        body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

        # Perigo em alguma direção
        danger_ahead = wall_ahead or body_ahead
        danger_left = self.wall_left or self.body_left
        danger_right = self.wall_right or self.body_right
        danger_down = self.wall_below or self.body_below
        danger_up = self.wall_above or self.body_above

        # O estado é uma string de uma sequência de digitos que será recebido por uma
        # função ação valor para decidir o movimento da cobrinha.
        state = ''
        state += str(int(self.food_right))
        state += str(int(self.food_left))
        state += str(int(self.food_below))
        state += str(int(self.food_above))

        state += str(int(self.going_left))
        state += str(int(self.going_right))
        state += str(int(self.going_down))
        state += str(int(self.going_up))

        state += str(int(danger_ahead))
        state += str(int(danger_left))
        state += str(int(danger_right))
        state += str(int(danger_down))
        state += str(int(danger_up))

        return state
    
    def populate(self, snake: Snake, food_pos: Coord, game_config: GameConfig):
        block = game_config.block_size
        # Posicao da comida relativa a cobrinha
        self.food_right = snake.head.x - food_pos.x < 0
        self.food_left = snake.head.x - food_pos.x > 0
        self.food_above = snake.head.y - food_pos.y > 0 
        self.food_below = snake.head.y - food_pos.y < 0 

        # Direção que a cobrinha está se movendo
        self.going_left = snake.velocity.x < 0
        self.going_right = snake.velocity.x > 0
        self.going_down = snake.velocity.y > 0
        self.going_up = snake.velocity.y < 0

        # Se há parede do lado
        self.wall_left = snake.head.x - block <= 0
        self.wall_right = snake.head.x + block >= game_config.screen_width
        self.wall_above = snake.head.y - block <= 0
        self.wall_below = snake.head.y + block >= game_config.screen_height

        # Posição do corpo da cobrinha em relação a cabeça
        self.body_left = Coord(snake.head.x - block, snake.head.y) in snake.body
        self.body_right = Coord(snake.head.x + block, snake.head.y) in snake.body
        self.body_below = Coord(snake.head.x, snake.head.y - block) in snake.body
        self.body_above = Coord(snake.head.x, snake.head.y + block) in snake.body

    def __str__(self):
        return self.state()
