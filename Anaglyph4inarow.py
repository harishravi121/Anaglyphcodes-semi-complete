import pygame
from pygame.locals import *
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption("3D Four in a Row")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
cyan = (0, 255, 255)

# Game board (6 rows, 7 columns)
board = np.zeros((6, 7))

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

# Function to check for a win
def check_win(board, player):
    # Check horizontal
    for row in range(6):
        for col in range(4):
            if all(board[row, col + i] == player for i in range(4)):
                return True

    # Check vertical
    for row in range(3):
        for col in range(7):
            if all(board[row + i, col] == player for i in range(4)):
                return True

    # Check diagonals (positive slope)
    for row in range(3):
        for col in range(4):
            if all(board[row + i, col + i] == player for i in range(4)):
                return True

    # Check diagonals (negative slope)
    for row in range(3):
        for col in range(3, 7):
            if all(board[row + i, col - i] == player for i in range(4)):
                return True

    return False

# Game loop
running = True
player = 1  # 1 for X, -1 for O
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and not game_over:
            if pygame.mouse.get_pressed()[0]:  # Left mouse click
                mx, my = pygame.mouse.get_pos()
                col = int(mx // (width / 7))
                # Find the lowest empty row in the column
                for row in range(5, -1, -1):
                    if board[row][col] == 0:
                        board[row][col] = player
                        if check_win(board, player):
                            game_over = True
                            print(f"Player {player} wins!")
                        player *= -1
                        break

    # Draw the board
    screen.fill(black)
    for i in range(1, 6):
        pygame.draw.line(screen, white, (0, i * height / 6), (width, i * height / 6), 2)
    for i in range(1, 7):
        pygame.draw.line(screen, white, (i * width / 7, 0), (i * width / 7, height), 2)

    # Draw the X's and O's
    for row in range(6):
        for col in range(7):
            if board[row][col] == 1:
                draw_cross(col, row)
            elif board[row][col] == -1:
                draw_circle(col, row)

    pygame.display.flip()

pygame.quit()
