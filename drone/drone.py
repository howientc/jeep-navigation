import logging
from geometry.point import Point3D


class Drone(object):
    __slots__ = ['_coords', '_topology_sensors', '_navigator']

    def __init__(self, navigator, topology_sensors):
        """
        :param navigator:
        :param topology_sensors:
        """
        self._coords = Point3D(0, 0, 0)
        self._topology_sensors = topology_sensors
        self._navigator = navigator

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
        logging.info("Drone moved to " + repr(point))

    def navigate_to_extraction_point(self, start_point):
        logging.info("Start point is " + repr(start_point))
        self._coords = Point3D(start_point.x, start_point.y, 0)  # set start position without calling move_to
        for point3d in self._navigator.iter_points_to_destination(start_point=start_point,
                                                                  topology_sensors=self._topology_sensors):
            self.move_to(point3d)
