from topology.topology_map import TopologyMap
from geometry.point2d import Point2D
from random import randint
import math


def make_topology_map_from_seed_points_xyz(seeds_xyz, lower_left, upper_right, style='cone'):
    """
    Creates a TopologyMap from seed points. The seed points are local or global maximums, and then
    surrounding points are lower and lower with distance. 'cone' style has peaks shaped like cones,
    'pyramid' style shapes them like 4 sided pyramids. Note that where peaks would collide, the valleys
    are not smoothed. It is possible to have more "extraction points" (summits or flat areas) than given
    in the seeds due to the way the peaks collide

    :param seeds_xyz: e.g. [(15,6,69), (21,11,52), (3, 4, 34)]
    :param lower_left: Lower left corner of map
    :param upper_right: Upper left corner of map
    :param style: 'cone' or 'pyramid' which determines curve shape
    :return: TopologyMap the created map
    """
    tm = TopologyMap()

    def distance(x1, y1, x2, y2):
        # linear distance between (x1,y1) and (x2,y2)
        return math.hypot(x2 - x1, y2 - y1)

    def linear_distance(x, y, pt):
        # return z value in a cone pattern from pt
        return round(pt[2] - distance(x, y, pt[0], pt[1]))

    def max_orthogonal_distance(x, y, pt):
        # return z value in a pyramid pattern from pt
        return round(pt[2] - max(abs(pt[0] - x), abs(pt[1] - y)))

    if style == 'cone':
        z_func = linear_distance
    elif style == 'pyramid':
        z_func = max_orthogonal_distance
    else:
        raise Exception('Unknown Style:' + style)

    # Go through all points. Pick the closest seed to the point, and calculate its z value and insert it
    for y in range(lower_left.y, upper_right.y + 1):
        for x in range(lower_left.x, upper_right.x + 1):
            pt = min(seeds_xyz, key=lambda p: distance(x, y, p[0], p[1]))  # closest point
            z = z_func(x, y, pt)  # apply style to get z
            tm.set_z(Point2D(x, y), z)

    return tm


def random_xyz(number_of_seeds, lower_left, upper_right, max_z):
    """
    Creates a list of unique (x,y,z) tuples
    :param number_of_seeds:
    :param lower_left:
    :param upper_right:
    :param max_z:
    :return:
    """
    # Sanity check. We can't get more seeds than what's available in the bounds
    assert number_of_seeds <= (upper_right.x - lower_left.x + 1) * (upper_right.y - lower_left.y + 1)

    found = {}
    while len(found) < number_of_seeds:
        pt = Point2D(randint(lower_left.x, upper_right.x), randint(lower_left.y, upper_right.y))
        if pt not in found:
            found[pt] = randint(1, max_z)
    return [(pt.x, pt.y, z) for pt, z in found.items()]


def generate_random_topology(number_of_seeds=5, lower_left=Point2D(0, 0), upper_right=Point2D(20, 20), max_z=None):
    """
    Generates a topology to test with. It is possible that the resulting topology could have more "extraction points"
    (peaks or flat areas) than the number of seeds because of the way the generated peaks collide.
    :param number_of_seeds: How many high points
    :param lower_left: lower-left point
    :param upper_right: upper-right point
    :param max_z: Maximum z value to generate
    :return: generated topology map
    """
    if not max_z:
        biggest_axis = max(upper_right.x - lower_left.x, upper_right.y - lower_left.y)
        max_z = biggest_axis // 2  # Just need a rule here. how about max height is half width?

    seeds = random_xyz(number_of_seeds, lower_left, upper_right, max_z)
    return make_topology_map_from_seed_points_xyz(seeds, lower_left, upper_right, 'cone')
