import logging
from geometry.point2d import Point2D


class Drone(object):
    __slots__ = ['_coords', '_navigation_strategy', '_topology_sensor']

    def __init__(self, navigation_strategy, topology_sensor):
        """
        :param navigation_strategy:
        :param topology_sensor:
        """
        self._coords = Point2D(0, 0)
        self._navigation_strategy = navigation_strategy
        self._topology_sensor = topology_sensor

    def move_to(self, point):
        """
        Move the drone to the given 2d point.
        In the future, we could:
        - Use a Point3D in case we need to care about moving vertically because
        of increased power use due to overcoming gravity
        - Keep track of distance covered
        :param point: 2D point
        :return:
        """
        self._coords = point
        logging.info("Drone moved to ", point)

    def navigate_to_extraction_point(self, start_point):
        logging.info("Start point is ", start_point)
        self._coords = start_point  # set start position without calling move_to
        return self._navigation_strategy.navigate_to_extraction_point(start_point=start_point,
                                                                      topology_sensor=self._topology_sensor,
                                                                      move_callback=lambda pt: self.move_to(pt))
