# DQN to have an AI learn and play our FlappyBird

import numpy as np
import random

import tensorflow as tf
import tensorflow.keras.layers as kl
import tensorflow.keras.optimizers as ko

from pygame import KEYDOWN, K_SPACE, event
from flappybirdv2 import FlappyBird

seed = 1
np.random.seed(seed)
tf.random.set_seed(seed)

class Model(tf.keras.Model):
    def __init__(self, num_actions):
        super().__init__(name='basic_dqn')
        # 2 hidden layers and the output layer
        self.fc1 = kl.Dense(32, activation='relu', kernel_initializer='he_uniform')
        self.fc2 = kl.Dense(32, activation='relu', kernel_initializer='he_uniform')
        self.logits = kl.Dense(num_actions, name='q_values')

    # forward propagation
    def call(self, inputs):
        x = self.fc1(inputs)
        x = self.fc2(x)
        x = self.logits(x)
        return x

    # a* = argmax_a' Q(s, a')
    def action_value(self, obs):
        q_values = self.predict(obs)
        best_action = np.argmax(q_values, axis=-1)
        return best_action[0], q_values[0]

class FlappyAI(FlappyBird):
    def __init__(self, model, target_model, buffer_size=100, learning_rate=.0015, epsilon=.1,
                 gamma=.95, batch_size=4, target_update_iter=400, train_nums=5000, start_learning=10):
        super().__init__()
        self.JUMP = event.Event(KEYDOWN, key=K_SPACE)

        # model
        self.model = model
        self.target_model = target_model
        opt = ko.Adam(learning_rate=learning_rate, clipvalue=10.0)
        self.model.compile(optimizer=opt, loss='mse')

        # parameters
        self.lr = learning_rate                     # learning step
        self.epsilon = epsilon                      # e-greedy when exploring
        self.gamma = gamma                          # discount rate
        self.batch_size = batch_size                # batch_size
        self.target_update_iter = target_update_iter    # target network update period
        self.train_nums = train_nums                # total training steps
        self.num_in_buffer = 0                      # transition's num in buffer
        self.buffer_size = buffer_size              # replay buffer size
        self.start_learning = start_learning        # step to begin learning(no update before that step)

        # replay buffer params [(s, a, r, ns, done), ...]
        self.obs = np.empty((self.buffer_size,) + self.state.shape)
        self.actions = np.empty((self.buffer_size), dtype=np.int8)
        self.rewards = np.empty((self.buffer_size), dtype=np.float32)
        self.dones = np.empty((self.buffer_size), dtype=np.bool)
        self.next_states = np.empty((self.buffer_size,) + self.state.shape)
        self.next_idx = 0

    @property
    def state(self):
        '''Returns velocity, bird position, and position of middle of next two pipes'''
        observation = []
        try:
            bird_y = self.bird_rect.center[1]
            observation.append(round(self.bird_velocity, 2))
            observation.append(bird_y)
            
            pipes = self.pipe_list
            if len(pipes) >= 2:
                pipe1, pipe2 = pipes[0], pipes[1]
                pipe_x, pipe1_y = pipe1.midtop if pipe1.bottom >= 512 else pipe1.midbottom
                _, pipe2_y = pipe2.midtop if pipe2.bottom >= 512 else pipe2.midbottom
                pipe_y = int((pipe1_y + pipe2_y) / 2)
                observation.append(pipe_x)
                observation.append(pipe_y)
        except AttributeError:
            pass

        # no pipes -> -1 positions
        while len(observation) < 4:
            observation.append(-1)
        
        return np.array(observation)

    def train(self):
        # initialize the initial observation of the agent
        obs = self.state
        for t in range(1, self.train_nums):
            best_action, q_values = self.model.action_value(obs[None])  # input the obs to the network model
            action = self.get_action(best_action)   # get the real action
            if best_action == 1:
                event.post(self.JUMP)
            self.step()
            next_obs, reward, done = self.state, self.reward, not self.game_active    # take the action in the env to return s', r, done
            self.store_transition(obs, action, reward, next_obs, done)  # store that transition into replay butter
            self.num_in_buffer = min(self.num_in_buffer + 1, self.buffer_size)

            if t > self.start_learning:  # start learning
                losses = self.train_step()
                if t % 1000 == 0:
                    print('losses each 1000 steps: ', losses)

            if t % self.target_update_iter == 0:
                self.update_target_model()
            if done:
                self.reset()
                self.game_active = True
                obs = self.state
            else:
                obs = next_obs

    # e-greedy
    def get_action(self, best_action):
        if np.random.rand() < self.epsilon:
            return np.random.choice(2, 1)
        return best_action

    # store transitions into replay butter
    def store_transition(self, obs, action, reward, next_state, done):
        n_idx = self.next_idx % self.buffer_size
        self.obs[n_idx] = obs
        self.actions[n_idx] = action
        self.rewards[n_idx] = reward
        self.next_states[n_idx] = next_state
        self.dones[n_idx] = done
        self.next_idx = (self.next_idx + 1) % self.buffer_size

    def train_step(self):
        idxes = self.sample(self.batch_size)
        s_batch = self.obs[idxes]
        a_batch = self.actions[idxes]
        r_batch = self.rewards[idxes]
        ns_batch = self.next_states[idxes]
        done_batch = self.dones[idxes]

        target_q = r_batch + self.gamma * np.amax(self.get_target_value(ns_batch), axis=1) * (1 - done_batch)
        target_f = self.model.predict(s_batch)
        for i, val in enumerate(a_batch):
            target_f[i][val] = target_q[i]

        losses = self.model.train_on_batch(s_batch, target_f)

        return losses

    # sample n different indexes
    def sample(self, n):
        assert n < self.num_in_buffer
        res = []
        while True:
            num = np.random.randint(0, self.num_in_buffer)
            if num not in res:
                res.append(num)
            if len(res) == n:
                break
        return res

    # assign the current network parameters to target network
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def play(self):
        self.game_active = True
        obs, done, ep_reward = self.state, not self.game_active, 0
        # one episode until done
        while not done:
            action, q_values = self.model.action_value(obs[None])  # Using [None] to extend its dimension (4,) -> (1, 4)
            if action == 1:
                event.post(self.JUMP)
            self.step()
            obs, reward, done = self.state, self.reward, not self.game_active
            ep_reward += reward
        return ep_reward

    def get_target_value(self, obs):
        return self.target_model.predict(obs)
    
if __name__ == "__main__":
    num_actions = 2
    model = Model(num_actions)
    target_model = Model(num_actions)
    
    game = FlappyAI(model, target_model)
    game.start()
    game.game_active = True

    # test before
    # rewards_sum = game.play()
    # print("Before Training: score of %d" % rewards_sum) # 9 out of 200

    # training
    game.train()
