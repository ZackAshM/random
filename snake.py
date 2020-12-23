# It's 5am and I randomly decided to follow a youtube tutorial
# to build the snake game
# Link: https://www.youtube.com/watch?v=9bBgyOkoBQ0
# This will serve as my introduction to pygame and some of its
# structure
# I made some minor changes to penalize going offscreen,
# resetting the score, and preventing food from spawning in
# the snake

import pygame
import random
import sys

class snake_class(object):
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = (17, 24, 47)

    def get_head_position(self):
        return self.positions[0]

    def turn(self, point):
        # cannot u-turn for snake bigger than 1
        if self.length > 1 and (point[0] * -1, point[1] * -1) == self.direction:
            return
        else:
            self.direction = point

    def move(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = (((cur[0] + (x*GRIDSIZE)) % SCREEN_WIDTH),
               ((cur[1] + (y*GRIDSIZE)) % SCREEN_HEIGHT))
        if len(self.positions) > 2 and new in self.positions[2:]:
            self.reset()
        elif cur[0] == 0 and self.direction == LEFT:
            self.reset()
        elif cur[0] == (SCREEN_WIDTH-GRIDSIZE) and self.direction == RIGHT:
            self.reset()
        elif cur[1] == 0 and self.direction == UP:
            self.reset()
        elif cur[1] == (SCREEN_HEIGHT-GRIDSIZE) and self.direction == DOWN:
            self.reset()
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH / 2), (SCREEN_HEIGHT / 2))]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])

    def draw(self, surface):
        for p in self.positions:
            r = pygame.Rect((p[0], p[1]), (GRIDSIZE, GRIDSIZE))
            pygame.draw.rect(surface, self.color, r)
            pygame.draw.rect(surface, (93, 216, 228), r, 1) #outline

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.turn(UP)
                elif event.key == pygame.K_DOWN:
                    self.turn(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.turn(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.turn(RIGHT)

class food_class(object):
    def __init__(self):
        self.position = (0, 0)
        self.color = (223, 163, 49)

    def randomize_position(self, snake_pos):
        self.position = (random.randint(0, GRID_WIDTH-1) * GRIDSIZE,
                         random.randint(0, GRID_HEIGHT-1) * GRIDSIZE)
        if self.position in snake_pos:
            self.randomize_position(snake_pos)

    def draw(self, surface):
        r = pygame.Rect((self.position[0], self.position[1]), (GRIDSIZE, GRIDSIZE))
        pygame.draw.rect(surface, self.color, r)
        pygame.draw.rect(surface, (93, 216, 228), r, 1)

def drawGrid(surface):
    for y in range(0, int(GRID_HEIGHT)):
        for x in range(0, int(GRID_WIDTH)):
            if (x + y) % 2 == 0:
                # rect object ((pos), (size))
                r = pygame.Rect((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE))
                # draw (surface object, (r,g,b) colors, rect object)
                pygame.draw.rect(surface, (93, 216, 228), r)
            else:
                rr = pygame.Rect((x*GRIDSIZE, y*GRIDSIZE), (GRIDSIZE, GRIDSIZE))
                pygame.draw.rect(surface, (84, 194, 205), rr)
                

# global variables to define game features
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480

GRIDSIZE = 20
GRID_WIDTH = SCREEN_WIDTH / GRIDSIZE
GRID_HEIGHT = SCREEN_HEIGHT / GRIDSIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# the main game loop
def main():
    pygame.init()

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

    surface = pygame.Surface(screen.get_size())
    surface = surface.convert()
    drawGrid(surface)

    snake = snake_class()
    food = food_class()

    myfont = pygame.font.SysFont('monospace', 16)
    
    score = 0
    while True:
        clock.tick(10) #ticking at 10 fps
        snake.handle_keys()
        drawGrid(surface)
        if snake.length == 1:
            score = 0
        snake.move()
        if snake.get_head_position() == food.position:
            snake.length += 1
            score += 1
            food.randomize_position(snake.positions)
        snake.draw(surface)
        food.draw(surface)

        # refresh and update when action occurs
        screen.blit(surface, (0, 0))
        text = myfont.render("Score {0}".format(score), 1, (0, 0, 0))
        screen.blit(text, (5, 10))
        pygame.display.update()
    

main()
