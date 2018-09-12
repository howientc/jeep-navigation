# jeep-navigation


## Problem:

 You are implementing the navigation unit of an autonomous search-and-rescue drone jeep. It knows how to navigate to the site of a "distress beacon" but it doesn't know how to navigate to an "extraction point".

 An "extraction point" is defined as a point in space that is at the same height, or higher, than all of its surrounding points. Consider the world to be a 2-dimensional grid of heights - just like a topographical map.

 This jeep is outfitted with a laser rangefinder that can determine the heights of all points that neighbor the jeep. The jeep can then move in any of 8 directions (cardinal + diagonal).

 Your module, given a starting point, must navigate to and return its current location for extraction.

## API:

 Your module consists of a single method,

    navigateToExtractionPoint(start) -> (extraction point)

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


## Discussion

## Algorithm
### Real-world analog
Imagine you're the jeep. You've got a piece of graph paper (a grid of cells) in your hand to draw the topology map as you go. You've also got 
surveying tools which let you determine the height of the cell you are on as well as the coordinates of cells one
unit in any direction, north, south, east or west. Given this, we can thus scan like the radar or sonar would.

To begin, your parachute drops us at the start coordinates.

You look at your map to see if the cell satisfies the rules for being an extraction point (initially map is empty, so it's not). Our rule is that all adjacent cells
must be known, and the cell is the highest or tied for the highest with its adjacent cells.
You then scan where you are and the cells around it. Scanning is a pain. First, there is a time cost in unpacking (+repacking) and
callibrating the equipment, and then each point measured has a cost. Since you are keeping track of what you've
already scanned in your map, you only scan cells that you haven't previously scanned. You then add the heights for these new cells
to your map.

Now you look at your map. Is the current cell an extraction point? If not, then what about the other cells that we've scanned? Because
your map is getting filled in more and more, it's possible that some of those cells are now fully surrounded by known cells, so
you can check if any of them are extraction points. Are there any other candidates to check? Yes! It turns out that *any* cell adjacent to 
a newly scanned cell might now be surrounded. So, if you find any extraction points, you'd be done.

If not, then you need to figure out where to move to next, applying some sort of strategy. One thing you know is that you always want
to be moving up. You look at our neighboring cells. If there is a single highest value, then move towards it. If there is a tie for
the highest, you need to use a tiebreak to figure out which way to move. Maybe you can just pick a direction at random.

So how much should you move?

#### Naive move 1 strategy
A naive strategy is to move one unit in the direction (diagonal would be moving both x and y). While this is conceptually simple, it would mean lots of
unpacking/callibrating/repacking of the equipment.

#### Move N strategy (N=3)
A more efficient strategy would be to move 3 units in the direction instead of just one. That way, you could potentially be scanning a full
9 cells each time. Because of how you check for extraction points: not just scanned cells but also those adjacent to them, you won't miss
anything by doing this. That is, except if you moved on a diagonal. Imagine this is the real topology, where 

    0 0 0 | 0 0 0
    0 0 0 | 0 2 0
    0 0 4 | 3 0 0
    ------+------
    0 0 9 | 5 0 0
    0 1 0 | 0 0 0
    0 0 0 | 0 0 0
    
Say you start in the lower left, where the height 1 is. Your scan would be of the lower left quadrant. The scan finds the 9 cell in the 
corner and points you tomove up and right, so you'd move three cells over to the cell of height 2 in the upper right quadrant. But 
then 3 cell would point you back to the lower left where you just came from.

#### Move N cardinal, 1 ordinal variant (N = 3)
One solution to avoid this is to only move 1 cell (x,y) if moving on a diagonal. In this case, we'd move from 1 to 9, and we'd see
that 9 is an extraction point. The drawback, of course, is like in the naive strategy, we'd do a lot more unpacking/callibration than 
we'd like. Given that half of the adjacent cells are corners, you'd be moving on a diagonal a lot. 

You could at least say that if an edge and a corner are tied for highest, prefer moving towards the edge. This would help some.

#### Smart oridinal strategy
When the scan shows a corner cell is the highest, you'll determine a path that gets you to the cell (3,3) away by also visiting the
cells (0,3) away and (3,0) away. In other words. In our example, we might move up, right, and then down, ending in the lower right
quadrant. To determine this path, you'd look at the map and see if you've already been to those cells, and if so, skip them.

Like always, after you scan, you'd check to see if you determined an extraction point, and if so stop. However, now, you'll wait until
you've visited all three cells on your "diagonal path" before determining where to go next. This determination can be done either
by just picking the direction based on the diagonal cell (even if we're not currently there), or using the maximum height of all
newly scanned 3x3 areas for guidance (which, as always, is guaranteed to contain our highest known cell).

#### Advanced Heuristics
As it turns out, real-world topology isn't a bunch of random points. It's likely made up of slopes which end in peaks before going
down the other side. Suppose we're hiking and climbing a peak, we'd walk until we hit a ridge line, and then walk up that ridge line until we
hit a spot higher than its surroundings. This would either be the main peak, or an "extraction point". This works for us because
we're constantly aware of slope changes.

How can we apply this to our jeep's navigation? Mathematically thinking of the terrain as a 3D function, extraction points are cells where the slope is either flat or changes
sign in both the x and y directions. For simplicity, we can think of Slope = (Sx,Sy) where x and y are the cartesian coordinates of the
cell with the highest point. For example, if the direction is pointing up, then Slope=(0,1). If direction is to go bottom-right, Slope=(1,-1).

So let's imagine you are the jeep again. You scan your start square to get direction D0. Then you'll move N cells in that direction (It's hard
to know an exact value for N because it depends on the smoothness of the terrain. Smoother values do better with higher Ns).
You then scan again to get direction D1, and check if either the either x or y, has reversed sign with respect to D1. This implies that we've crossed over a ridge line. We can also check to
see if the point is lower than the previous one. Normally, we'd expect it to be higher, but if it's not, it also means we've crossed a ridge.

So if you've determined you've crossed a ridge, it's a simple question of doing a binary search, continually going back to the midpoint between
the current cell and the previous one to see if slope changed. If it did, then search again in that half, if not, search the other half. This
will get you to a ridge line.

Once at a ridge line, you switch to the smart diagonal strategy to follow the ridge up to the peak.

It *is* possible that this heuristic could miss an inflection point of the value of N is too large. For these edge-cases, we might introduce
a rule to limit total distance from the start we are willing to travel before heading back with smaller N values

 
## Coding conventions
* Using PEP-8 coding convention
   * The problem refers to a method named: <code>navigateToExtractionPoint</code>. Because the problem was
   language-neutral, a camelCase name was used. I will assume that I can rename the method to use PEP-8 naming
* non-public class members/functions must be prefixed with _
* Use standard decorators when appropriate (e.g. @staticmethod, @classmethod, @property...)
* Generator function names must begin with iter_
* Variables holding function pointers should be prefixed with func_
* All classes should have __slots__ defined for each member variable in them
   * This helps catch accidental bugs to to typos in declaring members
   * It also is an internal optimization
* All abstract base classes must inherit from ABC and decorate abstract methods/fields...




## Geometry
I have written an immutable Point class for this exercize, but in a real production environment,
we should use an established library, such as [sympy](https://docs.sympy.org/latest/modules/geometry/index.html "SymPy Docs")

### Coordinate system
Points use a 2D cartesian coordinate system so that:
* North is +Y, South is -Y
* East is +X, West is -X
Furthermore, heights are the Z-axis, with increasing Z being increasing height

#### Directions
* Cardinal directions are North (0,1), South (0,-1), East (1,0), West (-1,0)
* Ordinal directions are the diagonal ones: NE (1,1), SE (1, -1), SW (-1, -1), NW (-1, 1)

#### Issues with arrays 
For the most part, we don't need to care that arrays have rows and columns vs x and y coordonates.
The only time this is an issue is for humans to produce test data where the rows of the array actually
are negatively corresponding to y values.

## Future Directions
Incorporate cost of moving, both laterally and vertically

Plot path taken and map using mathplotlib.pyplot
docker container example
travis.yml