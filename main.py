import pygame
from utils import scale_image

TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.5)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)

TRACK_BORDER = scale_image(pygame.image.load("imgs/border.png"), 0.5)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
FREE_CAR = scale_image(pygame.image.load("imgs/free-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

run = True
while run: 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

pygame.quit()