import pygame
import time
import math
from utils import scale_image

TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.5)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)

TRACK_BORDER = scale_image(pygame.image.load("imgs/border.png"), 0.5)
FINISH = pygame.image.load("imgs/finish.png")

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
FREE_CAR = scale_image(pygame.image.load("imgs/free-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

run = True
clock = pygame.time.Clock()

while run: 
    clock.tick(FPS)
    
    WIN.blit(GRASS, (0, 0))
    WIN.blit(TRACK, (0, 0))
    WIN.blit(FINISH, (0, 0))
    
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

pygame.quit()