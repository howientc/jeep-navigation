from geometry.point2d import Point2D

OUT_OF_BOUNDS = float("-inf")
NO_BOUNDS = float("inf")


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

    __slots__ = ['_known_z', '_lower_left', '_upper_right', '_lower_left_bounds', '_upper_right_bounds']

    def __init__(self, lower_left_bounds=None, upper_right_bounds=None):
        self._known_z = dict()  # keeps track of points already tracked to reduce cost of firing laser

        self._lower_left_bounds = lower_left_bounds
        self._upper_right_bounds = upper_right_bounds

        # for convenience, let's store off a list of offsets from 0, 0 to use in adjacent calculations
        self._lower_left = None
        self._upper_right = None

    def populate_from_matrix(self, topology_matrix, origin=Point2D(0, 0), set_bounds=True):
        """
        Populates the map from a matrix. Mostly useful in testing, but someday we might want to preload one or more
        matrices of data into our maps
        :param topology_matrix:
        :param origin:
        :param set_bounds: True (default) if we should limit the map's bounds to this array's dimensions
        :return:
        """
        width = len(topology_matrix[0])  # the width of the first row is the width of all rows
        height = len(topology_matrix)
        origin = origin
        for row in range(height):
            for col in range(width):
                # reversing rows to make y value
                point = Point2D(origin.x + col, origin.y + height - row - 1)
                self.set_z(point, topology_matrix[row][col])

        if set_bounds:
            self._lower_left_bounds = origin
            self._upper_right_bounds = Point2D(origin.x + width -1, origin.y + height -1)

    def get_z(self, point):
        """
        Gets z value (height) at a point. If out of bounds, returns OUT_OF_BOUNDS
        :param point:
        :return:
        """
        # Handle cases where the point lies off the topology (out of bounds)
        if self._lower_left_bounds and (point.x < self._lower_left_bounds.x or point.y < self._lower_left_bounds.y):
            return OUT_OF_BOUNDS

        if self._upper_right_bounds and (point.x > self._upper_right_bounds.x or point.y > self._upper_right_bounds.y):
            return OUT_OF_BOUNDS

        return self._known_z.get(point)

    def set_z(self, point, height):
        """
        Sets z value at a point to the passed height
        :param point:
        :param height:
        :return:
        """
        self._known_z[point] = height

        # adjust our current bounds
        if not self._upper_right:
            self._upper_right = self._lower_left = point
        else:
            self._upper_right = Point2D(max(self._upper_right.x, point.x), max(self._upper_right.y, point.y))
            self._lower_left = Point2D(min(self._lower_left.x, point.x), min(self._lower_left.y, point.y))

    @property
    def width_and_height(self):
        """
        Gets the width and height of the rectangular bounds containing all known points. Since a point takes up
        one square unit of space, make sure to add 1 to the both dimensions
        :return:
        """
        return 1 + self._upper_right.x - self._lower_left.x, 1+ self._upper_right.y - self._lower_left.y

    @property
    def boundary_points(self):
        """
        Gets the lower left and upper right points of the rectangular bounds containing all known points
        :return: tuplo(lower left corner, upper right corner)
        """
        return self._lower_left, self._upper_right

    def iter_all_points_xyz(self):
        """
        Generates all of the points in the map as x,y,z in no specific order
        :return:
        """
        for pt, z in self._known_z.items():
            yield pt.x, pt.y, z

    def iter_cells_around_point(self, point, cells):
        """
        Generates adjacent points for each offset in cells
        :param point: The reference point
        :param cells: A list containing (x,y) offsets from the point
        :return: generator yielding x,y,z,pt
        """
        for (x, y) in cells:
            pt = point.translate(x, y)
            z = self._known_z.get(pt)
            yield x, y, z, pt

    def iter_adjacent_points(self, point, radius=1):
        """
        Walks all adjacent cells (excludes center)
        :param radius:
        :param point: center point
        :return: generator yielding x, y, z, pt
        """
        return self.iter_cells_around_point(point, iter_adjacent_cells_in_radius(radius))

    def iter_self_and_adjacent_points(self, point, radius=1):
        """
        Walks all adjacent cells (includes center)
        :param radius:
        :param point: center point
        :return: generator yielding x, y, z, pt
        """
        return self.iter_cells_around_point(point, iter_cells_in_radius(radius))

    def count_unknown_points_at_and_adjacent_to_point(self, point, radius=1):
        """
        Counts how many unknown cells are around the point for the given radius
        :param radius:
        :param point:
        :return:
        """
        return sum(z is None for _x, _y, z, _pt in self.iter_self_and_adjacent_points(point, radius))

    def is_highest_of_known_adjacent(self, point, radius=1):
        """
        Sees if the point is equal or higher than all points adjacent to it on the condition
        that all of the adjacent points have already been scanned
        :param radius:
        :param point:
        :return: True if the point is highest (or tied), False if not, or not all of the adjacent
        points are known
        """
        center_z = self._known_z.get(point)
        if not center_z:
            return False

        for x, y, z, pt in self.iter_adjacent_points(point, radius):
            if not z or z > center_z:
                return False
        return True

    def get_highest_adjacent_points_as_directions(self, point, radius=1):
        """
        Figures out the list of highest points around a given point
        :param radius:
        :param point:
        :return: list of points
        """
        # Figure out the max height by walking adjacent points and maxing on the z value
        highest_adjacent = max(z for (_x, _y, z, _pt) in self.iter_adjacent_points(point, radius))

        # Now get the highest adjacent offsets as (x,y) tuples
        candidates = [(x, y) for (x, y, z, _pt) in self.iter_adjacent_points(point) if
                      z == highest_adjacent]  # array of tuples x,y
        return candidates


def iter_cells_in_radius(radius=1):
    """
    Convenience method to walk through all cells in a given radius
    :param radius:
    :return: yields x,y offsets from the center
    """
    size = range(-radius, radius + 1)
    return ((x, y) for y in size for x in size)


def iter_adjacent_cells_in_radius(radius=1):
    """
    Convenience method to walk through all cells in a given radius, excluding the center
    :param radius:
    :return: yields x,y offsets from the center
    """
    return ((x, y) for (x, y) in iter_cells_in_radius(radius) if x != 0 or y != 0)
