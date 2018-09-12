from topology.topology_map import TopologyMap
from geometry.point2d import Point2D
from collections import OrderedDict
from random import randint


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


def make_topology_map_from_seed_points_xyz(list_of_xyz, lower_left, upper_right):
    """
    Creates a TopologyMap from seed points, such that the seed points are inserted, and then each
    of their surrounding points is one lower. Then process these surrounding points in the same way.
    However, if a point has already been determined, then don't change its height.
    :param list_of_xyz: e.g. [(15,6,69), (21,11,52), (3, 4, 34)]
    :param lower_left: Lower left corner of map
    :param upper_right: Upper left corner of map
    :return: TopologyMap the created map
    """
    tm = TopologyMap()

    # calculate our map's extents
    x_range = range(lower_left.x, upper_right.x + 1)
    y_range = range(lower_left.y, upper_right.y + 1)

    def process_seeds(seeds):
        """
        Performs breadth-first recursion to process points according to the rules described above
        :param seeds: a dictionary containing the seed points
        """
        children = OrderedDict()  # keep track of children to process. Keep order for repeatability
        for pt, z in seeds.items():
            tm.set_z(pt, z)  # add the point
            # We care about unknown adjacent points in our range
            for _x, _y, known, apt in tm.iter_adjacent_points(pt):
                if not known and apt.x in x_range and apt.y in y_range:
                    children[apt] = z - 1  # use any value since we're using the OrderedDict as a set
        if children:
            process_seeds(children)

    # populate a dictionary with the initial seeds
    seeds = {Point2D(x, y): z for x, y, z in list_of_xyz} # Note order here not guaranteed

    process_seeds(seeds)

    return tm


def generate_random_topology(number_of_seeds=5, lower_left=Point2D(0, 0), upper_right=Point2D(20, 20), max_z=None):
    if not max_z:
        biggest_axis = max(upper_right.x - lower_left.x, upper_right.y - lower_left.y)
        max_z = biggest_axis // 2  # Just need a rule here. how about max height is half width?

    seeds = random_xyz(number_of_seeds, lower_left, upper_right, max_z)
    return make_topology_map_from_seed_points_xyz(seeds, lower_left, upper_right)
