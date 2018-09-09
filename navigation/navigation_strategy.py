from abc import ABC, abstractmethod
from operator import itemgetter


class NavigationStrategy(ABC):

    def __init__(self):
        self.topology_map = None  # will be injected later by factory

    def set_topology_map(self, topology_map):
        self.topology_map = topology_map

    def populate_adjacent_from_cache(self, adjacent, point):
        for y in range(len(adjacent)):
            for x in range(len(adjacent[0])):
                pt = point.translate(x - 1, y - 1)
                adjacent[y][x] = self.get_known_height(pt)

    def _determine_next_point(self, point, sensor):
        """
        :param point:
        :return: tuple(Point, bool) Point is where to go next, bool is whether this point is an extraction point
        """
        sensor.get_adjacent_topology(point)

        field_width = self.topology_sensor.field_width
        #
        center = self.topology_sensor.center_of_field
        # biggest = adjacent[center[1]][center[0]]  # initially set to home square
        # offset_x_y = center

        # now find biggest values
        # first convert the 2d array into 1d array of (x,y, height)
        flattened = [(x, y, adjacent[y][x]) for y in range(field_width) for x in range(field_width)]
        biggest = max(flattened, key=itemgetter(2))[2]  # the height is item at index 2
        candidates = [(a[0], a[1]) for a in flattened if a[2] == biggest]  # array of tuples x,y

        # It is possible that values of all highest cells are already in cache (certainly true for center)
        # see if any are winners

        for offset in highest:

        # normalize the value so that the center is at 0,0
        return offset_x_y[0] - center[0], offset_x_y[1] - center[1]
    return tuple of point, done

    @abstractmethod
    def navigate_to_extraction_point(self, start_point, topology_sensor, move_callback=None):
        """

        :param topology_sensor:
        :param start_point:
        :param move_callback:
        """
