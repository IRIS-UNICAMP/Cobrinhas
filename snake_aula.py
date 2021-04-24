# Jogo da cobrinha

import pygame # Precisamos usar o PyGame, então precisamos importá-lo
import time # Precisamos disso para esperar 2 segundos antes de fechar o jogo quando o jogador perde.

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
food_x = 30
food_y = 30
food_width = 20
food_height = 20

# Posições x e y ATUAIS da cobra. No começo, elas são as posições iniciais que desejamos configurar.
snake_x = snake_initial_x
snake_y = snake_initial_y

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

# Loop de jogo.
# Nós precisamos que o jogo sempre esteja executando, porque caso contrário o script vai chegar ao fim
# e a janela do jogo vai fechar.
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
                snake_x -= 10 # Mover a cobra para a esquerda.
            elif event.key == pygame.K_RIGHT:
                snake_x += 10 # Mover a cobra para a direita.
            elif event.key == pygame.K_UP:
                snake_y -= 10 # Mover a cobra para cima.
            elif event.key == pygame.K_DOWN:
                snake_y += 10 # Mover a cobra para baixo.

    # Verificar se a cobra passou dos limites da tela, ou seja, se bateu na parede.
    if snake_x >= game_screen_width or snake_x < 0 or snake_y >= game_screen_height or snake_y < 0:
        game_over = True # Indicar que o jogo acabou, pra conseguir sair do loop de jogo.
        show_text("Você perdeu :(", white) # Avisar que o jogador perdeu.
        time.sleep(5) # Esperar 5 segundos antes de fechar a janela de jogo.
        pygame.quit() # Fechar a janela de jogo.
        quit() # Sair.

    # Aqui vamos ver se a cobra pegou a comida atual.
    if snake_x == food_x and snake_y == food_y:
        print("Comida") # Por enquanto, só imprimimos no terminal quando isso acontece. Vamos mexer mais nisso na próxima aula!

    # Guardar posição e dimensões da cobra.
    snake_position_and_size = [snake_x, snake_y, snake_initial_width, snake_initial_height]

    # Limpar a tela antes de desenhar nela.
    game_screen.fill(black)

    # Desenhar um retângulo azul, que é a cobra, considerando a posição e as dimensões desejadas.
    pygame.draw.rect(game_screen, blue, snake_position_and_size)

    # Desenhar a comida, também passando como parâmetro as posições e o tamanho.
    pygame.draw.rect(game_screen, red, [food_x, food_y, food_width, food_height])

    # Mandar o PyGame atualizar a tela, pra essas figuras aparecerem :)
    pygame.display.update()

# Ao sair do loop de jogo, ou seja, quando game_over = True, vamos fechar a janela do jogo.
# Sair do jogo e fechar a janela dele.
pygame.quit()
quit()
