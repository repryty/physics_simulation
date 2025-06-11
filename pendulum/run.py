import pygame
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pendulum Simulation")

G = 10
T = 10

class Pendulum:
    def __init__(self, length, angle):
        self.length = length
        self.angle = angle
        self.x_position = 400+ length * math.sin(angle)
        self.y_position = 300+ length/2 + length * math.cos(angle)
        self.x_vector = 0
        self.y_vector = 0

    def update(self):
        # get angle
        self.angle = math.asin(abs(self.x_position-400)/self.length)
        # gravity
        self.y_vector -= G
        # tension
        self.y_vector += T
        

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  
    pygame.draw.line(screen, (0, 0, 0), (400, 300), (400, 200), 5)  # Draw the pendulum string
    pygame.draw.circle(screen, (0, 0, 255), (400, 300), 50)  # Draw a pendulum bob
    pygame.display.flip()

pygame.quit()