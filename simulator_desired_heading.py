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
size = width, height = 500, 500  # window size
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
gameIcon = pygame.image.load('images/intruder.png')
pygame.display.set_icon(gameIcon)
pygame.display.set_caption('Aircraft Guidance Simulator', 'Spine Runtime')

HEADING_CHANGE_RATE = 2  # parameter: how much degrees the drone can turn at each time step
tick = 30  # update no more than 30 frames in one second
np.set_printoptions(precision=2)


# display the time step at top right corner
def time_display(count):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("Time Step: " + str(count), True, black)
    screen.blit(text, (5, 0))


def reward_display(reward):
    font = pygame.font.SysFont("comicsansms", 20)
    text = font.render("Cum Reward: " + str(reward), True, green)
    screen.blit(text, (5, 25))


# the aircraft object
class DroneSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load('images/drone.png')
        self.rect = self.src_image.get_rect()
        self.image = self.src_image
        self.position = (width-50, height-50)  # initial position
        self.speed = 2  # speed of the ownship is 2 pixel per time step
        self.direction = 45
        self.rad = math.radians(self.direction)
        # velocity (v_x, v_y) can be decided from the speed scalar and heading angle
        self.vx = -self.speed * math.sin(self.rad)
        self.vy = -self.speed * math.cos(self.rad)
        self.velocity = (self.vx, self.vy)
        # this aircraft will be safe if other aircraft are outside this radius
        self.radius = 16
        # the heading angle will be updated according to this delta_direction.
        self.desired_direction = self.direction

        # cumulative reward of ownship
        self.cumulative_reward = 0

    def update(self, deltat):
        if self.desired_direction > self.direction + 2:
            self.direction += HEADING_CHANGE_RATE
        elif self.desired_direction > self.direction:
            self.direction = self.desired_direction
        elif self.desired_direction < self.direction - 2:
            self.direction -= HEADING_CHANGE_RATE
        elif self.desired_direction < self.direction:
            self.direction = self.desired_direction

        self.direction %= 360  # keep it between (0, 360)
        self.rad = math.radians(self.direction)  # turn deg to rad

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


# the distance between object a and object b based on their current position
def dist(a, b):
    dx = a.position[0] - b.position[0]
    dy = a.position[1] - b.position[1]
    return math.sqrt(dx * dx + dy * dy)


# get the state vector according to current aircraft position, velocity and goal position
# own is the ownship we are controlling
# goal is the goal sprite
def get_state(own, goal):
    state_list = [own.position[0], own.position[1], own.velocity[0], own.velocity[1], own.direction, goal.position[0],
                  goal.position[1]]

    return np.array(state_list)


# generate a random goal position
goal = GoalSprite(position=(random.random() * width, random.random() * height))

# drone is the ownship we are controlling
drone = DroneSprite()
drone_group = pygame.sprite.RenderPlain(drone)
goal_group = pygame.sprite.RenderPlain(goal)


time_step = -1  # this is the time step displayed at the top right corner.
simulate = True

while simulate:
    # while simulating, you can press esc to exit the pygame window
    # the process will terminate after hitting the boundary or the goal
    time_step += 1

    current_state = get_state(drone, goal)

    # specify the desired heading angle here, based on the current state.
    # action = policy(current_state)
    # drone.desired_direction = action

    # this desired heading angle is chosen to be the heading pointing directly to the goal position.
    direction = math.atan2(goal.position[1] - drone.position[1], goal.position[0] - drone.position[0])
    drone.desired_direction = -math.degrees(direction) - 90

    # use key board to exit the pygame window
    for event in pygame.event.get():
        if not hasattr(event, 'key'):
            continue
        down = event.type == KEYDOWN
        if event.key == K_ESCAPE:
            sys.exit(0)

    deltat = clock.tick(tick)
    screen.fill((255, 255, 255))

    # check if the ownship flies out of the map
    if not 0 < drone.position[0] < width or not 0 < drone.position[1] < height:
        drone.cumulative_reward += -100
        simulate = False
        print('You hit the wall :(')
        print('Total Reward: ', drone.cumulative_reward)

    # check if the ownship reaches the goal state.
    if dist(drone, goal) < drone.radius + goal.radius:
        # the ownship reaches the goal position
        collide_goal = True

        drone.cumulative_reward += 500
        simulate = False
        print('You reach the goal!')
        print('Total Reward: ', drone.cumulative_reward)

    # update the drone, goal
    drone_group.update(deltat)
    goal_group.update()

    # draw the aircraft and the goal
    drone_group.draw(screen)
    goal_group.draw(screen)

    # display time steps, number of times hitting wall, goals reached, the cum reward.
    time_display(time_step)
    reward_display(drone.cumulative_reward)

    pygame.display.flip()

    drone.cumulative_reward += -1
