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
red = (200, 0, 0)
green = (0, 200, 0)

# size of the airspace
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
gameIcon = pygame.image.load('images/intruder.png')
pygame.display.set_icon(gameIcon)
pygame.display.set_caption('Aircraft Guidance Simulator', 'Spine Runtime')

intruder_size = 10  # number of intruder aircraft
RADIUS = 16  # safe radius for aircraft: above this number will be considered conflict
no_frame = 1  # one action can last how many frames or time steps?
tick = 30  # update no more than 30 frames in one second
min_dist = 128  # newly generated intruder shouldn't be too close to the ownship
np.set_printoptions(precision=2)


# display the time step at top right corner
def time_display(count):
    font = pygame.font.SysFont("comicsansms", 25)
    text = font.render("time step: " + str(count), True, black)
    screen.blit(text, (5, 0))


# display how many times the ownship flies out of map at top right corner
def collision_wall(count):
    font = pygame.font.SysFont("comicsansms", 25)
    text = font.render("Collision with wall: " + str(count), True, black)
    screen.blit(text, (5, 30))


# display how many conflicts there are at top right corner
def collision_intruder(count):
    font = pygame.font.SysFont("comicsansms", 25)
    text = font.render("Conflict with intruder: " + str(count), True, red)
    screen.blit(text, (5, 60))


# display how many goals reached at top right corner
def collision_goal(count):
    font = pygame.font.SysFont("comicsansms", 25)
    text = font.render("Goal: " + str(count), True, green)
    screen.blit(text, (5, 90))


# the aircraft object
class DroneSprite(pygame.sprite.Sprite):
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load('images/drone.png')
        self.rect = self.src_image.get_rect()
        self.image = self.src_image  # initial position
        self.position = position
        self.speed = 2  # speed of the ownship is 2 pixel per time step
        self.direction = 0
        self.rad = 0
        # velocity (v_x, v_y) can be decided from the speed scalar and orientation
        vx = -self.speed * math.sin(self.rad)
        vy = -self.speed * math.cos(self.rad)
        self.velocity = (vx, vy)
        # this aircraft will be safe if other aircraft are outside this radius
        self.radius = RADIUS
        # the heading angle will be updated according to this delta_direction.
        self.delta_direction = 0
        # use keyboard to control left or right
        self.k_right = 0
        self.k_left = 0

        # number of collisions, out of maps, reached goals
        self.collision_intruder = 0
        self.collision_wall = 0
        self.collision_goal = 0

    def update(self, deltat):
        # decide the new heading angle according to the action: self.delta_direction
        self.delta_direction = self.k_right + self.k_left
        self.direction += self.delta_direction
        self.direction %= 360
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


# the intruder aircraft sprite
class PadSprite(pygame.sprite.Sprite):
    def __init__(self, position, speed, direction):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load('images/intruder.png')
        self.image = self.src_image
        self.rect = self.src_image.get_rect()
        self.position = position
        self.speed = speed
        self.direction = direction
        self.rad = self.direction * math.pi / 180
        vx = -self.speed * math.sin(self.rad)
        vy = -self.speed * math.cos(self.rad)
        self.velocity = (vx, vy)
        self.radius = RADIUS

    def update(self):
        x, y = self.position
        x += self.velocity[0]
        y += self.velocity[1]
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
# pads is the list contains all the intruder aircraft sprite
# own is the ownship we are controlling
# goal is the goal sprite
def get_state(pads, own, goal):
    state_list = []
    for i in range(intruder_size):
        state_list.append(pads[i].position[0])
        state_list.append(pads[i].position[1])
        state_list.append(pads[i].velocity[0])
        state_list.append(pads[i].velocity[1])
    for i in range(1):
        state_list.append(own.position[0])
        state_list.append(own.position[1])
        state_list.append(own.velocity[0])
        state_list.append(own.velocity[1])
        state_list.append(own.direction)
    state_list.append(goal.position[0])
    state_list.append(goal.position[1])

    return np.array(state_list)


# distance between two sprites
def dist(a, b):
    dx = a.position[0] - b.position[0]
    dy = a.position[1] - b.position[1]
    return math.sqrt(dx * dx + dy * dy)


# reset the intruder aircraft position so that the intruder aircraft stays out of the safe distance
# from the ownship
# this usually happens when it's the beginning of the episode, when generating all the aircraft
def reset_intruder(intruder):
    # while the intruder is too near to the ownship, keep changing its position
    while dist(drone, intruder) < min_dist:
        intruder.position = (random.random() * width,
                             random.random() * height)
    intruder.speed = random.random() + 1
    intruder.direction = random.random() * 360
    intruder.rad = intruder.direction * math.pi / 180
    vx = -intruder.speed * math.sin(intruder.rad)
    vy = -intruder.speed * math.cos(intruder.rad)
    intruder.velocity = (vx, vy)


# generate a goal position
goal = GoalSprite((random.random() * (width - 200) + 100,
                   random.random() * (height - 200) + 100))

# pads is a list containts all the intruder aircraft
pads = []
for _ in range(intruder_size):
    # generate position, speed, direction of new intruder aircraft.
    pads.append(PadSprite((random.random() * width,
                           random.random() * height),
                          random.random() + 1,
                          random.random() * 360))

rect = screen.get_rect()  # screen center position

# drone is the ownship we are controlling
drone = DroneSprite(rect.center)
drone_group = pygame.sprite.RenderPlain(drone)
pad_group = pygame.sprite.RenderPlain(*pads)
goal_group = pygame.sprite.RenderPlain(goal)

import time
time_list = []  # used to track running time of the algorithm

time_step = -1  # this is the time step displayed at the top right corner.
simulate = True

while simulate:
    time_step += 1

    current_state = get_state(pads, drone, goal)
    current_time = int(round(time.time() * 1000))  # time before the algorithm

    # there can plug in some algorithms, input is current_state, output is action
    # action = algorithm(current_state)
    # drone.delta_direction = action
    # drone.speed = action

    time_after = int(round(time.time() * 1000))  # time after the algortihm
    time_list.append(time_after - current_time)

    # use key board left and right to control the ownship
    for event in pygame.event.get():
        if not hasattr(event, 'key'):
            continue
        down = event.type == KEYDOWN
        if event.key == K_RIGHT:
            drone.k_right = down * -4
        elif event.key == K_LEFT:
            drone.k_left = down * 4
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
            collide_wall = True
            drone.collision_wall += 1
            drone.position = (random.random() * 300 + 400,
                              random.random() * 200 + 300)
            drone.direction = random.random() * 360

        # check if there is conflicts with other intruder aircraft
        for intruder in pad_group:
            x = intruder.position[0]
            y = intruder.position[1]
            if pygame.sprite.collide_circle(drone, intruder):
                # there is conflict between the ownship and the current intruder
                collide_intruder = True
                drone.collision_intruder += 1
                # reset the position of current intruder
                reset_intruder(intruder)
            elif x > width - 4 or x < 4 or y > height - 4 or y < 4:
                # no conflict with the current intruder
                intruder.position = drone.position
                reset_intruder(intruder)

        # check if the ownship reaches the goal state.
        if pygame.sprite.collide_circle(drone, goal):
            # the ownship reaches the goal position
            collide_goal = True
            drone.collision_goal += 1
            # reset the position of all the intruder aircraft
            for intruder in pad_group:
                reset_intruder(intruder)
            # generate a new goal for the aircraft
            goal.position = (random.random() * (width - 200) + 100,
                             random.random() * (height - 200) + 100)

        # update the drone, intruder aircraft, goal
        drone_group.update(deltat)
        pad_group.update()
        goal_group.update()

        # draw the aircraft and the goal
        pad_group.draw(screen)
        drone_group.draw(screen)
        goal_group.draw(screen)

        time_display(time_step)
        collision_wall(drone.collision_wall)
        collision_intruder(drone.collision_intruder - intruder_size)
        collision_goal(drone.collision_goal)

        pygame.display.flip()
