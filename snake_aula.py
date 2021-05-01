# Jogo da cobrinha

# Coisas pra fazer:
# - a cobra não pode se mexer pra baixo, se ela estiver se mexendo pra cima.

import pygame # Precisamos usar o PyGame, então precisamos importá-lo
import time # Precisamos disso para esperar 2 segundos antes de fechar o jogo quando o jogador perde.
import random # Aleatoriedade nas posições da comida.

pygame.init() # Inicializar o PyGame.

game_screen_width = 600 # Largura da nossa tela de jogo.
game_screen_height = 600 # Altura da nossa tela de jogo.

# Criando tela de jogo com as dimensões desejadas.
game_screen = pygame.display.set_mode((game_screen_width, game_screen_height))

# Mandar o PyGame atualizar a tela, para que ela apareça.
pygame.display.update()

# Indicar se o jogo já acabou ou não.
game_over = False

# Cores (sistema RGB) que vamos usar.
blue = (0,0,255)
red = (255,0,0)
white = (255, 255, 255)
black = (0, 0, 0)

# Altura e largura da cobra. Por enquanto, ela é um quadrado. Vamos melhorar isso em breve!
snake_initial_height = 20
snake_initial_width = 20

# Posições iniciais da cobra.
snake_initial_x = 0
snake_initial_y = 0

# Posições iniciais, largura e altura de uma comida fixa no mapa.
food_x = 300
food_y = 300
food_width = 20
food_height = 20

score = 0

# Posições x e y ATUAIS da cobra. No começo, elas são as posições iniciais que desejamos configurar.
snake_x = snake_initial_x
snake_y = snake_initial_y

snake_y_change = 0
snake_x_change = 0

snake_speed = 10
snake_block = 20

snake_grid_scale = 20.0

# Precisamos disso pra conseguir mostrar texto no PyGame.
font_style = pygame.font.SysFont(None, 50)

# Função para mostrar texto no PyGame.
def show_text(text, color):
    text_object = font_style.render(text, True, color) # Objeto de texto que vai ser mostrado.
    # game_screen.blit adiciona um objeto na tela.
    # Aqui, estamos adicionando o objeto de texto criado, na posição x = game_screen_width/2 e y = game_screen_height/2.
    game_screen.blit(text_object, [game_screen_width/2, game_screen_height/2])
    # Mandar o PyGame atualizar a tela depois de adicionar alguma coisa, por que se não não vai aparecer.
    pygame.display.update()

clock = pygame.time.Clock() # Velocidade?
# Loop de jogo.
# Nós precisamos que o jogo sempre esteja executando, porque caso contrário o script vai chegar ao fim
# e a janela do jogo vai fechar.
snake_list = []
length_of_snake = 1

while not game_over:
    # Ver se "eventos" aconteceram, pegando todos os eventos.
    # Um evento é qualquer atividade do jogador na tela de jogo.
    # O ato de mover o mouse ou de clicar é um evento, por exemplo.
    # O de pressionar uma tecla do teclado também.
    for event in pygame.event.get():
        # Verificar se o evento atual é um evento do tipo QUIT.
        # QUIT = alguém fechar o jogo clicando no x para fechar a janela dele.
        if event.type==pygame.QUIT:
            game_over=True # Se estamos fechando o jogo, game_over = True
            break # Sair do loop de jogo em vez de continuar.

        # Aqui, queremos saber se o jogador está pressionando as setas para se mexer.
        if event.type == pygame.KEYDOWN:
            # Aqui, queremos saber qual seta (direita, esquerda, cima, baixo).
            if event.key == pygame.K_LEFT:
                snake_x_change = -snake_block # Mover a cobra para a esquerda.
                snake_y_change = 0
            elif event.key == pygame.K_RIGHT:
                snake_x_change = snake_block # Mover a cobra para a direita.
                snake_y_change = 0
            elif event.key == pygame.K_UP:
                snake_y_change = -snake_block # Mover a cobra para cima.
                snake_x_change = 0
            elif event.key == pygame.K_DOWN:
                snake_y_change = snake_block # Mover a cobra para baixo.
                snake_x_change = 0

    # Verificar se a cobra passou dos limites da tela, ou seja, se bateu na parede.
    if snake_x >= game_screen_width or snake_x < 0 or snake_y >= game_screen_height or snake_y < 0:
        game_over = True # Indicar que o jogo acabou, pra conseguir sair do loop de jogo.
        show_text("Você perdeu :(", white) # Avisar que o jogador perdeu.
        time.sleep(5) # Esperar 5 segundos antes de fechar a janela de jogo.
        pygame.quit() # Fechar a janela de jogo.
        quit() # Sair.

    # Aqui vamos ver se a cobra pegou a comida atual.
    if snake_x == food_x and snake_y == food_y:
        food_x = round(random.randrange(0, game_screen_width - snake_block) / snake_grid_scale) * snake_grid_scale
        food_y = round(random.randrange(0, game_screen_height - snake_block) / snake_grid_scale) * snake_grid_scale
        length_of_snake += 1
        # Teste! Ver como fica a comida nos limites.
        #food_x = round((game_screen_width - snake_block) / snake_grid_scale) * snake_grid_scale
        #food_y = round((game_screen_height - snake_block) / snake_grid_scale) * snake_grid_scale

    snake_x = snake_x + snake_x_change
    snake_y = snake_y + snake_y_change

    # Guardar posição e dimensões da cobra.
    snake_position_and_size = [snake_x, snake_y, snake_initial_width, snake_initial_height]

    # Limpar a tela antes de desenhar nela.
    game_screen.fill(black)

    # Desenhar um retângulo azul, que é a cobra, considerando a posição e as dimensões desejadas.
    # pygame.draw.rect(game_screen, blue, snake_position_and_size)
    snake_head = []
    snake_head.append(snake_x)
    snake_head.append(snake_y)
    snake_list.append(snake_head)

    if len(snake_list) > length_of_snake:
        del snake_list[0]

    for x in snake_list[:-1]:
        if x == snake_head:
            game_over = True

    for x in snake_list:
        pygame.draw.rect(game_screen, blue, [x[0], x[1], snake_block, snake_block])

    value = font_style.render("Score: " + str(length_of_snake - 1), True, white)
    game_screen.blit(value, [0, 0])

    # Desenhar a comida, também passando como parâmetro as posições e o tamanho.
    pygame.draw.rect(game_screen, red, [food_x, food_y, food_width, food_height])

    # Mandar o PyGame atualizar a tela, pra essas figuras aparecerem :)
    pygame.display.update()

    clock.tick(snake_speed) #Velocidade?

# Ao sair do loop de jogo, ou seja, quando game_over = True, vamos fechar a janela do jogo.
# Sair do jogo e fechar a janela dele.
pygame.quit()
quit()
