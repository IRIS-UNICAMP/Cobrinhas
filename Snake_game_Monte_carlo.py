import pygame
import time
import random
import math



#----------------------------------------------Inicializar pygame----------------------------------------------#
pygame.init()




#-------------------Posicoes disponíveis na tela do jogo-------------------#
# Linhas : 0 -> 600 de 20 em 20
# Colunas : 0 -> 600 colunas de 20 em 20
posicoes_tela = set()
for x in range(0, 600, 20):
    for y in range(0, 600, 20):
        posicoes_tela.add((x,y))
#--------------------------------------------------------------------------#




#------------------------Criando o display do jogo-------------------------#
# Dimensões
game_screen_weight = 600
game_screen_width = 600

# Inicializando objeto
game_screen = pygame.display.set_mode((game_screen_weight, game_screen_width))
pygame.display.update()
#--------------------------------------------------------------------------#




#----------------------------Criando a cobrinha----------------------------#
# Corpo da cobrinha
snake_list = []

# Cor
blue = (67,59,103)

# Tamanho inicial da cobrinha
snake_initial_height = 20
snake_initial_width = 20
length_of_snake = 1
snake_block = 20

# Posição
snake_x, snake_y = random.choice(list(posicoes_tela))
snake_list.append((snake_x, snake_y))

# Mudança na posição a cada movimento
snake_x_change = 0
snake_y_change = 0

# Velocidade da cobrinha
snake_speed = 150
#--------------------------------------------------------------------------#




#-----------------------------Criando a comida-----------------------------#
# Cor
red = (200, 112, 126)

# Posição
food_x, food_y = random.choice(list(posicoes_tela - set(snake_list)))

#Tamanho
food_heigth = 20
food_width = 20
#--------------------------------------------------------------------------#




#---------------------Componentes que aparecem na tela---------------------#
# Pontuação
score = 0

# Definindo um font style para imprimir uma mensagem na tela
font_style = pygame.font.SysFont(None, 50)
def show_text(text, color):
    text_object =  font_style.render(text, True, color)
    game_screen.blit(text_object, [game_screen_weight/2 - 100, game_screen_width/2 - 50])
    pygame.display.update()
#--------------------------------------------------------------------------#




#----------------------------Analises de estado----------------------------#
# Saber quando terminar o jogo
game_over = False

# Usado para congelar o tempo da repetição do laço while um tempo.
clock = pygame.time.Clock()
#--------------------------------------------------------------------------#




#------------------------------Agente Humano-------------------------------#
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
#--------------------------------------------------------------------------#




#------------------------Estados de jogo da cobrinha-----------------------#
def make_state():

    # Posicao da comida relativa a cobrinha
    food_right = (snake_x - food_x < 0)
    food_left = (snake_x - food_x > 0)
    food_down = (snake_y - food_y < 0)
    food_up = (snake_y  - food_y > 0)

    # Direção que a cobrinha está se movendo
    going_left = (snake_x_change < 0)
    going_right = (snake_x_change > 0)
    going_down = (snake_y_change > 0)
    going_up = (snake_y_change < 0)


    """"
    Perigos #1: Paredes
    Perigos #2: Corpo
    """

    # Se há parede do lado
    wall_left = (snake_x - snake_block <= 0)
    wall_right = (snake_x + snake_block >= game_screen_width)
    wall_up = (snake_y - snake_block <= 0)
    wall_down = (snake_y + snake_block >= game_screen_weight)

    # Se há parede e está indo em direção a ela --Perigo--
    going_left_wall_ahead = going_left and wall_left
    going_right_wall_ahead = going_right and wall_right
    going_down_wall_ahead = going_down and wall_down
    going_up_wall_ahead = going_up and wall_up

    # Perigo de uma parede
    wall_ahead = going_left_wall_ahead or going_right_wall_ahead or going_down_wall_ahead or going_up_wall_ahead

    # Posição do corpo da cobrinha em relação a cabeça
    body_left = ((snake_x - snake_block, snake_y) in snake_list)
    body_right = ((snake_x + snake_block, snake_y) in snake_list)
    body_down = ((snake_x, snake_y + snake_block) in snake_list)
    body_up = ((snake_x, snake_y - snake_block) in snake_list)

    # Se a cobrinha está indo em direção a uma parte do corpo
    going_left_body_ahead = going_left and body_left
    going_right_body_ahead = going_right and body_right
    going_down_body_ahead = going_down and body_down
    going_up_body_ahead = going_up and body_up

    # Perigo de uma parte do corpo como obstáculo
    body_ahead = going_left_body_ahead or going_right_body_ahead or going_down_body_ahead or going_up_body_ahead

    # Perigo em alguma direção
    danger_ahead = wall_ahead or body_ahead
    danger_left = wall_left or body_left
    danger_right = wall_right or body_right
    danger_down = wall_down or body_down
    danger_up = wall_up or body_up


    # O estado é uma string de uma sequência de digitos que será recebido por uma
    # função ação valor para decidir o movimento da cobrinha.
    state = ''
    state += str(int(food_left))
    state += str(int(food_right))
    state += str(int(food_down))
    state += str(int(food_up))

    state += str(int(going_left))
    state += str(int(going_right))
    state += str(int(going_down))
    state += str(int(going_up))

    state += str(int(danger_ahead))
    state += str(int(danger_left))
    state += str(int(danger_right))
    state += str(int(danger_down))
    state += str(int(danger_up))
    
    return state
#--------------------------------------------------------------------------#



def get_action_vector(action):
    if action == "LEFT":
        return [-snake_block, 0]
    
    elif action == "RIGHT":
        return [snake_block, 0]

    elif action == "DOWN":
        return [0, +snake_block]
    
    elif action == "UP":
        return [0, -snake_block]



def choose_action(ia_S):

    epsilon = 5/(5 + ia_N_S.get(ia_S, 0))  ## Aumentar a cte 1 para testes
    
    value = random.random()
    if value <= epsilon:
        action = random.choice(["UP", "DOWN", "RIGHT", "LEFT"])
        while [(-1)*snake_x_change, (-1)*snake_y_change] == get_action_vector(action):
            action = random.choice(["UP", "DOWN", "RIGHT", "LEFT"])
        return action
    else:
        # escolher melhor ação com base no valor do Q
        best = -1000000000000000000000
        best_a = ""
        for a in ["UP", "DOWN", "RIGHT", "LEFT"]:
            action_value = ia_Q[ia_S].get(a, 0)   # As ações que ainda não estao no dict para um dado estado, terão previsão 0
            if action_value >= best:
                best = action_value    
                best_a = a
        

        # Escolher segunda melhor ação
        second_best = -1000000000000000000000
        second_best_a = ""
        for a in ["UP", "DOWN", "RIGHT", "LEFT"]:
            action_value = ia_Q[ia_S].get(a, 0)
            if action_value >= second_best and a != best_a:
                second_best = action_value
                second_best_a = a
        
        # Se a melhor ação é o sentido contrário do movimento atual, a cobrinha morreria se fosse nessa direção.
        if [(-1)*snake_x_change, (-1)*snake_y_change] == get_action_vector(best_a):
            best_a = second_best_a
                
        
        return best_a





#----------------------Repetição do jogo em vários episódios para treinar a IA---------------------#

episode_count = 0
episodes = 10000
ia_Q = {}
ia_N_S_A = {}
ia_N_S = {}
gamma = 0.2

while episode_count < episodes:
    # Fim de jogo
    game_over = False

    # Cobrinha
    snake_list = []
    snake_x_change = 0
    snake_y_change = 0
    snake_x, snake_y = random.choice(list(posicoes_tela))
    snake_list.append((snake_x, snake_y))
    length_of_snake = 1
    fuel = 900
    passos = 0
    

    #comida
    food_x, food_y = random.choice(list(posicoes_tela - set(snake_list)))

    # Distancia inicial da cobrinha a comida
    dist = (snake_x - food_x)*(snake_x - food_x) + (snake_y - food_y)*(snake_y - food_y)

    # Pontuação e número de episódios
    score = 0
    episode_count += 1

    # Estados e pontuação da IA
    ia_R = 0
    ia_G = 0

    #Estados de um episódio
    states_and_actions_visited = []

    # Numero de açoes do episodio
    n_acoes_episodio = 0


    #---------------------Loop para manter o jogo rodando----------------------#
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            

        # Estado atual
        ia_S = make_state()
        # Ação escolhida pelo Monte carlo para aquele estado
        ia_A = choose_action(ia_S)

        # Se tem energia suficiente, usa o monte carlo, senão sorteia uma ação aleatória. Objetivo : Evitar loops infinitos.
        if (fuel > 0):
            vector_action = get_action_vector(ia_A)
        else:
            vector_action = get_action_vector(random.choice(["UP", "DOWN", "RIGHT", "LEFT"]))
            while [(-1)*snake_x_change, (-1)*snake_y_change] == vector_action:
                vector_action = get_action_vector(random.choice(["UP", "DOWN", "RIGHT", "LEFT"]))
            fuel = 900

        snake_x_change = vector_action[0]
        snake_y_change = vector_action[1]


        # Atualizar posição da cobrinha
        snake_x = snake_x + snake_x_change
        snake_y = snake_y + snake_y_change

        # ia_R = -1 (Ou usa isso, o a analise de distancias da cobrinha até a comida.)

        # A cada movimento perde 1 de energia. 900 é o numero de quadrados disponivies na tela.
        fuel -= 1

        #Punições de acordo com a distancia da cobrinha a comida
        dist_atual = (snake_x - food_x)*(snake_x - food_x) + (snake_y - food_y)*(snake_y - food_y)
        ia_R = (dist - dist_atual)*0.001
        

        # Terminar o jogo quando a cobrinha encosta nas bordas.
        if snake_x >= game_screen_width or snake_x < 0 or snake_y >= game_screen_weight or snake_y < 0 :
            game_over = True
            show_text("Episodio: " + str(episode_count), [0,0,0])
            time.sleep(0.3)
            ia_R = -900
        

        # Sortear nova posição da comida quando a cobrinha come
        if snake_x == food_x and snake_y == food_y:
            posicoes_disponiveis = list(posicoes_tela - set(snake_list))
            food_x, food_y = random.choice(posicoes_disponiveis)
            
            length_of_snake += 1
            ia_R = fuel  # A IA recebe como recompensa por comer a energia restante. Logo, quanto menos ela demorar para comer,
            fuel = 900   # mais pontos ela ganha. Ao comer a energia volta para 900.
            passos = 0

        

        # Redesenhar a cobrinha
        snake_head = (snake_x, snake_y)
        snake_list.append(snake_head)
        
        len_snake = len(snake_list)
        if (len_snake == 2 and snake_list[0] == snake_list[1]):
            del snake_list[0]
            len_snake -= 1

        
        for x in snake_list[:-1]:
            if x == snake_head:
                game_over = True
                show_text("Episodio: " + str(episode_count), [0,0,0])
                time.sleep(0.3)
                ia_R = -900
        
        if len_snake > length_of_snake:
            del snake_list[0]


        n_acoes_episodio += 1
        passos += 1
        if passos == 10000:
            game_over = True

        # Soma das recompensas
        ia_G = ia_G*gamma + ia_R

        # Limpar a tela antes de colocar na tela a nova posição da cobrinha e da comida.
        game_screen.fill([158, 206, 225])
        for x in snake_list:
            pygame.draw.rect(game_screen, blue, [x[0], x[1], snake_block, snake_block])

        pygame.draw.rect(game_screen, red, [food_x, food_y, food_heigth, food_width])


        # Pontuações
        value = font_style.render("Score: " + str(length_of_snake), True, [255,255,255])
        game_screen.blit(value, [0, 0])


        states_and_actions_visited.append((ia_S, ia_A))
        dist = dist_atual

        # Atualizar o display e congelar brevemente o tempo
        pygame.display.update()
        clock.tick(snake_speed)
    #--------------------------------------------------------------------------#


    #---------------------Aprender/ Atualizar o ia_Q---------------------------#
    for s, a in states_and_actions_visited:
        if s in ia_Q.keys():
            ia_N_S[s] += 1
            if a in ia_N_S_A.keys():
                ia_N_S_A[s][a] += 1
                ia_Q[s][a] += (ia_G - ia_Q[s][a])/(ia_N_S_A)
            else:
                ia_Q[s][a] = ia_G
                ia_N_S_A[s][a] = 1
        else:
            ia_Q[s] = dict()
            ia_Q[s][a] = ia_G
            ia_N_S_A[s] = dict()
            ia_N_S_A[s][a] = 1
            ia_N_S[s] = 1
            

#------------------------------Fechar o jogo-------------------------------#
pygame.quit()
quit()
#--------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------#
