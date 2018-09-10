from operator import itemgetter


class TopologyMap(object):
    """
    A map of the world as the drone sees it. Basically, it keeps track of all of the areas where it's
    already been. This helps us avoid rescanning areas that we've already scanned. Currently this
    map is regenerated every time the drone is used. In the future, we can persist and then it can
    be used by any drone on a mission to the area. We could also persist the extraction points that
    have been discovered. That way we can have a rule that routes drones to the closest extraction
    point if it's within a certain threshold. That threshold could be determined by seeing if we have enough
    power to drive to the point.
    """
    __slots__ = ['_known_z', '_all_cells', '_adjacent_cells']

    def __init__(self):
        self._known_z = dict()  # keeps track of points already tracked to reduce cost of firing laser
        # for convenience, let's store off a list of offsets from 0, 0 to use in adjacent calculations
        self._adjacent_cells = [(x, y) for y in range(-1, 2) for x in range(-1, 2) if x != 0 or y != 0]
        self._all_cells = [(x, y) for y in range(-1, 2) for x in range(-1, 2)]

    def get_z(self, point):
        return self._known_z.get(point)

    def set_z(self, point, height):
        self._known_z[point] = height

    def walk_points(self, point, cells):
        for (x, y) in cells:
            pt = point.translate(x, y)
            z = self._known_z.get(pt)
            yield x, y, z, pt

    def walk_adjacent_points(self, point, radius=1):
        """
        Walk all adjacent cells (excludes center)
        :param radius:
        :param point: center point
        :return: generator yielding x, y, z, pt
        """
        return self.walk_points(point, adjacent_cells_in_radius(radius))

    def walk_all_points(self, point, radius=1):
        """
        Walk all adjacent cells (includes center)
        :param radius:
        :param point: center point
        :return: generator yielding x, y, z, pt
        """
        return self.walk_points(point, cells_in_radius(radius))

    def count_unknown_points_at_and_adjacent_to_point(self, point, radius=1):
        """
        :param radius:
        :param point:
        :return:
        """
        return sum(z is None for _x, _y, z, _pt in self.walk_all_points(point, radius))

    def is_highest_of_known_adjacent(self, point, radius=1):
        """
        See if the point is equal or higher than all points adjacent to it on the condition
        that all of the adjacent points have already been scanned
        :param radius:
        :param point:
        :return: True if the point is highest (or tied), False if not, or not all of the adjacent
        points are known
        """
        center_z = self._known_z.get(point)
        if not center_z:
            return False

        for x, y, z, pt in self.walk_adjacent_points(point, radius):
            if not z or z > center_z:
                return False
        return True

    def get_highest_adjacent_points_as_directions(self, point, radius=1):
        """
        :param radius:
        :param point:
        :return:
        """
        # Figure out the max height by walking adjacent points and maxing on the z value
        highest_adjacent = max(z for (_x, _y, z, _pt) in self.walk_adjacent_points(point, radius))

        # Now get the highest adjacent offsets as (x,y) tuples
        candidates = [(x, y) for (x, y, z, _pt) in self.walk_adjacent_points(point) if
                      z == highest_adjacent]  # array of tuples x,y
        return candidates


def cells_in_radius(radius=1):
    size = range(-radius, radius + 1)
    return ((x, y) for y in size for x in size)


def adjacent_cells_in_radius(radius=1):
    return ((x, y) for (x, y) in cells_in_radius(radius) if x != 0 or y != 0)
