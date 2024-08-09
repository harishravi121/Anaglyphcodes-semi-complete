import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 600, 400
screen = pygame.display.set_mode((width, height), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption("3D Snake")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
cyan = (0, 255, 255)
green = (0, 255, 0)

# Snake properties
snake_size = 10
snake = [(width / 2, height / 2, 0)]  # Initial snake segment (with z-coordinate for 3D)
snake_direction = (1, 0, 0)  # Initial direction (right)

# Food
food = (random.randint(0, width - snake_size), random.randint(0, height - snake_size), 0)

# Projection function (with anaglyph offset)
def project(vertex, eye_offset):
    x, y, z = vertex
    focal_length = 5
    x += eye_offset
    projected_x = int(x * focal_length / (z + focal_length) * 50 + width / 2)
    projected_y = int(y * focal_length / (z + focal_length) * 50 + height / 2)
    return projected_x, projected_y

# Draw functions
def draw_square(x, y, z, color):
    points_left = [(x, y, z), (x + snake_size, y, z), (x + snake_size, y + snake_size, z), (x, y + snake_size, z)]
    points_right = [(x, y, z + 0.2), (x + snake_size, y, z + 0.2), (x + snake_size, y + snake_size, z + 0.2), (x, y + snake_size, z + 0.2)]

    for i in range(4):
        p1_left = project(points_left[i], -0.1)
        p2_left = project(points_left[(i + 1) % 4], -0.1)
        pygame.draw.line(screen, cyan, p1_left, p2_left, 2)

        p1_right = project(points_right[i], 0.1)
        p2_right = project(points_right[(i + 1) % 4], 0.1)
        pygame.draw.line(screen, red, p1_right, p2_right, 2)

    if color == green:  # Fill the food square
        pygame.draw.rect(screen, green, (project(points_left[0], 0)[0], project(points_left[0], 0)[1], snake_size, snake_size))


# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP and snake_direction != (0, 1, 0):
                snake_direction = (0, -1, 0)
            elif event.key == K_DOWN and snake_direction != (0, -1, 0):
                snake_direction = (0, 1, 0)
            elif event.key == K_LEFT and snake_direction != (1, 0, 0):
                snake_direction = (-1, 0, 0)
            elif event.key == K_RIGHT and snake_direction != (-1, 0, 0):
                snake_direction = (1, 0, 0)

    # Move the snake
    new_head = (snake[0][0] + snake_direction[0] * snake_size,
                snake[0][1] + snake_direction[1] * snake_size,
                snake[0][2] + snake_direction[2] * snake_size)
    snake.insert(0, new_head)

    # Check for food collision
    if (new_head[0], new_head[1]) == (food[0], food[1]):
        food = (random.randint(0, width - snake_size), random.randint(0, height - snake_size), 0)
    else:
        snake.pop()

    # Check for game over (collision with walls or self)
    if (
        new_head[0] < 0
        or new_head[0] + snake_size > width
        or new_head[1] < 0
        or new_head[1] + snake_size > height
        or new_head in snake[1:]
    ):
        running = False

    # Draw everything
    screen.fill(black)
    for segment in snake:
        draw_square(segment[0], segment[1], segment[2], white)
    draw_square(food[0], food[1], food[2], green)

    pygame.display.flip()
    clock.tick(10)  # Control the game speed

pygame.quit()
