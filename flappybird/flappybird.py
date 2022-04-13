# I've again followed another tutorial, this time for building
# flappybird using pygame
# The youtube tutorial also gives a detailed explanation on
# the structure of game development, i.e. game loop, event loop, etc.

# Resources pulled from...
# https://github.com/samuelcust/flappy-bird-assets

# Takeaways:
# - Basic game structure
# - Drawing objects, importing images
# - Handling Collisions
# - Simple animation with transforms
# - Handling game vs gameover/start screen
# - Adding text/score
# - Implementing Sounds

import pygame, sys, random

# a function to draw the moving floor
def draw_floor():
    screen.blit(floor_surface, (floor_x_pos,450))
    screen.blit(floor_surface, (floor_x_pos+288,450))

# a function to spawn pipes
def create_pipe():
    random_pipe_pos = random.choice(pipe_heights)
    bottom_pipe = pipe_surface.get_rect(midtop=(310,random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midbottom=(310, random_pipe_pos-150))
    return bottom_pipe, top_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 2
    return pipes

def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 512: # if bottom pipe
            screen.blit(pipe_surface,pipe)
        else: # top pipe
            # flip(surface, x_bool, y_bool)
            flip_pipe = pygame.transform.flip(pipe_surface,False,True)
            screen.blit(flip_pipe,pipe)

# handle collisions
def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            death_sound.play()
            return False

    if bird_rect.top <= -100 or bird_rect.bottom >= 450:
        death_sound.play()
        return False
    
    # if no collisions...
    return True

# functions to animate bird
def rotate_bird(bird):
    # rotozoom(surface,angle,scale)
    new_bird = pygame.transform.rotozoom(bird,-bird_velocity*3,1)
    return new_bird

def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(50,bird_rect.centery))
    return new_bird,new_bird_rect

# functions to handle score
def score_display(game_state):
    if game_state == 'main_game':
        score_surface = game_font.render(str(score),False,(255,255,255))
        score_rect = score_surface.get_rect(center=(144,50))
        screen.blit(score_surface,score_rect)
    elif game_state == 'game_over':
        score_surface = game_font.render(str(score),False,(255,255,255))
        score_rect = score_surface.get_rect(center=(144,50))
        screen.blit(score_surface,score_rect)

        highscore_text = "best: " + str(high_score)
        highscore_surface = game_font.render(highscore_text,False,(255,255,255))
        highscore_rect = highscore_surface.get_rect(center=(144,425))
        screen.blit(highscore_surface,highscore_rect)

def update_score(pipes,score,high_score):
    for pipe in pipes:
        if bird_rect.centerx == pipe.centerx:
            score_sound.play()
            new_score = score + 1
            new_highscore = new_score if new_score > high_score else high_score
            return new_score, new_highscore
    return score, high_score


# initiate the sound mixer in a specific way
pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pygame.init()
screen = pygame.display.set_mode((288, 512))
clock = pygame.time.Clock()
game_font = pygame.font.Font('assets/04B_19.TTF',40)

# game variables
gravity = 0.25
bird_velocity = 0
game_active = False # False when gameover or start
score = 0
high_score = 0

# note: .convert converts the image to something easier for pygame
bg_surface = pygame.image.load('assets/sprites/background-day.png').convert()
# scale 2x in tutorial, but we'll use original
# bg_surface = pygame.transform.scale2x(bg_surface) 

floor_surface = pygame.image.load('assets/sprites/base.png').convert()
floor_x_pos = 0

bird_downflap = pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
bird_midflap = pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha()
bird_upflap = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(50,256))

BIRDFLAP = pygame.USEREVENT # define a new event type
pygame.time.set_timer(BIRDFLAP,200) # flap every 200ms

# for simple non animated bird
# bird_surface = pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha()
# # convert_alpha to remove black surface from rotation
# bird_rect = bird_surface.get_rect(center=(50,256))

pipe_surface = pygame.image.load('assets/sprites/pipe-green.png').convert()
pipe_list = []
SPAWNPIPE = pygame.USEREVENT + 1 # define an additional new event type
pygame.time.set_timer(SPAWNPIPE,2000) # trigger event every 2s
pipe_heights = [200, 300, 400]

gameover_surface = pygame.image.load('assets/sprites/message.png').convert_alpha()
gameover_rect = gameover_surface.get_rect(center=(144,256))

# sounds
flap_sound = pygame.mixer.Sound('assets/audio/wing.wav')
death_sound = pygame.mixer.Sound('assets/audio/hit.wav')
score_sound = pygame.mixer.Sound('assets/audio/point.wav')

# the main game loop
while True:
    for event in pygame.event.get(): # the event loop
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_SPACE) and game_active:
                bird_velocity = 0   # reset velocity
                bird_velocity -= 6 # jump
                flap_sound.play()
            if (event.key == pygame.K_SPACE) and (game_active == False):
                game_active = True
                pipe_list.clear()
                bird_rect.center = (50,256)
                bird_velocity = -6
                score = 0
                flap_sound.play()
        if event.type == SPAWNPIPE:
            pipe_list.extend(create_pipe())
        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0

            bird_surface,bird_rect = bird_animation()

    # blit puts one surface onto another surface
    # note: (0,0) is the top-left of the screen
    # the position of objects is also their top-left
    screen.blit(bg_surface, (0,0))

    if game_active:
        # bird
        bird_velocity += gravity
        rotated_bird = rotate_bird(bird_surface)
        bird_rect.centery += bird_velocity
        screen.blit(rotated_bird,bird_rect)
        game_active = check_collision(pipe_list)

        # pipes
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        # Score
        score_display('main_game')
        score, high_score = update_score(pipe_list,score,high_score)
    else:
        screen.blit(gameover_surface,gameover_rect)
        score_display('game_over')
    
    # floor
    floor_x_pos -= 1
    draw_floor()
    if floor_x_pos <= -288:
        floor_x_pos = 0
            
    pygame.display.update()
    clock.tick(60)
