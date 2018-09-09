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


## Coding conventions
* Using PEP-8 coding convention
   * The problem refers to a method named: <code>navigateToExtractionPoint</code>. Because the problem was
   language-neutral, a camelCase name was used. I will assume that I can rename the method to use PEP-8 naming
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

Need to take care in code:
* that increasing array rows = decreasing Y (and vice versa)
* indexing into a 2D array is array[y][x], whereas points are (x,y)

## Future Directions
Incorporate cost of moving, both laterally and vertically

Plot path taken and map using mathplotlib.pyplot
docker container example
travis.yml