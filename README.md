# Continuous-Grid-World

A simulator to test algorithms that can guide the fixed wing aircraft to a random generated destination.

`simulator.py` is the code where this is a randomly generated goal at the beginning of each episode.

`simulator_with_intruder.py` is the code where intruder aircraft will be in this simulator.

## MDP Formulation

### State: 
(position_x, position_y, velocity_x, velocity_y, heading angel, goal_pos_x, goal_pos_y) -> (x,y,v_x,v_y,\phi,g_x,g_y)

### Action:
At each time step, the aircraft can choose to turn left for 2 deg, go straight, or to turn right for 2 deg.

### State Transition:


### Reward:
-1 at each time step

+500 at goal state

-100 if the aircraft flies out of map (map is of size 500 * 500 (pixel))

## Requirements

* python 3.6
* random
* numpy
* pygame


## Getting Started

Make sure that you have the above requirements taken care of, then download all the files.




If you have any questions or comments, don't hesitate to send me an email! I am looking for ways to make this code even more computationally efficient. 

Email: xuxiyang@iastate.edu
