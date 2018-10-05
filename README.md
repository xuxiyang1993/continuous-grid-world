# Continuous-Grid-World

A simulator to test algorithms that can guide the fixed wing aircraft to a random generated destination.

`simulator.py` is the code where there is a randomly generated goal at the beginning of each episode.

And you can use keyboard left and right arrow keys to control the aircraft in this simulator.
It will be amazing if your agent can beat you!

## MDP Formulation

### State: 
The state include the position, velocity, heading angle, and the goal position of the ownship (ownship is the yellow aircraft we can control):

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

where v is fixed speed (2 pixel/s), and the time step (delta t) is assumed to be 1 second. Here we assume at next state s', the aircraft doesn't reach the goal state (so that the goal position don't need to be updated).

### Reward:

-1 at each time step

+500 at goal state

-100 if the aircraft flies out of map (map is of size 500 * 500 (pixel))

### Terminal State:

When the ownship reaches the goal position (the distance between the goal and ownship is less than 32 pixel, the ownship is regarded as reaching the goal), the MDP will terminate with a big positive reward.

When the ownship flies out of the map (the position (x,y) is not in the range (0,500)), the MDP will also terminate.

## Submission

You should submit a policy function which is a mapping from the state space to the action space.

## Test Your Policy

You should define a policy function which the input is `current_state` from line 132. And the output of this policy function is the action corresponding to current state. Call the policy function at line 137 like following:

`action = policy(current_state)`

After uncommenting line 137,138 and running the code, it's time to grab a coffee and see how your agent performs!

Note you can use whatever programming language to solve this problem. If you use other language, you need to store the policy in a file and read the file using Python to get the action at each time step.

## Requirements

* python 3.6
* random
* numpy
* pygame


## Getting Started

Make sure that you have the above requirements taken care of, then download all the files.

### Note
If you want to solve more challenging problem, `simulator_with_intruder.py` is the code for you, where many intruder aircraft will be in this simulator.

If you have any questions or comments, or you think there are bugs in this code, don't hesitate to send me an email! I am looking for ways to make this code even more computationally efficient. Or you can also stop by my office at 2362 Howe Hall (Seat 2362-19).

Email: xuxiyang@iastate.edu
