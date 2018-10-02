import math
import os
import random
import sys
import numpy as np
import pygame
from pygame.locals import *

www = (10, 40)
os.environ['SDL_VIDEO_WINDOW_POS'] = str(www[0]) + "," + str(www[1])
pygame.init()
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 200, 0)

# set the window
size = width, height = 500, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
gameIcon = pygame.image.load('images/intruder.png')
pygame.display.set_icon(gameIcon)
pygame.display.set_caption('Aircraft Guidance Simulator', 'Spine Runtime')

no_frame = 1  # one action can last how many frames or time steps?
tick = 30  # update no more than 30 frames in one second
np.set_printoptions(precision=2)


# display the time step at top right corner
def time_display(count):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("time step: " + str(count), True, black)
    screen.blit(text, (5, 0))


# display how many times the ownship flies out of map at top right corner
def collision_wall(count):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("Out of Map: " + str(count), True, black)
    screen.blit(text, (5, 25))


# display how many goals reached at top right corner
def reach_goal(count):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("Goal: " + str(count), True, green)
    screen.blit(text, (5, 50))


def reward_display(reward):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("Cum Reward: " + str(reward), True, green)
    screen.blit(text, (5, 75))


# the aircraft object
class DroneSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load('images/drone.png')
        self.rect = self.src_image.get_rect()
        self.image = self.src_image  # initial position
        self.position = (width-50, height-50)
        self.speed = 2  # speed of the ownship is 2 pixel per time step
        self.direction = 45
        self.rad = self.direction * math.pi / 180
        # velocity (v_x, v_y) can be decided from the speed scalar and heading angle
        self.vx = -self.speed * math.sin(self.rad)
        self.vy = -self.speed * math.cos(self.rad)
        self.velocity = (self.vx, self.vy)
        # this aircraft will be safe if other aircraft are outside this radius
        self.radius = 16
        # the heading angle will be updated according to this delta_direction.
        self.delta_direction = 0
        # use keyboard to control left or right
        self.k_right = 0
        self.k_left = 0

        # number of out of maps, reached goals, cumulative reward
        self.collision_wall = 0
        self.reach_goal = 0
        self.cumulative_reward = 0

    def update(self, deltat):
        # decide the new heading angle according to the action: self.delta_direction
        self.delta_direction = self.k_right + self.k_left
        self.direction += self.delta_direction
        self.direction %= 360  # keep it between (0, 360)
        self.rad = self.direction * math.pi / 180  # turn deg to rad

        # decide the new velocity according to the heading angle
        vx = -self.speed * math.sin(self.rad)
        vy = -self.speed * math.cos(self.rad)
        self.velocity = (vx, vy)

        # decide the new position according to the velocity
        x = self.position[0] + vx
        y = self.position[1] + vy
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position


# the goal sprite for the ownship
class GoalSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/goal.png')
        self.rect = self.image.get_rect()
        self.position = position
        self.radius = 16
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def update(self):
        self.rect.center = self.position


# get the state vector according to current aircraft position, velocity and goal position
# own is the ownship we are controlling
# goal is the goal sprite
def get_state(own, goal):
    state_list = []

    state_list.append(own.position[0])
    state_list.append(own.position[1])
    state_list.append(own.velocity[0])
    state_list.append(own.velocity[1])
    state_list.append(own.direction)
    state_list.append(goal.position[0])
    state_list.append(goal.position[1])

    return np.array(state_list)


# generate a goal position
goal = GoalSprite((random.random() * width,
                   random.random() * height))


# drone is the ownship we are controlling
drone = DroneSprite()
drone_group = pygame.sprite.RenderPlain(drone)
goal_group = pygame.sprite.RenderPlain(goal)


time_step = -1  # this is the time step displayed at the top right corner.
simulate = True

while simulate:
    # while simulating, you can press esc to exit the pygame window
    time_step += 1

    current_state = get_state(drone, goal)

    # there can plug in some algorithms, input is current_state, output is action
    # action should be turn left for 2 deg, go straight, turn right for 2 deg
    # action = policy(current_state)
    # drone.delta_direction = action

    # use key board left and right to control the ownship
    for event in pygame.event.get():
        if not hasattr(event, 'key'):
            continue
        down = event.type == KEYDOWN
        if event.key == K_RIGHT:
            drone.k_right = down * -2
        elif event.key == K_LEFT:
            drone.k_left = down * 2
        elif event.key == K_ESCAPE:
            sys.exit(0)

    # the simulator will run many frames for one action
    for _ in range(no_frame):
        deltat = clock.tick(tick)
        screen.fill((255, 255, 255))

        # check if the ownship flies out of the map
        if drone.position[0] < 8 or drone.position[0] > width - 8 \
                or drone.position[1] < 8 or drone.position[1] > height - 8:
            # collide with walls
            drone.cumulative_reward += -100
            drone.collision_wall += 1
            drone.position = (width-50, height-50)
            drone.direction = 45

        # check if the ownship reaches the goal state.
        if pygame.sprite.collide_circle(drone, goal):
            # the ownship reaches the goal position
            collide_goal = True
            drone.reach_goal += 1

            # generate a new goal for the aircraft
            goal.position = (random.random() * width,
                             random.random() * height)

            drone.cumulative_reward += 500
            # simulate = False

        # update the drone, goal
        drone_group.update(deltat)
        goal_group.update()

        # draw the aircraft and the goal
        drone_group.draw(screen)
        goal_group.draw(screen)

        time_display(time_step)
        collision_wall(drone.collision_wall)
        reach_goal(drone.reach_goal)
        reward_display(drone.cumulative_reward)

        pygame.display.flip()

        drone.cumulative_reward += -1
