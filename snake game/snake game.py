import pygame
import random

# Initialize pygame
pygame.init()

# 🎶 Initialize sound system
pygame.mixer.init()

# Load sounds (make sure these files are in the same folder)
eat_sound = pygame.mixer.Sound("eat.wav")       # play when food eaten
game_over_sound = pygame.mixer.Sound("gameover.wav")  # play on collision

# Game settings
WIDTH, HEIGHT = 400, 400
CELL = 20
FPS = 15

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🐍 Snake Game with Sound")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Initialize variables
snake = [(200, 200)]
snake_dir = (0, 0)
food = pygame.Rect(random.randrange(0, WIDTH - CELL, CELL),
                   random.randrange(0, HEIGHT - CELL, CELL),
                   CELL, CELL)
score = 0
running = True

# Function to reset the game
def reset_game():
    global snake, snake_dir, food, score
    snake = [(200, 200)]
    snake_dir = (0, 0)
    food.topleft = (random.randrange(0, WIDTH - CELL, CELL),
                    random.randrange(0, HEIGHT - CELL, CELL))
    score = 0
    pygame.mixer.Sound.play(game_over_sound)

# Main game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement control
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake_dir != (0, CELL):
        snake_dir = (0, -CELL)
    elif keys[pygame.K_DOWN] and snake_dir != (0, -CELL):
        snake_dir = (0, CELL)
    elif keys[pygame.K_LEFT] and snake_dir != (CELL, 0):
        snake_dir = (-CELL, 0)
    elif keys[pygame.K_RIGHT] and snake_dir != (-CELL, 0):
        snake_dir = (CELL, 0)

    if snake_dir != (0, 0):
        head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
        snake.insert(0, head)

        # 🍎 Check food collision
        if pygame.Rect(head, (CELL, CELL)).colliderect(food):
            score += 1
            pygame.mixer.Sound.play(eat_sound)
            food.topleft = (random.randrange(0, WIDTH - CELL, CELL),
                            random.randrange(0, HEIGHT - CELL, CELL))
        else:
            snake.pop()

        # 💥 Collision with walls or itself
        if (head in snake[1:] or head[0] < 0 or head[0] >= WIDTH or head[1] < 0 or head[1] >= HEIGHT):
            reset_game()

    # Draw everything
    screen.fill(BLACK)
    for pos in snake:
        pygame.draw.rect(screen, GREEN, (pos[0], pos[1], CELL, CELL))
    pygame.draw.rect(screen, RED, food)

    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()


