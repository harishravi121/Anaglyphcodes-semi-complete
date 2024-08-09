import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 600, 400
screen = pygame.display.set_mode((width, height), DOUBLEBUF | HWSURFACE)
pygame.display.set_caption("3D Pac-Man")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
cyan = (0, 255, 255)
yellow = (255, 255, 0)

# Pac-Man properties
pacman_size = 20
pacman_pos = [width / 2, height / 2, 0]
pacman_direction = (1, 0, 0)

# Pellets
pellets = []
for i in range(100):
    pellets.append((random.randint(0, width - 10), random.randint(0, height - 10), 0))

# Projection function (with anaglyph offset)
def project(vertex, eye_offset):
    x, y, z = vertex
    focal_length = 5
    x += eye_offset
    projected_x = int(x * focal_length / (z + focal_length) * 50 + width / 2)
    projected_y = int(y * focal_length / (z + focal_length) * 50 + height / 2)
    return projected_x, projected_y

# Draw functions
def draw_circle(x, y, z, radius, color):
    points_left = []
    points_right = []
    for angle in range(0, 360, 10):
        angle_rad = angle * 3.14159 / 180
        px = x + radius * np.cos(angle_rad)
        py = y + radius * np.sin(angle_rad)
        points_left.append((px, py, z))
        points_right.append((px, py, z + 0.2))

    for i in range(len(points_left)):
        p1_left = project(points_left[i], -0.1)
        p2_left = project(points_left[(i + 1) % len(points_left)], -0.1)
        pygame.draw.line(screen, cyan, p1_left, p2_left, 2)

        p1_right = project(points_right[i], 0.1)
        p2_right = project(points_right[(i + 1) % len(points_right)], 0.1)
        pygame.draw.line(screen, red, p1_right, p2_right, 2)

def draw_pellet(x, y, z):
    pygame.draw.circle(screen, yellow, project((x, y, z), 0), 3)

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                pacman_direction = (0, -1, 0)
            elif event.key == K_DOWN:
                pacman_direction = (0, 1, 0)
            elif event.key == K_LEFT:
                pacman_direction = (-1, 0, 0)
            elif event.key == K_RIGHT:
                pacman_direction = (1, 0, 0)

    # Move Pac-Man
    pacman_pos[0] += pacman_direction[0] * 3
    pacman_pos[1] += pacman_direction[1] * 3

    # Wall collisions (simple wrap-around for now)
    if pacman_pos[0] < 0:
        pacman_pos[0] = width
    elif pacman_pos[0] > width:
        pacman_pos[0] = 0
    if pacman_pos[1] < 0:
        pacman_pos[1] = height
    elif pacman_pos[1] > height:
        pacman_pos[1] = 0

    # Pellet collision
    for pellet in pellets[:]:  # Iterate over a copy to allow removal
        if (abs(pacman_pos[0] - pellet[0]) < pacman_size / 2 and
            abs(pacman_pos[1] - pellet[1]) < pacman_size / 2):
            pellets.remove(pellet)

    # Draw everything
    screen.fill(black)
    draw_circle(pacman_pos[0], pacman_pos[1], pacman_pos[2], pacman_size / 2, yellow)
    for pellet in pellets:
        draw_pellet(pellet[0], pellet[1], pellet[2])

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
