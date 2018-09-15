# jeep-navigation


## Problem (as stated by customer)

 You are implementing the navigation unit of an autonomous search-and-rescue drone jeep. It knows how to navigate to the site of a "distress beacon" but it doesn't know how to navigate to an "extraction point".

 An "extraction point" is defined as a point in space that is at the same height, or higher, than all of its surrounding points. Consider the world to be a 2-dimensional grid of heights - just like a topographical map.

 This jeep is outfitted with a laser rangefinder that can determine the heights of all points that neighbor the jeep. The jeep can then move in any of 8 directions (cardinal + diagonal).

 Your module, given a starting point, must navigate to and return its current location for extraction.

### API:

 Your module consists of a single method,

    navigateToExtractionPoint(start) -> (extraction point)
    
**NOTE: The above (with PEP-8 style naming) can be found in <code>examples/basic_usage_example.py</code>** 
    
    

 In production, your module will call the laser component to sample nearby locations. You will need to define the API surface that the laser should implement, as well as prepare a stub implementation that we can use for testing, using fake data.

 Test topology:

    [
        [1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 1, 1, 2, 4],
        [1, 2, 2, 2, 1, 2, 2],
        [1, 2, 3, 2, 1, 1, 1],
        [1, 1, 2, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 2],
    ]

## (part 2) In essence, the question is:

    What is the "production-ready" version of this code snippet?

What this means to us: the version of this code that is optimized for (in no specific order)

* Testability
* Readability & understandability – specifically by junior staff
* Optionality – what if we want to swap the laser out with a radar?
* Performance – minimize the number of times the laser height sampler is called

##Project Specificiation
### Definitions
* Cardinal (orthogonal) directions are North (0,1), South (0,-1), East (1,0), West (-1,0)
* Ordinal (diagonal) directions are the diagonal ones: NE (1,1), SE (1, -1), SW (-1, -1), NW (-1, 1)

## Discussion
Imagine you're the jeep. You've got a piece of graph paper (a grid of cells) in your hand to draw the topology map as you go. You've also got 
surveying tools which let you determine the height of the cell you are on as well as the coordinates of cells one
unit in any direction, north, south, east or west. Given this, we can thus scan like the radar or sonar would.

To begin, your parachute drops you on a start point

You look at your map to see if the cell satisfies the rules for being an extraction point (initially map is empty, so it's not). Our rule is that all adjacent cells
must be known, and the cell is the highest or tied for the highest with its adjacent cells.
You then scan where you are and the cells around it. Scanning is a pain. First, there is a time cost in unpacking (+repacking) and
callibrating the surveying equipment, and then each point measured has a cost. Since you are keeping track of what you've
already scanned in your map, you only scan cells that you haven't previously scanned. You then add the heights for these new cells
to your map.

Now you look at your map. Is the current cell an extraction point? If not, then what about the other cells that we've scanned? Because
your map is getting filled in more and more, it's possible that some of those cells are now fully surrounded by known cells, so
you can check if any of them are extraction points. Are there any other candidates to check? Yes! It turns out that the scan can
fill in the map enough so that a cell nearby is now surrounded with known points, so be sure to check in a bigger radius on your map to see if
that's the case. If we find any extraction point, you're done

If not, then you need to figure out where to move to next, applying some sort of strategy. One thing you know is that you always want
to be moving up. You look at our neighboring cells. If there is a single highest value, then move towards it. If there is a tie for
the highest, you need to use a tiebreak to figure out which way to move. Maybe you can just pick a direction at random.

Scanning a lot is a pain, so you decide to move three cells at a time towards the highest point, that way you cover more ground instead of rescanning points
you already know. Unfortunately, for diagonal movement, if you move 3, you'd be missing some values, so to play it safe, you move
just one on the diagonal. You prefer, then, if there's a tie between an orthogonal direction and a cardinal one, you go cardinal.

But even that can be a pain, so you see if you can be smart about it. So initially you scan a point far away, see if it's higher. If
it isn't you back up to the midpoint back to the highest point and try again. As time goes by, you go a little less far away, until
you arrive at small steps like your previous strategy. You might move more, but you'll likely scan less

### Observations
Ordinal moves are much more likely than cardinal in real-world data. This is because slopes
are much larger than cells.

### MoveStrategies
#### Naive move 1 strategy
A naive strategy is to move one unit in the direction (diagonal would be moving both x and y). While this is conceptually simple, it would mean lots of
unpacking/callibrating/repacking of the equipment.

#### Move N strategy (N=3)
A more efficient strategy would be to move 3 units in the direction instead of just one. That way, you could potentially be scanning a full
9 cells each time. Because of how you check for extraction points: not just scanned cells but also those adjacent to them, you won't miss
anything by doing this. That is, except if you moved on a diagonal. Imagine this is the real topology, where 

    0 0 0 | 0 0 0
    0 b 0 | 0 2 0
    0 8 9 | 6 0 0
    ------+------
    0 0 7 | 10 0 0
    0 1 9 | 0 a 0
    0 0 0 | 0 0 0
    
Say you start in the lower left, where the height 1 is. Your scan would be of the lower left quadrant. The scan finds the 9 cell in the 
corner and points you tomove up and right, so you'd move three cells over to the cell of height 2 in the upper right quadrant. But 
then 3 cell would point you back to the lower left where you just came from.

#### Move N cardinal, 1 ordinal variant (N = 3)
One solution to avoid this is to only move 1 cell (x,y) if moving on a diagonal. In this case, we'd move from 1 to 9, and we'd see
that 9 is an extraction point. The drawback, of course, is like in the naive strategy, we'd do a lot more unpacking/callibration than 
we'd like. Given that half of the adjacent cells are corners, you'd be moving on a diagonal a lot. 

You could at least say that if an edge and a corner are tied for highest, prefer moving towards the edge. This would help some.

Optimizing diagonal movement is tricky because we could miss an extraction point if we don't check all possibilities
surrounding the point. We could always visit cardinal points, but that might be more costly

#### Binary Search
The binary search as described above seems like a good idea. Of course it is dependent on the terrain, and could be tuned
accordingly 

#### Other move strategies
There are a lot of possibilities to tinker and optimize. Therefore, we should consider having the
possibility to benchmark different strategies


## Algorithm
### Definitions:
* Navigator decides on the path to take and tells the drone to move
* TopologicalMap is the map the Navigator uses to keep track of what it knows
* Destination is a rule like "Is Extracton Point".
* MoveStrategy is, as described above. It's used to determine where to go next
* TopologySensor measures heights of points around it
* Drone has sensors and a navigator. It eventually could have the ablilty to move and broadcast telemtry 

### Navigation Algorithm:

The Navigator is configured with a Destination and and MoveStrategy and an empty TopologicalMap
Drone is built with one or more TopologicalSensors and a Navigator.
Initiaze Navigator current point to start point

While not Destination found
- Navigator chooses a sensor from list given by drone and scans at the current point
- Navigator adds newly discovered points to its TopologicalMap
- Navigator sees if the point or any near points on Topological map are Destinations.
- Navigator applies its MoveStrategy to get the next point
- Navigator informs drone to move
- (Drone could physically move and broadcast telemetry)

### Discussion
* This algorithm is very flexible, in that it lets us navigate to things other than extraction points, just
by changing our Destination.
* We can experiment with any number of MoveStrategies. We can benchmark to see which are the best for different terrains
* It also lets us use different sensors, and pick the appropriate one for the job.
* It is not tied to the radius of our sensors or radius of what points we need to know to be at a destination
* We could persist TopologicalMaps and reuse them, or share them with other Drones

## Code

### Project structure:
`examples`  Code which demonstrates the usage of the library. In ths case, there s a run_example.py which uses
matplotlib to make an interactive test demo.

`src` The library source

`tests` unit tests which test the source


### Dependencies
To install dependencies on ubuntu:
<code>./install.sh</code>

They are needed for the interactive example

See <code>install.sh</code> for dependencies.
The interactive example code requires a bunch of stuff:
python3, pip, mathplotlib, python-tk, PyDisptacher
The basic library doesn't

Note that I've made a .Dockerfile to run the example code, but issues with getting Tcl/x11 working right make it
not worth the hassle at ths time.

### Usage

    drone = DroneFactory.make_drone(move_strategy, topology_sensors, destination)
    drone.navigate_to_destination_point(start_point):

*move_strategy*:  one of the enums in move_strategy.py, such as MoveStrategy.BINARY_SEARCH
*topology_sensors*: A list of one or more TopologySensors(). For testing see SimulatedTopologySensor
*destination*: A Destination, by default ExtractionPoint()
*start_point* is Point2D x,y

See <code>examples/basic_usage.py</code> for how to call the API

A full-blown interactive simulator is in <code>examples/interactive_simulator_example.py</code>

### Simulator
Because we cannot do much in the way of system testing, I've provided simulation classes to help:
TopologyFactory, to generate simulated topologies
SimulatedTopologySensor which reads from a simulated topology

### Interactive Example
The interactive example provides a friendly way to test different strategies. One prolem with coding problems
like this is that even if our unit tests pass, it's possible we're misunderstanding the concept, thus coding to incorrect
assumptions. The example lets you see visually how the drone moves.


### Coding conventions
* Using PEP-8 coding convention
* non-public class members/functions must be prefixed with _
* Use standard decorators when appropriate (e.g. @staticmethod, @classmethod, @property...)
* Generator function names should begin with iter_
* Variables holding function pointers should be prefixed with func_
* Consider using __slots__ for each member variable in them
   * This helps catch accidental bugs to to typos in declaring members
   * It also is an internal optimization
* All abstract base classes must inherit from ABC and decorate abstract methods/fields...


### Geometry
I have written an immutable Point2D and Point3D classes for this exercize, but in a real production environment,
we should use an established library, such as [sympy](https://docs.sympy.org/latest/modules/geometry/index.html "SymPy Docs")

#### Coordinate system
Points use a 2D cartesian coordinate system so that:
* North is +Y, South is -Y
* East is +X, West is -X
Furthermore, heights are the Z-axis, with increasing Z being increasing height

#### Issues with arrays 
For the most part, we don't need to care that arrays have rows and columns vs x and y coordonates.
The only time this is an issue is for humans to produce test data where the rows of the array actually
are negatively corresponding to y values.

#TODOs
* Add benchmarking code which repeatedly generates maps, and tallies up scan costs for different algorithms 
   * also generate maps with different densities.
   * If we have any maps that are like the real ones, use them too
* Add test runner
* Integrate test runner into CI system (e.g. have a travis.yml)
* Improve installation (docker would be nice, but a pain with X11)
* Get test coverage to 100% for algorithmic code
