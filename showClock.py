import pygame, sys
from pygame.locals import *
import random
import time

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

#Setting up FPS
FPS = 60
FramePerSec = pygame.time.Clock()

#Creating colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Other Variables for use in the program
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0

#Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

background = pygame.image.load("img/big/easteregg.png")

#Create a white screen
DISPLAYSURF = pygame.display.set_mode((400,600))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")


# Fonts
fontpath = pygame.font.match_font('dejavusansmono')
fontS2 = pygame.font.Font(fontpath, 28)
fontSm = pygame.font.Font(fontpath, 18)


# see a clock with secounds, just call it in loop or as many times as you need it, after it clear the screen !
def showClock():
    # clear screen and update
    DISPLAYSURF.fill(BLACK)
    pygame.display.update()

    # show the clock @ (10,260), uodate the screen and wait 1 second
    updated = time.strftime("%Y-%m-%d %H:%M:%S")
    text_surface = fontS2.render(updated, True, WHITE)
    DISPLAYSURF.blit(text_surface, (10, 320))
    pygame.display.update()
    time.sleep(1)



#Adding a new User event
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

#Game Loop
while True:

    #Cycles through all events occurring
    for event in pygame.event.get():
        if event.type == INC_SPEED:
              SPEED += 0.5
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    DISPLAYSURF.blit(background, (0,0))
    scores = font_small.render(str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10,10))

    showClock()

    #Moves and Re-draws all Sprites
    #for entity in all_sprites:
    #    DISPLAYSURF.blit(entity.image, entity.rect)
    #    entity.move()


    pygame.display.update()
    FramePerSec.tick(FPS)
