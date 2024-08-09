import pygame
from pygame.locals import *
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 600, 600
screen = pygame.display.set_mode((width, height), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption("3D Tic-Tac-Toe")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
cyan = (0, 255, 255)

# Game board
board = np.zeros((3, 3))

# 3D cross and circle shapes (vertices)
cross_vertices = [
    (-0.5, -0.2, 0), (0.5, -0.2, 0),
    (-0.5, 0.2, 0), (0.5, 0.2, 0),
    (-0.2, -0.5, 0), (0.2, -0.5, 0),
    (-0.2, 0.5, 0), (0.2, 0.5, 0),
    (0, 0, -0.3), (0, 0, 0.3)
]

circle_vertices = [
    (np.cos(theta), np.sin(theta), 0)
    for theta in np.linspace(0, 2 * np.pi, 30)
]

# Projection function (with anaglyph offset)
def project(vertex, eye_offset):
    x, y, z = vertex
    focal_length = 5
    x += eye_offset
    projected_x = int(x * focal_length / (z + focal_length) * 100 + width / 2)
    projected_y = int(y * focal_length / (z + focal_length) * 100 + height / 2)
    return projected_x, projected_y

# Draw functions
def draw_cross(x, y):
    for i in range(0, len(cross_vertices), 2):
        p1_left = project(cross_vertices[i], -0.1)
        p2_left = project(cross_vertices[i + 1], -0.1)
        pygame.draw.line(screen, cyan, p1_left, p2_left, 2)

        p1_right = project(cross_vertices[i], 0.1)
        p2_right = project(cross_vertices[i + 1], 0.1)
        pygame.draw.line(screen, red, p1_right, p2_right, 2)

def draw_circle(x, y):
    for i in range(len(circle_vertices) - 1):
        p1_left = project(circle_vertices[i], -0.1)
        p2_left = project(circle_vertices[i + 1], -0.1)
        pygame.draw.line(screen, cyan, p1_left, p2_left, 2)

        p1_right = project(circle_vertices[i], 0.1)
        p2_right = project(circle_vertices[i + 1], 0.1)
        pygame.draw.line(screen, red, p1_right, p2_right, 2)

# Game loop
running = True
player = 1  # 1 for X, -1 for O
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:  # Left mouse click
                mx, my = pygame.mouse.get_pos()
                i, j = int(my // (height / 3)), int(mx // (width / 3))
                if board[i][j] == 0:
                    board[i][j] = player
                    player *= -1

    # Draw the board
    screen.fill(black)
    for i in range(1, 3):
        pygame.draw.line(screen, white, (0, i * height / 3), (width, i * height / 3), 2)
        pygame.draw.line(screen, white, (i * width / 3, 0), (i * width / 3, height), 2)

    # Draw the X's and O's
    for i in range(3):
        for j in range(3):
            if board[i][j] == 1:
                draw_cross(j, i)
            elif board[i][j] == -1:
                draw_circle(j, i)

    pygame.display.flip()

pygame.quit()
