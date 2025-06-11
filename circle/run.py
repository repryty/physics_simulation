import pygame
import math
import time

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Pendulum Simulation")

font = pygame.font.Font("Pretendard-Regular.otf", 20)

G = 5
T = 5.3

LENGTH = 100
INIT_ANGLE = math.radians(-30)

class Pendulum:
    def __init__(self, length, angle):
        self.length = length
        self.angle = angle
        self.x_position = 400 + length * math.sin(angle)
        self.y_position = 300 - length/2 + length * math.cos(angle)
        self.x_vector = 0
        self.y_vector = 0

    def update(self):
        # get angle
        self.angle = math.asin((self.x_position-400)/self.length)
        # gravity
        self.y_vector += G
        # tension
        self.x_vector += T * math.sin(self.angle)
        self.y_vector -= T * math.cos(self.angle)

        # step

        self.x_position-=self.x_vector
        self.y_position+=self.y_vector


pendulum = Pendulum(LENGTH, INIT_ANGLE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pendulum.update()

    screen.fill((255, 255, 255))  
    pygame.draw.line(screen, (0, 0, 0), (400, 300-LENGTH/2), (pendulum.x_position, pendulum.y_position), 5) 
    pygame.draw.circle(screen, (0, 0, 255), (pendulum.x_position, pendulum.y_position), 20)

    text_surface = font.render(f"X: {pendulum.x_position}, Y: {pendulum.y_position}, ANGLE: {math.degrees(pendulum.angle)}", True, (0,0,0))
    screen.blit(text_surface, (0, 0))

    pygame.display.flip()

    time.sleep(0.1)

pygame.quit()