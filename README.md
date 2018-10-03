# Continuous-Grid-World

A simulator to test algorithms that can guide the fixed wing aircraft to a random generated destination.

`simulator.py` is the code where there is a randomly generated goal at the beginning of each episode.

And you can use keyboard left and right arrow keys to control the aircraft in this simulator.
It will be amazing if your agent can beat you!

## MDP Formulation

### State: 
The state include the position of the ownship, the velocity of the ownship, the heading angle of the ownship, and goal position of the ownship:

(position_x, position_y, velocity_x, velocity_y, heading angle, goal_pos_x, goal_pos_y) 

The state is a vector in the following form:

<img src="https://github.com/xuxiyang1993/continuous-grid-world/blob/master/images/state.png" width="160" height="35" />

### Action:
At each time step, the aircraft can choose to turn left for 2 deg, go straight, or to turn right for 2 deg.

More precisely, the action space is {+2deg/s, 0deg/s, -2deg/s} where positive means turning left, 
with the assumption that each time step is 1 second.

### State Transition:

Suppose the current state is S, current action is a, then the next state 

<img src="https://github.com/xuxiyang1993/continuous-grid-world/blob/master/images/sp.png" width="190" height="35" />

will be

<img src="https://github.com/xuxiyang1993/continuous-grid-world/blob/master/images/transition.png" width="140" height="255" />

where v is fixed speed (2 pixel/s), and the time step (delta t) is assumed to be 1 second.

### Reward:

-1 at each time step

+500 at goal state

-100 if the aircraft flies out of map (map is of size 500 * 500 (pixel))

## Submission

You should submit a policy function which is a mapping from a state to the action.

## Requirements

* python 3.6
* random
* numpy
* pygame


## Getting Started

Make sure that you have the above requirements taken care of, then download all the files.

### Note
If you want to solve more challenging problem, `simulator_with_intruder.py` is the code for you,
where many intruder aircraft will be in this simulator.


If you have any questions or comments, don't hesitate to send me an email! I am looking for ways to make this code even more computationally efficient. 

Email: xuxiyang@iastate.edu
