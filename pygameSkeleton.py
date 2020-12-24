# The general skeleton for most games developed with pygame
# This follows a YouTube tutorial in the beginning of the
# flappybird tutorial
# Link: https://www.youtube.com/watch?v=UZg49z76cLw

import pygame, sys

# the game begins with this code
pygame.init()

# create the display surface, conventionally denoted 'screen'
screen = pygame.display.set_mode((576, 1024))

# a clock object to control the update speed
clock = pygame.time.Clock()


# the main game loop
while True:
    for event in pygame.event.get(): # the event loop
        if event.type == pygame.QUIT:
            # quit the game (does not quit code, so also sys.exit)
            pygame.quit()
            sys.exit()

    # update the display
    pygame.display.update()

    # control the game frame rate
    clock.tick(120)
