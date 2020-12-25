# cleaning up the first flappybird code,
# so... it's now my organization rather than the tutorial's
# Edits also made for easier use to train an AI to play (observations)

import pygame, sys, random

class FlappyBird:
    def __init__(self, observe=False):
        self.size = (288, 512)
        self.score = 0
        self.high_score = 0
        self.gravity = 0.3
        self.pipe_gap = 150
        self.game_active = False # False when start or gameover
        self.framerate = 60
        self.observe = observe

    def get_observation(self):
        '''Returns distances to next two pipes (mid open edge)'''
        observation = []
        bird_x, bird_y = self.bird_rect.center
        for pipe in self.pipe_list:
            if pipe.bottom >= 512:
                pipe_x, pipe_y = pipe.midtop
            else:
                pipe_x, pipe_y = pipe.midbottom
            dx = pipe_x - bird_x
            if (dx > 0) and (len(observation) < 2):
                dy = pipe_y - bird_y
                dist = (dx**2 + dy**2)**0.5 / self.pipe_gap # normalized to pipe gap
                observation.append(dist)
        while len(observation) < 2:
            observation.append(-1)
        return observation
    
    def start(self):
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
        pygame.init()

        # sounds
        flap_sound = pygame.mixer.Sound('assets/audio/wing.wav')
        death_sound = pygame.mixer.Sound('assets/audio/hit.wav')
        score_sound = pygame.mixer.Sound('assets/audio/point.wav')
        self.sounds = {
            'flap':flap_sound,
            'death':death_sound,
            'score':score_sound
        }

        # game properties
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.game_font = pygame.font.Font('assets/04B_19.TTF',40)

        # initialize game objects
        self.bg_init()
        self.title_init()
        self.bird_init()
        self.pipes_init()

        if self.observe:
            self.observation = self.get_observation() 

    def bg_init(self):
        self.bg_surface = pygame.image.load('assets/sprites/background-day.png').convert()
        
        self.floor_surface = pygame.image.load('assets/sprites/base.png').convert()
        self.floor_x_pos = 0
    
    def title_init(self):
        self.title_surface = pygame.image.load('assets/sprites/message.png').convert_alpha()
        self.title_rect = self.title_surface.get_rect(center=(144,256))

    def bird_init(self):
        bird_downflap = pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()
        bird_midflap = pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha()
        bird_upflap = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.bird_frames = [bird_downflap, bird_midflap, bird_upflap]
        self.bird_index = 0
        self.bird_surface = self.bird_frames[self.bird_index]
        self.bird_rect = self.bird_surface.get_rect(center=(50,256))

        self.bird_velocity = 0

        self.BIRDFLAP = pygame.USEREVENT # define a new event type
        pygame.time.set_timer(self.BIRDFLAP, 200) # flap every 200ms

    def pipes_init(self):
        self.pipe_surface = pygame.image.load('assets/sprites/pipe-green.png').convert()
        
        self.pipe_list = []
        self.pipe_heights = [200, 300, 400]
        
        self.SPAWNPIPE = pygame.USEREVENT + 1
        self.pipe_spawnrate = int(60*2000 / self.framerate)
        pygame.time.set_timer(self.SPAWNPIPE, self.pipe_spawnrate)

        # self.PRINT_LIST = pygame.USEREVENT + 2
        # pygame.time.set_timer(self.PRINT_LIST, 500)

    # animation functions
    def draw_floor(self):
        self.floor_x_pos -= 1
        self.screen.blit(self.floor_surface, (self.floor_x_pos,450))
        self.screen.blit(self.floor_surface, (self.floor_x_pos+288,450)) # extends image for scrolling
        if self.floor_x_pos <= -288:
            self.floor_x_pos = 0

    def create_pipes(self):
        random_pipe_pos = random.choice(self.pipe_heights)
        bottom_pipe = self.pipe_surface.get_rect(midtop=(310, random_pipe_pos))
        top_pipe = self.pipe_surface.get_rect(midbottom=(310, random_pipe_pos-self.pipe_gap))
        return bottom_pipe, top_pipe

    def draw_pipes(self):
        for pipe in self.pipe_list:
            pipe.centerx -= 2
            if pipe.bottom >= 512:
                self.screen.blit(self.pipe_surface, pipe)
            else:
                flip_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.screen.blit(flip_pipe, pipe)

    def rotate_bird(self):
        new_bird = pygame.transform.rotozoom(self.bird_surface, -3*self.bird_velocity, 1)
        return new_bird

    def bird_animation(self):
        new_bird = self.bird_frames[self.bird_index]
        new_bird_rect = new_bird.get_rect(center=(50, self.bird_rect.centery))
        return new_bird, new_bird_rect

    # gameplay functions
    def check_collision(self):
        for pipe in self.pipe_list:
            if self.bird_rect.colliderect(pipe):
                self.pipe_list.clear()
                self.sounds['death'].play()
                return False

        if self.bird_rect.top <= -100 or self.bird_rect.bottom >= 450:
            self.pipe_list.clear()
            self.sounds['death'].play()
            return False

        return True

    def score_display(self, game_state):
        if game_state == 'main_game':
            score_surface = self.game_font.render(str(self.score),False,(255,255,255))
            score_rect = score_surface.get_rect(center=(144,50))
            self.screen.blit(score_surface, score_rect)
        elif game_state == 'title':
            score_surface = self.game_font.render(str(self.score),False,(255,255,255))
            score_rect = score_surface.get_rect(center=(144,50))
            self.screen.blit(score_surface, score_rect)

            highscore_text = "best: " + str(self.high_score)
            highscore_surface = self.game_font.render(highscore_text,False,(255,255,255))
            highscore_rect = highscore_surface.get_rect(center=(144,425))
            self.screen.blit(highscore_surface, highscore_rect)

    def update_score(self):
        for pipe in self.pipe_list:
            if self.bird_rect.centerx == pipe.centerx:
                self.sounds['score'].play()
                new_score = self.score + 1
                new_highscore = new_score if new_score > self.high_score else self.high_score
                return new_score, new_highscore
        return self.score, self.high_score

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE) and self.game_active:
                    self.bird_velocity = 0   # reset velocity
                    self.bird_velocity -= 6  # jump
                    self.sounds['flap'].play()
                if (event.key == pygame.K_SPACE) and (self.game_active == False):
                    self.game_active = True
                    self.pipe_list.clear()
                    pygame.time.set_timer(self.SPAWNPIPE, self.pipe_spawnrate)
                    self.bird_rect.center = (50,256)
                    self.bird_velocity = -6
                    self.score = 0
                    self.sounds['flap'].play()
                    
            if event.type == self.SPAWNPIPE:
                self.pipe_list.extend(self.create_pipes())

            # if event.type == self.PRINT_LIST:
            #     print(self.pipe_list)

            if event.type == self.BIRDFLAP:
                if self.bird_index < 2:
                    self.bird_index += 1
                else:
                    self.bird_index = 0
                self.bird_surface, self.bird_rect = self.bird_animation()

    def step(self):
        self.check_events()
        self.screen.blit(self.bg_surface, (0,0))
        
        if self.game_active:
            self.bird_velocity += self.gravity
            self.rotated_bird = self.rotate_bird()
            self.bird_rect.centery += self.bird_velocity
            self.screen.blit(self.rotated_bird, self.bird_rect)
            self.game_active = self.check_collision()

            if len(self.pipe_list) > 4:
                self.pipe_list = self.pipe_list[-4::]
            self.draw_pipes()

            self.score_display('main_game')
            self.score, self.high_score = self.update_score()

            if self.observe:
                self.observation = self.get_observation()
        else:
            pygame.time.set_timer(self.SPAWNPIPE, 0)
            self.screen.blit(self.title_surface,self.title_rect)
            self.score_display('title')

        self.draw_floor()
        pygame.display.update()
        self.clock.tick(self.framerate)

if __name__ == "__main__":
    game = FlappyBird(observe=True)
    game.start()
    # i = 0
    while True:
        # i+=1
        game.step()
        # if i % 50 == 0:
        #     print(game.observation)
