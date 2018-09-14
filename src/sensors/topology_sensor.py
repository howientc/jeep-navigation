# -*- coding: utf-8 -*-
"""
Topology Sensors are used to scan points in a radius. They have a cost associated with turning them on, as well as
a cost for each point scanned. Some sensors might have a high cost to turn on, but a negligable or cheap cost for
each point then scanned. Sensors keep track of their usage
"""
from abc import ABC, abstractmethod


class TopologySensor(ABC):
    """
    Absract base class for all TopologySensors. They read the values of the terrain around them
    In the future, if we have other sensor types, we can pull up
    most of this class into an abstract Sensor class.
    """
    __slots__ = ['_radius', '_scan_point_cost', '_power_on_cost', '_power_on_count', '_scan_point_count', "_total_cost"]

    def __init__(self, radius=1, power_on_cost=0, scan_point_cost=0):
        """
        :param radius: The sensor's scan has this radius
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
        """
        Returns much it costs to power on the sensor
        :return: a number
        """
        return self._power_on_cost

    @property
    def radius(self):
        """
        This sensor's scan radius
        :return:
        """
        return self._radius

    def increment_power_on_count(self):
        """
        Keeps track of total power-ups. CCall this when the scanner is powered on
        :return:
        """
        self._power_on_count += 1

    def increment_scan_point_count(self):
        """
        Adds one to the total of individual points scanned.
        :return:
        """
        self._scan_point_count += 1

    def estimate_cost_to_scan(self, adjacent_points):
        """
        Calculates the cost of turning on the sensor + the
        cost to scan each adjacent_point. This assumes all adjacent points are equally costly to scan.
        :param adjacent_points: Not used here, but subclasses might have different costs to scan different offsets
        :return:
        """
        if not adjacent_points:
            return 0

        return self._power_on_cost + self._scan_point_cost * len(adjacent_points)

    def turn_on(self):
        """
        Turns on the hardware. Subclass overrides should also call this super method
        :return:
        """
        self._power_on_count += 1
        self._total_cost += self._power_on_cost

    def turn_off(self):
        """
        Turns off the hardware
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