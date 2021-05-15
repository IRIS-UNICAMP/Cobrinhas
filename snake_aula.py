import pygame
import time
import random

pygame.init()

game_screen_width = 600
game_screen_height = 600

game_screen = pygame.display.set_mode((game_screen_width, game_screen_height))

pygame.display.update()

game_over = False

blue = (0,0,255)
red = (255,0,0)
white = (255, 255, 255)
black = (0, 0, 0)

snake_initial_height = 20
snake_initial_width = 20

snake_initial_x = 100
snake_initial_y = 100

food_x = 300
food_y = 300
food_width = 20
food_height = 20

score = 0

snake_x = snake_initial_x
snake_y = snake_initial_y

snake_y_change = 0
snake_x_change = 0

snake_speed = 10
snake_block = 20

snake_grid_scale = 20.0

clock = pygame.time.Clock()
snake_list = []
length_of_snake = 1

def human_player_agent(event, snake_x_change, snake_y_change):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            snake_x_change = -snake_block
            snake_y_change = 0
        elif event.key == pygame.K_RIGHT:
            snake_x_change = snake_block
            snake_y_change = 0
        elif event.key == pygame.K_UP:
            snake_y_change = -snake_block
            snake_x_change = 0
        elif event.key == pygame.K_DOWN:
            snake_y_change = snake_block
            snake_x_change = 0

    return [snake_x_change, snake_y_change]

# Comida está em 300,300
# Cobra está em 100,100
# 1/4 (cima), 1/4 (baixo), 1/4 (direita), 1/4 (esquerda)
# 120, 140, 160, ... , 300 -> (300 - 100) / 20 = 200 / 20 = 10 vezes pra direita
# 10 vezes pra baixo
# (1/4)^10 * (1/4)^10 = probabilidade de uma possibilidade válida pra chegar na comida
# 20!/(10!.10!) = 184756 maneiras de chegar na comida

def random_choice_agent(snake_x_change, snake_y_change):
    choice = random.choice(["UP", "DOWN", "RIGHT", "LEFT"])

    if choice == "LEFT":
        snake_x_change = -snake_block
        snake_y_change = 0
    elif choice == "RIGHT":
        snake_x_change = snake_block
        snake_y_change = 0
    elif choice == "UP":
        snake_y_change = -snake_block
        snake_x_change = 0
    elif choice == "DOWN":
        snake_y_change = snake_block
        snake_x_change = 0

    print(choice)
    print([snake_x_change, snake_y_change])

    return [snake_x_change, snake_y_change]

# Experimentar parametrizar com k passos (multiplicar os snake_block)
def make_state():
    state = ""
    """
    - Comida à esquerda
    - Comida à direita
    - Comida abaixo
    - Comida acima
    """
    food_right = (snake_x - food_x < 0)
    food_left = (snake_x - food_x > 0)
    food_down = (snake_y - food_y < 0)
    food_up = (snake_y - food_y > 0)
    """
    Movimento atual da cobra:
    - Esquerda
    - Direita
    - Cima
    - Baixo
    """
    going_left = (snake_x_change < 0)
    going_right = (snake_x_change > 0)
    going_down = (snake_y_change > 0)
    going_up = (snake_y_change < 0)

    """
    Perigos #1: Paredes

    Perigos #2: Corpo
    """

    wall_left = (snake_x - snake_block <= 0)
    wall_right = (snake_x + snake_block >= game_screen_width)
    wall_up = (snake_y - snake_block <= 0)
    wall_down = (snake_y + snake_block >= game_screen_height)

    going_left_wall_ahead = going_left and wall_left
    going_right_wall_ahead = going_right and wall_right
    going_down_wall_ahead = going_down and wall_down
    going_up_wall_ahead = going_up and wall_up

    wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

    body_left = ([snake_x - snake_block, snake_y] in snake_list)
    body_right = ([snake_x + snake_block, snake_y] in snake_list)
    body_up = ([snake_x, snake_y - snake_block] in snake_list)
    body_down = ([snake_x, snake_y + snake_block] in snake_list)

    going_left_body_ahead = going_left and body_left
    going_right_body_ahead = going_right and body_right
    going_down_body_ahead = going_down and body_down
    going_up_body_ahead = going_up and body_up

    body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

    danger_ahead = wall_ahead or body_ahead
    danger_left = wall_left or body_left
    danger_right = wall_right or body_right
    danger_down = wall_down or body_down
    danger_up = wall_up or body_up

    state += str(int(food_right))
    state += str(int(food_left))
    state += str(int(food_down))
    state += str(int(food_up))

    state += str(int(going_left))
    state += str(int(going_right))
    state += str(int(going_down))
    state += str(int(going_up))

    state += str(int(danger_ahead))
    state += str(int(danger_left))
    state += str(int(danger_right))
    state += str(int(danger_up))
    state += str(int(danger_down))

    print(state)
    return state

def choose_action(current_state):
    # Usar o Q!!!
    epsilon = 0.1
    value = random.random()
    if value <= epsilon:
        return random.choice(["UP", "DOWN", "RIGHT", "LEFT"])
    else:
        best = 0
        best_a = ""
        # escolher com base no valor do Q
        for a in ["UP", "DOWN", "RIGHT", "LEFT"]:
            if ia_Q[current_state][a] >= best:
                best = ia_Q[current_state][a]
                best_a = a

        return best_a

    """
    if snake_x - food_x < 0:
        return "RIGHT"

    if snake_x - food_x > 0:
        return "LEFT"

    if snake_x == food_x:
        # começar a mexer y
        if snake_y - food_y < 0:
            return "DOWN"
        if snake_y - food_y > 0:
            return "UP"
    """

def get_action_vector(ia_action):
    xc = snake_x_change
    yc = snake_y_change

    if ia_action == "LEFT":
        xc = -snake_block
        yc = 0
    if ia_action == "RIGHT":
        xc = snake_block
        yc = 0
    if ia_action == "UP":
        yc = -snake_block
        xc = 0
    if ia_action == "DOWN":
        yc = snake_block
        xc = 0

    print(ia_action, xc, yc)
    return [xc, yc]

episode_count = 0
episodes = 1
ia_Q = {}
while episode_count < episodes: # Episódios
    game_over = False
    food_x = 300
    food_y = 300
    score = 0
    snake_x = snake_initial_x
    snake_y = snake_initial_y
    snake_y_change = 0
    snake_x_change = 0
    snake_list = []
    length_of_snake = 1

    ia_S = make_state()
    ia_R = 0

    while not game_over: # Um jogo - um episódio
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                game_over=True
                break

        # Trocar isso pelo vetor retornado por choose_action, depois que ela tiver sido implementada.
        ia_A = choose_action(ia_S)

############# "take action" #####################

        vector_change = get_action_vector(ia_A)
        snake_x_change = vector_change[0]
        snake_y_change = vector_change[1]

        if snake_x >= game_screen_width or snake_x < 0 or snake_y >= game_screen_height or snake_y < 0:
            game_over = True
            print("Perdeu")
            ia_R = -10

        if snake_x == food_x and snake_y == food_y:
            food_x = round(random.randrange(0, game_screen_width - snake_block) / snake_grid_scale) * snake_grid_scale
            food_y = round(random.randrange(0, game_screen_height - snake_block) / snake_grid_scale) * snake_grid_scale
            length_of_snake += 1
            ia_R = +10

        snake_x = snake_x + snake_x_change
        snake_y = snake_y + snake_y_change

        snake_position_and_size = [snake_x, snake_y, snake_initial_width, snake_initial_height]

        game_screen.fill(black)

        snake_head = []
        snake_head.append(snake_x)
        snake_head.append(snake_y)
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for x in snake_list[:-1]:
            if x == snake_head:
                game_over = True
                print("Perdeu")

        snake_parts_drawn = 0
        for x in snake_list:
            if snake_parts_drawn == length_of_snake -1:
                pygame.draw.rect(game_screen, white, [x[0], x[1], snake_block, snake_block])
            else:
                pygame.draw.rect(game_screen, blue, [x[0], x[1], snake_block, snake_block])

            snake_parts_drawn += 1

        score = length_of_snake - 1
        print("Pontos = ", score, "episódio = ", episode_count)

        pygame.draw.rect(game_screen, red, [food_x, food_y, food_width, food_height])
        pygame.display.update()

############# acaba "take action" #####################

        ia_S_ = make_state()
        ia_A_ = choose_action(ia_S_)
        # FALTANDO: Atualizar ia_Q
        ia_S = ia_S_
        ia_A = ia_A_

        clock.tick(snake_speed)

    print("Fim do episódio ", episode_count)
    episode_count += 1
