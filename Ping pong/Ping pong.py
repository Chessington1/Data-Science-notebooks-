import pygame
import math
import random

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()

# --- Load sounds and music ---
pygame.mixer.music.load("bg_music.wav")      # Background music
pygame.mixer.music.play(-1)                  # Loop forever
pygame.mixer.music.set_volume(0.3)           # Medium volume

bounce_sound = pygame.mixer.Sound("bounce.wav")
score_sound = pygame.mixer.Sound("score.wav")

# --- Game setup ---
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pong with Music & Sounds")
clock = pygame.time.Clock()

# --- Game objects ---
left_paddle = pygame.Rect(50, 250, 20, 100)
right_paddle = pygame.Rect(730, 250, 20, 100)
ball = pygame.Rect(390, 290, 20, 20)

# --- Variables ---
paddle_speed = 5
ball_speed = [0, 0]
base_speed = 5
score = [0, 0]
font = pygame.font.Font(None, 36)

# --- Reset Ball ---
def reset_ball():
    ball.center = (400, 300)
    angle = random.uniform(-math.pi / 4, math.pi / 4)
    direction = random.choice([-1, 1])
    ball_speed[0] = direction * base_speed * math.cos(angle)
    ball_speed[1] = base_speed * math.sin(angle)

# --- Main Game Loop ---
running = True
focused = True  # Track window focus

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.ACTIVEEVENT:
            # Pause/Resume music if window focus changes
            if event.state == 2:  # Window focus
                if event.gain == 0:
                    pygame.mixer.music.pause()
                    focused = False
                else:
                    pygame.mixer.music.unpause()
                    focused = True

    keys = pygame.key.get_pressed()

    # Paddle movement
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= paddle_speed
    if keys[pygame.K_s] and left_paddle.bottom < 600:
        left_paddle.y += paddle_speed
    if keys[pygame.K_UP] and right_paddle.top > 0:
        right_paddle.y -= paddle_speed
    if keys[pygame.K_DOWN] and right_paddle.bottom < 600:
        right_paddle.y += paddle_speed

    # Adjust difficulty
    if keys[pygame.K_EQUALS] or keys[pygame.K_PLUS]:
        base_speed += 0.05
    if keys[pygame.K_MINUS] and base_speed > 1:
        base_speed -= 0.05
    if keys[pygame.K_p]:
        paddle_speed += 0.1
    if keys[pygame.K_o] and paddle_speed > 1:
        paddle_speed -= 0.1

    # Start ball if stopped
    if ball_speed == [0, 0]:
        reset_ball()

    # Move ball
    ball.x += ball_speed[0]
    ball.y += ball_speed[1]

    # Bounce off walls
    if ball.top <= 0 or ball.bottom >= 600:
        ball_speed[1] = -ball_speed[1]
        bounce_sound.play()

    # Bounce off paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        ball_speed[0] = -ball_speed[0] * 1.05
        ball_speed[1] *= 1.05
        bounce_sound.play()

    # Score points
    if ball.left <= 0:
        score[1] += 1
        score_sound.play()
        reset_ball()
    if ball.right >= 800:
        score[0] += 1
        score_sound.play()
        reset_ball()

    # --- Draw everything ---
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), left_paddle)
    pygame.draw.rect(screen, (0, 255, 0), right_paddle)
    pygame.draw.ellipse(screen, (255, 0, 0), ball)

    score_text = font.render(f"{score[0]} - {score[1]}", True, (255, 255, 255))
    speed_text = font.render(f"Ball: {base_speed:.1f}  Paddle: {paddle_speed:.1f}", True, (180, 180, 180))
    screen.blit(score_text, (370, 10))
    screen.blit(speed_text, (270, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

