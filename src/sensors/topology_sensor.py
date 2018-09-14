from abc import ABC, abstractmethod


class TopologySensor(ABC):
    __slots__ = ['_radius', '_scan_point_cost', '_power_on_cost', '_power_on_count', '_scan_point_count', "_total_cost"]
    """
    Base class for topology sensors. They read the values of the terrain around them
    """

    def __init__(self, radius=1, power_on_cost=0, scan_point_cost=0):
        """
        :param radius:
        :param power_on_cost:
        :param scan_point_cost:
        """
        self._radius = radius
        self._power_on_cost = power_on_cost
        self._scan_point_cost = scan_point_cost

        self._power_on_count = 0  # how many times sensor is turned on
        self._scan_point_count = 0  # how many time scans of individual cells are done
        self._total_cost = 0

    @property
    def power_on_cost(self):
        return self._power_on_cost

    @property
    def radius(self):
        return self._radius

    def increment_power_on_count(self):
        self._power_on_count += 1

    def increment_scan_point_count(self):
        self._scan_point_count += 1

    def estimate_cost_to_scan(self, adjacent_points):
        """
        The default implmentation is to calculate the cost of turning on the sensor + the
        cost to scan each adjacent_point. This assumes all adjacent points are equally costly to scan.
        :param adjacent_points:
        :return:
        """
        if not adjacent_points:
            return 0

        return self._power_on_cost + self._scan_point_cost * len(adjacent_points)

    def turn_on(self):
        """
        this turns on the hardware. Subclass overrides should also call this super method
        :return:
        """
        self._power_on_count += 1
        self._total_cost += self._power_on_cost

    def turn_off(self):
        """
        this turns off the hardware
        :return:
        """
        pass

    @abstractmethod
    def scan_points(self, offsets, home_point):
        """
        Scan the points desired
        :param offsets: A list of (x,y) tuples to scan
        :param home_point: the physical point at 0,0
        :return: a list of of tuples (x,y,z, point) corresponding to the values of points that were read. A sensor
        is free to return MORE that what was asked for. If so, this list will be larger than the offsets list. The
        caller can then use these additional points in its calculations
        """