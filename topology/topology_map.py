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
    __slots__ = ['_cached_z', '_adjacent_cells']

    def __init__(self):
        self._cached_z = dict()  # keeps track of points already tracked to reduce cost of firing laser
        # for convenience, let's store off a list of offsets from 0, 0 to use in adjacent calculations
        self._adjacent_cells = [(x, y) for y in range(-1, 2) for x in range(-1, 2) if x != 0 or y != 0]

    def get_z(self, point):
        return self._cached_z.get(point)

    def set_z(self, point, height):
        self._cached_z[point] = height

    def populate_sensor_buffer_from_cache(self, sensor_buffer, point):
        for x, y, _, pt in sensor_buffer.walk_points(point):
            sensor_buffer.set_z(x, y, self.get_z(pt))

    def is_highest_of_cached_adjacent(self, point):
        """
        See if the point is equal or higher than all points adjacent to it on the condition
        that all of the adjacent points have already been scanned
        :param point:
        :return: True if the point is highest (or tied), False if not, or not all of the adjacent
        points are known
        """
        center_z = self._cached_z.get(point)
        if not center_z:
            return False
        for (x, y) in self._adjacent_cells:
            pt = point.translate(x, y)
            z = self._cached_z.get(pt)
            if not z or z > center_z:
                return False
        return True
