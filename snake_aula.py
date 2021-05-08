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

font_style = pygame.font.SysFont(None, 50)

def show_text(text, color):
    text_object = font_style.render(text, True, color)
    game_screen.blit(text_object, [game_screen_width/2, game_screen_height/2])
    pygame.display.update()

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

while not game_over:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            game_over=True
            break

        # Trocar isso pela sua IA.
        vector_change = human_player_agent(event, snake_x_change, snake_y_change)
        snake_x_change = vector_change[0]
        snake_y_change = vector_change[1]

    if snake_x >= game_screen_width or snake_x < 0 or snake_y >= game_screen_height or snake_y < 0:
        game_over = True
        show_text("Você perdeu :(", white)
        time.sleep(5)
        pygame.quit()
        quit()

    if snake_x == food_x and snake_y == food_y:
        food_x = round(random.randrange(0, game_screen_width - snake_block) / snake_grid_scale) * snake_grid_scale
        food_y = round(random.randrange(0, game_screen_height - snake_block) / snake_grid_scale) * snake_grid_scale
        length_of_snake += 1

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

    snake_parts_drawn = 0
    for x in snake_list:
        if snake_parts_drawn == length_of_snake -1:
            pygame.draw.rect(game_screen, white, [x[0], x[1], snake_block, snake_block])
        else:
            pygame.draw.rect(game_screen, blue, [x[0], x[1], snake_block, snake_block])

        snake_parts_drawn += 1

    value = font_style.render("Score: " + str(length_of_snake - 1), True, white)
    game_screen.blit(value, [0, 0])

    pygame.draw.rect(game_screen, red, [food_x, food_y, food_width, food_height])
    pygame.display.update()

    clock.tick(snake_speed)

pygame.quit()
quit()
